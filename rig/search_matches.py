#!/usr/bin/env python
# coding: utf-8


import asyncio


class SearchMatches():
    """
    """
    def __init__(self, rule, msg):
        """
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
        """
        coro = self._loop.run_in_executor(None, self._search, regex)
        match = await coro

        return match

    def _search(self, regex):
        """
        """
        return regex.search(self.msg)

