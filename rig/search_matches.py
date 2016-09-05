#!/usr/bin/env python
# coding: utf-8


import asyncio


class SearchMatches():
    """
    An *asynchronous iterator* that allows us to check if a message (from
    journald) matches a Rule.

    See PEP-0492_ for further details about asynchronous iterators.

    .. _PEP-O492: https://www.python.org/dev/peps/pep-0492/#id62
    """
    def __init__(self, rule, msg):
        """
        Initializes a newly created SearchMatches object.

        The only noticeable thing here is that we use ``iter`` to get the
        Rule's filters as an iterable.
        """
        self.msg = msg
        self._regexes = iter(rule.filter)
        self._loop = asyncio.get_event_loop()

    async def __aiter__(self):
        """
        """
        return self

    async def __anext__(self):
        """
        """
        try:
            regex = next(self._regexes)
        except StopIteration:
            raise StopAsyncIteration
        else:
            match = await self.search(regex)

        return match

    async def search(self, regex):
        """
        Wraps the search for a match in an `executor`_ and awaits for it.

        .. _executor: https://docs.python.org/3/library/asyncio-eventloop.html#executor
        """
        coro = self._loop.run_in_executor(None, self._search, regex)
        match = await coro

        return match

    def _search(self, regex):
        """
        Actually searches for a match.
        
        Scans through self.msg looking for the first location where the given `regex object`_ produces a match.
        
        Returns a `match object`_ if the search is succesful or None otherwise.

        .. _regex object: https://docs.python.org/3/library/re.html#regular-expression-objets
        .. _match object: https://docs.python.org/3/library/re.html#match-objects
        """
        return regex.search(self.msg)

