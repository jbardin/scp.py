# Changelog

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

