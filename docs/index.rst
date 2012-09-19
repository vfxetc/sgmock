.. _index:

sgmock
======

This Python package is a mock `Shotgun <http://www.shotgunsoftware.com/>`_ server for use in unit testing, and a series of tools for building test fixtures. It emulates the experience of using `shotgun_api3 <https://github.com/shotgunsoftware/python-api>`_ with a Shotgun server near version 4.0. It is fairly incomplete, but is enough for testing the majority of our own tools which tend to focus heavily on consuming data from Shotgun instead of manipulating it.

This mockup does not perfectly emulate the Shotgun experience. In general, it makes the assumption that your usage of the Shotgun API is correct, and that you are testing your manipulation of the data that comes out of it. For example:

- schemas are not enforced (nor do they exist at all);
- there are no default values, and unspecified fields will not be retrievable later;
- entities do not require a `project`.

Also, the mockup starts with absolutely no entities. That includes things that you would normally have by default, e.g. pipeline steps.

If you ask the mockup to do something that it doesn't understand then we try to fail quickly and fail really hard. Usually with a :class:`ShotgunError` or :class:`NotImplementedError`.

Good luck, and happy testing!


..
    Contents
    ========


.. toctree::
   :maxdepth: 2

..
    Indices and tables
    ==================
    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

