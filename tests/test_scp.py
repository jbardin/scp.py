import paramiko
import scp
import os.path
import subprocess

import pytest


testdata = os.path.join(os.path.dirname(scp.__file__), 'testdata')

# paramiko client
pclient = paramiko.SSHClient()
pclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

sclient = None


def setup():
    pclient.connect("127.0.0.1")
    global sclient
    sclient = scp.SCPClient(pclient.get_transport())


def teardown():
    pclient.close()


def test_notfound():
    with pytest.raises(scp.SCPException):
        sclient.get("lwehfh39rho1p293ryo1829yo129hrl1i2hr")


def test_put_single(tmpdir):
    tmpdir = str(tmpdir)
    testfile = os.path.join(testdata, 'data')
    dest = os.path.join(tmpdir, 'data')
    sclient.put(testfile, dest)
    subprocess.check_call(["diff", testfile, dest])


def test_put_multiple(tmpdir):
    tmpdir = str(tmpdir)
    testfile1 = os.path.join(testdata, 'data')
    testfile2 = os.path.join(testdata, 'data2')
    destfile1 = os.path.join(tmpdir, 'data')
    destfile2 = os.path.join(tmpdir, 'data2')
    sclient.put([testfile1, testfile2], tmpdir)

    subprocess.check_call(["diff", testfile1, destfile1])
    subprocess.check_call(["diff", testfile2, destfile2])


def test_put_recurse(tmpdir):
    tmpdir = str(tmpdir)
    sclient.put(testdata, tmpdir, recursive=True)
    subprocess.check_call(['diff', '-r', testdata,
        os.path.join(tmpdir, 'testdata')])


def test_get_single(tmpdir):
    tmpdir = str(tmpdir)
    testfile = os.path.join(testdata, 'data')
    dest = os.path.join(tmpdir, 'data')
    sclient.get(testfile, dest)
    subprocess.check_call(["diff", testfile, dest])


def test_get_multiple(tmpdir):
    tmpdir = str(tmpdir)
    testfile1 = os.path.join(testdata, 'data')
    testfile2 = os.path.join(testdata, 'data2')
    destfile1 = os.path.join(tmpdir, 'data')
    destfile2 = os.path.join(tmpdir, 'data2')
    sclient.get([testfile1, testfile2], tmpdir)

    subprocess.check_call(["diff", testfile1, destfile1])
    subprocess.check_call(["diff", testfile2, destfile2])


def test_get_recurse(tmpdir):
    tmpdir = str(tmpdir)
    sclient.get(testdata, tmpdir, recursive=True)
    subprocess.check_call(['diff', '-r',
        testdata, os.path.join(tmpdir, 'testdata')])


def test_put_newline(tmpdir):
    'verify that a newline is escaped as \^J just like openssh scp'
    #TODO: investigate when scp really does create a file with \n in the name

    tmpdir = str(tmpdir)
    testfile = os.path.join(tmpdir, 'newline\nfile')
    with open(testfile, 'w') as f:
        f.write('has a newline')

    sclient.put(testfile, tmpdir)
    subprocess.check_call(['diff', testfile,
        os.path.join(tmpdir, 'newline\\^Jfile')])


def test_put_perm_denied(tmpdir):
    tmpdir = str(tmpdir)

    # pre-copy the data, and make a subdirectory read-only
    subprocess.check_call(['cp', '-a', testdata, tmpdir])
    subprocess.check_call(['chmod', '0444',
        os.path.join(tmpdir, 'testdata', 'dir1')])

    try:
        sclient.put(testdata, tmpdir, recursive=True)
        pytest.Fail('no exception')
    except scp.SCPException as e:
        assert 'permission denied' in e.message.strip().lower()


def test_get_perm_denied(tmpdir):
    tmpdir = str(tmpdir)

    # pre-copy the data, and make a subdirectory read-only
    subprocess.check_call(['cp', '-a', testdata, tmpdir])
    subprocess.check_call(['chmod', '0444',
        os.path.join(tmpdir, 'testdata', 'dir1')])

    try:
        sclient.get(tmpdir, '/tmp/foo', recursive=True)
        pytest.Fail('no exception')
    except scp.SCPException as e:
        assert 'permission denied' in e.message.strip().lower()
