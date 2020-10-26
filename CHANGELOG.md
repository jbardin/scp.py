# Changelog

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

