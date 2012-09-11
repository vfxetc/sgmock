# sgmock

[![Test Status](https://secure.travis-ci.org/westernx/sgmock.png)](http://travis-ci.org/westernx/sgmock)

This Python package is a mock Shotgun server for use in unit testing. It is fairly incomplete, but is enough for testing the majority of our own tools which tend to focus heavily on consuming data from Shotgun instead of manipulating it.

This mockup does not perfectly emulate the Shotgun experience. In general, it makes the assumption that your usage of the Shotgun API is correct, and that you are testing your manipulation of the data that comes out of it. For example:

- schemas are not enforced (nor do they exist at all);
- there are no default values, and unspecified fields will not be retrievable later;
- entities do not require a `project`.

Also, the mockup starts with absolutely no entities. That includes things that you would normally have by default, e.g. pipeline steps.

If you ask the mockup to do something that it doesn't understand then we try to fail quickly and fail really hard. Usually with a NotImplementedError.

Good luck, and happy testing!