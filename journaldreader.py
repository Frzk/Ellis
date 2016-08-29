#!/usr/bin/env python
# coding: utf-8


from systemd import journal


class JournaldReader(journal.Reader):
    """
    A JournaldReader reads systemd journald entries.

    It implements the :func:`__enter__` and :func:`__exit__` special methods 
    so it can be used as a context manager (which is obviously recommended).
    """
    def __init__(self):
        """
        Initializes a newly created JournaldReader.

        Basically, this initialization only consists in setting the log level 
        to *LOG_INFO*.
        """
        super().__init__()

        self.log_level(journal.LOG_INFO)

    def __enter__(self):
        """
        Enters the runtime context related to the JournaldReader.

        Seeks to the last message of the log.

        Returns self

        .. seealso::
            For further details, be sure to read the official doc:
            https://docs.python.org/3/reference/datamodel.html#object.__enter__
        """
        self.seek_tail()
        self.get_previous()

        return self

    def __exit__(self, type, value, traceback):
        """
        Exits the runtime context related to the JournaldReader.

        .. seealso::
            For further details, be sure to read the official doc:
            https://docs.python.org/3/reference/datamodel.html#object.__exit__
        """
        self.close()
        # FIXME: we are supposed to return True or False here.

