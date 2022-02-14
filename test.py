from __future__ import print_function

from io import BytesIO
import os
import paramiko
import random
import shutil
import sys
from scp import SCPClient, SCPException, put, get
import tempfile
import types
import unittest

try:
    import pathlib
except ImportError:
    pathlib = None


ssh_info = {
    'hostname': os.environ.get('SCPPY_HOSTNAME', '127.0.0.1'),
    'port': int(os.environ.get('SCPPY_PORT', 22)),
    'username': os.environ.get('SCPPY_USERNAME', None),
}


# Environment info
PY3 = sys.version_info >= (3,)
WINDOWS = os.name == 'nt'
MACOS = sys.platform == 'darwin'


if MACOS:
    import unicodedata

    def normalize_paths(names):
        """Ensures the test names are normalized (NFC).

        HFS (on Mac OS X) will normalize filenames if necessary.
        """
        normed = set()
        for n in names:
            if isinstance(n, bytes):
                n = n.decode('utf-8')

            normed.add(unicodedata.normalize('NFC', n).encode('utf-8'))
        return normed
else:
    normalize_paths = set


def unique_names():
    """Generates unique sequences of bytes.
    """
    characters = (b"abcdefghijklmnopqrstuvwxyz"
                  b"0123456789")
    characters = [characters[i:i + 1] for i in range(len(characters))]
    rng = random.Random()
    while True:
        letters = [rng.choice(characters) for i in range(10)]
        yield b''.join(letters)
unique_names = unique_names()


class TestDownload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Server connection
        cls.ssh = paramiko.SSHClient()
        cls.ssh.load_system_host_keys()
        cls.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        cls.ssh.connect(**ssh_info)

        # Makes some files on the server
        chan = cls.ssh.get_transport().open_session()
        chan.exec_command(
            b'if ! echo -ne "/tmp/r\\xC3\\xA9mi" | xargs test -d; then '
            # Directory
            b'echo -ne "/tmp/bien rang\\xC3\\xA9" | xargs -0 mkdir; '
            # Files
            b'echo -ne "'
            b'/tmp/r\\xC3\\xA9mi\\x00'
            b'/tmp/bien rang\\xC3\\xA9/file\\x00'
            b'/tmp/bien rang\\xC3\\xA9/b\\xC3\\xA8te\\x00'
            b'/tmp/p\\xE9t\\xE9'  # invalid UTF-8 here
            b'" | xargs -0 touch; '
            b'fi')
        assert chan.recv_exit_status() == 0

        print("Running tests on %s with %s" % (
              "Windows" if WINDOWS else
              "Mac OS X" if MACOS else
              "POSIX",
              "Python 3" if PY3 else "Python 2"))

    def download_test(self, filename, recursive, destination=None,
                      expected_win=[], expected_posix=[]):
        # Make a temporary directory
        temp = tempfile.mkdtemp(prefix='scp-py_test_')
        # Add some unicode in the path
        if WINDOWS:
            if isinstance(temp, bytes):
                temp = temp.decode(sys.getfilesystemencoding())
            temp_in = os.path.join(temp, u'cl\xE9')
        else:
            if not isinstance(temp, bytes):
                temp = temp.encode('utf-8')
            temp_in = os.path.join(temp, b'cl\xC3\xA9')
        previous = os.getcwd()
        os.mkdir(temp_in)
        os.chdir(temp_in)
        cb3 = lambda filename, size, sent: None
        try:
            with SCPClient(self.ssh.get_transport(), progress=cb3) as scp:
                scp.get(filename,
                        destination if destination is not None else u'.',
                        preserve_times=True, recursive=recursive)
            actual = []

            def listdir(path, fpath):
                for name in os.listdir(fpath):
                    fname = os.path.join(fpath, name)
                    actual.append(os.path.join(path, name))
                    if os.path.isdir(fname):
                        listdir(name, fname)
            listdir(u'' if WINDOWS else b'',
                    u'.' if WINDOWS else b'.')
            self.assertEqual(normalize_paths(actual),
                             set(expected_win if WINDOWS else expected_posix))
        finally:
            os.chdir(previous)
            shutil.rmtree(temp)

    def test_get_bytes(self):
        self.download_test(b'/tmp/r\xC3\xA9mi', False, b'target',
                           [u'target'], [b'target'])
        self.download_test(b'/tmp/r\xC3\xA9mi', False, u'target',
                           [u'target'], [b'target'])
        self.download_test(b'/tmp/r\xC3\xA9mi', False, None,
                           [u'r\xE9mi'], [b'r\xC3\xA9mi'])
        self.download_test([b'/tmp/bien rang\xC3\xA9/file',
                            b'/tmp/bien rang\xC3\xA9/b\xC3\xA8te'],
                           False, None,
                           [u'file', u'b\xE8te'], [b'file', b'b\xC3\xA8te'])

    def test_get_unicode(self):
        self.download_test(u'/tmp/r\xE9mi', False, b'target',
                           [u'target'], [b'target'])
        self.download_test(u'/tmp/r\xE9mi', False, u'target',
                           [u'target'], [b'target'])
        self.download_test(u'/tmp/r\xE9mi', False, None,
                           [u'r\xE9mi'], [b'r\xC3\xA9mi'])
        self.download_test([u'/tmp/bien rang\xE9/file',
                            u'/tmp/bien rang\xE9/b\xE8te'],
                           False, None,
                           [u'file', u'b\xE8te'], [b'file', b'b\xC3\xA8te'])

    def test_get_folder(self):
        self.download_test(b'/tmp/bien rang\xC3\xA9', True, None,
                           [u'bien rang\xE9', u'bien rang\xE9\\file',
                            u'bien rang\xE9\\b\xE8te'],
                           [b'bien rang\xC3\xA9', b'bien rang\xC3\xA9/file',
                            b'bien rang\xC3\xA9/b\xC3\xA8te'])
        self.download_test(b'/tmp/bien rang\xC3\xA9', True, b'target',
                           [u'target', u'target\\file',
                            u'target\\b\xE8te'],
                           [b'target', b'target/file',
                            b'target/b\xC3\xA8te'])

    def test_get_invalid_unicode(self):
        self.download_test(b'/tmp/p\xE9t\xE9', False, u'target',
                           [u'target'], [b'target'])
        if WINDOWS:
            with self.assertRaises(SCPException):
                self.download_test(b'/tmp/p\xE9t\xE9', False, None,
                                   [], [])
        elif MACOS:
            self.download_test(b'/tmp/p\xE9t\xE9', False, None,
                               [u'not windows'], [b'p%E9t%E9'])
        else:
            self.download_test(b'/tmp/p\xE9t\xE9', False, None,
                               [u'not windows'], [b'p\xE9t\xE9'])


class TestUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Server connection
        cls.ssh = paramiko.SSHClient()
        cls.ssh.load_system_host_keys()
        cls.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        cls.ssh.connect(**ssh_info)

        # Makes some files locally
        cls._temp = tempfile.mkdtemp(prefix='scp_py_test_')
        if isinstance(cls._temp, bytes):
            cls._temp = cls._temp.decode(sys.getfilesystemencoding())
        inner = os.path.join(cls._temp, u'cl\xE9')
        os.mkdir(inner)
        os.mkdir(os.path.join(inner, u'dossi\xE9'))
        os.mkdir(os.path.join(inner, u'dossi\xE9', u'bien rang\xE9'))
        open(os.path.join(inner, u'dossi\xE9', u'bien rang\xE9', u'test'),
             'w').close()
        open(os.path.join(inner, u'r\xE9mi'), 'w').close()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._temp)

    def upload_test(self, filenames, recursive, expected=[], fl=None):
        destination = b'/tmp/upp\xC3\xA9' + next(unique_names)
        chan = self.ssh.get_transport().open_session()
        chan.exec_command(b'mkdir ' + destination)
        assert chan.recv_exit_status() == 0
        previous = os.getcwd()
        cb4 = lambda filename, size, sent, peername: None
        try:
            os.chdir(self._temp)
            with SCPClient(self.ssh.get_transport(), progress4=cb4) as scp:
                if not fl:
                    scp.put(filenames, destination, recursive)
                else:
                    prefix = destination.decode(sys.getfilesystemencoding())
                    remote_path = '%s/%s' % (prefix, filenames)
                    scp.putfo(fl, remote_path)
                    fl.close()

            chan = self.ssh.get_transport().open_session()
            chan.exec_command(
                b'echo -ne "' +
                destination.decode('iso-8859-1')
                    .encode('ascii', 'backslashreplace') +
                b'" | xargs find')
            out_list = b''
            while True:
                data = chan.recv(1024)
                if not data:
                    break
                out_list += data
            prefix = len(destination) + 1
            out_list = [l[prefix:] for l in out_list.splitlines()
                        if len(l) > prefix]
            self.assertEqual(normalize_paths(out_list), set(expected))
        finally:
            os.chdir(previous)
            chan = self.ssh.get_transport().open_session()
            chan.exec_command(b'rm -Rf ' + destination)
            assert chan.recv_exit_status() == 0

    @unittest.skipIf(WINDOWS, "Use unicode paths on Windows")
    def test_put_bytes(self):
        self.upload_test(b'cl\xC3\xA9/r\xC3\xA9mi', False, [b'r\xC3\xA9mi'])
        self.upload_test(b'cl\xC3\xA9/dossi\xC3\xA9/bien rang\xC3\xA9/test',
                         False,
                         [b'test'])
        self.upload_test(b'cl\xC3\xA9/dossi\xC3\xA9', True,
                         [b'dossi\xC3\xA9',
                          b'dossi\xC3\xA9/bien rang\xC3\xA9',
                          b'dossi\xC3\xA9/bien rang\xC3\xA9/test'])
        # Again, with trailing slash
        self.upload_test(b'cl\xC3\xA9/dossi\xC3\xA9/', True,
                         [b'bien rang\xC3\xA9',
                          b'bien rang\xC3\xA9/test'])

    def test_put_unicode(self):
        self.upload_test(u'cl\xE9/r\xE9mi', False, [b'r\xC3\xA9mi'])
        self.upload_test(u'cl\xE9/dossi\xE9/bien rang\xE9/test', False,
                         [b'test'])
        self.upload_test(u'cl\xE9/dossi\xE9', True,
                         [b'dossi\xC3\xA9',
                          b'dossi\xC3\xA9/bien rang\xC3\xA9',
                          b'dossi\xC3\xA9/bien rang\xC3\xA9/test'])
        self.upload_test([u'cl\xE9/dossi\xE9/bien rang\xE9',
                          u'cl\xE9/r\xE9mi'], True,
                         [b'bien rang\xC3\xA9',
                          b'bien rang\xC3\xA9/test',
                          b'r\xC3\xA9mi'])
        g = (n for n in (u'cl\xE9/dossi\xE9/bien rang\xE9', u'cl\xE9/r\xE9mi'))
        assert isinstance(g, types.GeneratorType)
        self.upload_test(g, True,
                         [b'bien rang\xC3\xA9',
                          b'bien rang\xC3\xA9/test',
                          b'r\xC3\xA9mi'])
        self.upload_test([u'cl\xE9/dossi\xE9',
                          u'cl\xE9/r\xE9mi'], True,
                         [b'dossi\xC3\xA9',
                          b'dossi\xC3\xA9/bien rang\xC3\xA9',
                          b'dossi\xC3\xA9/bien rang\xC3\xA9/test',
                          b'r\xC3\xA9mi'])

    @unittest.skipUnless(pathlib, "pathlib not available")
    def test_pathlib(self):
        self.upload_test(pathlib.Path(u'cl\xE9/dossi\xE9'), True,
                         [b'dossi\xC3\xA9',
                          b'dossi\xC3\xA9/bien rang\xC3\xA9',
                          b'dossi\xC3\xA9/bien rang\xC3\xA9/test'])

    def test_putfo(self):
        fl = BytesIO()
        fl.write(b'r\xC3\xA9mi')
        fl.seek(0)
        self.upload_test(u'putfo-test', False, [b'putfo-test'], fl)


class TestUpAndDown(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Server connection
        cls.ssh = paramiko.SSHClient()
        cls.ssh.load_system_host_keys()
        cls.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        cls.ssh.connect(**ssh_info)

        # Makes some files locally
        cls._temp = tempfile.mkdtemp(prefix='scp_py_test_')
        if isinstance(cls._temp, bytes):
            cls._temp = cls._temp.decode(sys.getfilesystemencoding())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._temp)

    def test_up_and_down(self):
        '''send and receive files with the same client'''
        previous = os.getcwd()
        testfile = os.path.join(self._temp, 'testfile')
        testfile_sent = os.path.join(self._temp, 'testfile_sent')
        testfile_rcvd = os.path.join(self._temp, 'testfile_rcvd')
        try:
            os.chdir(self._temp)
            with open(testfile, 'w') as f:
                f.write("TESTING\n")
            put(self.ssh.get_transport(), testfile, testfile_sent)
            get(self.ssh.get_transport(), testfile_sent, testfile_rcvd)

            with open(testfile_rcvd) as f:
                self.assertEqual(f.read(), 'TESTING\n')
        finally:
            os.chdir(previous)


if __name__ == '__main__':
    unittest.main()
