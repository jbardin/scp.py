from __future__ import print_function

import os
import paramiko
import shutil
import sys
from scp import SCPClient, SCPException
import tempfile
import unittest


ssh_info = {
    'hostname': '127.0.0.1',
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


class TestSCP(unittest.TestCase):
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
        try:
            scp = SCPClient(self.ssh.get_transport())
            scp.get(filename, destination if destination is not None else u'.',
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

    def test_get_unicode(self):
        self.download_test(u'/tmp/r\xE9mi', False, b'target',
                           [u'target'], [b'target'])
        self.download_test(u'/tmp/r\xE9mi', False, u'target',
                           [u'target'], [b'target'])
        self.download_test(u'/tmp/r\xE9mi', False, None,
                           [u'r\xE9mi'], [b'r\xC3\xA9mi'])

    def test_get_folder(self):
        self.download_test(b'/tmp/bien rang\xC3\xA9', True, None,
                           [u'bien rang\xE9', u'bien rang\xE9\\file',
                            u'bien rang\xE9\\b\xE8te'],
                           [b'bien rang\xC3\xA9', b'bien rang\xC3\xA9/file',
                            b'bien rang\xC3\xA9/b\xC3\xA8te'])

    def test_invalid_unicode(self):
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


if __name__ == '__main__':
    unittest.main()
