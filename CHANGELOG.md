# Changelog

## 0.14.3 (2022-02-15)

- Add type hints

## 0.14.2 (2021-12-15)

- Don't fail if the remote path is a PurePath not a Path

## 0.14.1 (2021-09-10)

- Don't fail if 'pathlib' doesn't import (Python 2)
- Accept 'unicode' objects as paths (Python 2)

## 0.14.0 (2021-09-07)

- Accept iterables other than list and tuple in `get()` and `put()`
- Accept `pathlib.Path` objects

## 0.13.6 (2021-07-09)

- Fix put when the source directory has a trailing slash. It will now work similarly to rsync, copying the contents of the directory.

## 0.13.5 (2021-06-28)

- Fix extra space sent in SSH command-line for `get()`, causing issues on some servers

## 0.13.4 (2021-06-08)

- Add `scp_command` attribute, allowing changing the command run on the server (for example to `sudo scp`)

## 0.13.3 (2020-10-26)

- Fix hanging when underlying paramiko channel is closed

## 0.13.2 (2019-03-19)

- Fix AssertionError in recursive get() when `_rename` is set and server sends a POPD at the end (`_depth > 0`)

## 0.13.1 (2019-03-11)

- Guard against some malformed messages from the server

## 0.13.0 (2018-11-12)

- Remove all introspection logic for `progress` callback introduced in 0.12
- `progress` callback only accept 3 arguments again
- Introduce `progress4` parameter which accepts the peername as 4th argument

## 0.12.1 (2018-10-12)

- Fix `progress` callback failing when it is an instance or class method

## 0.12.0 (2018-10-09)

- Fix README.rst for PyPI
- Add possibility of getting the peer IP and port from the `progress` callback
- Make `putfo()` work with file-like objects that don't provide `getvalue()`

## 0.11.0 (2018-05-05)

- Add `putfo()` method, allowing one to upload a file-like object
- Add top-level `get()` and `put()` functions for convenience
- Increase default socket time from 5 to 10 seconds

## 0.10.2 (2015-05-15)

- Fixes using the SCPClient multiple times

## 0.10.0 (2015-05-07)

- SCPClient can be used as a context manager
- Added `close()`

## 0.9.0 (2015-02-04)

- Add changelog
- Finish up py3k and unicode support
- Unicode should work on OSX, Windows and Linux
- Some tests have been added

