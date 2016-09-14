#!/usr/bin/env python
# coding: utf-8

import asyncio

from asyncio.subprocess import PIPE


class ShellCommander(object):
    """
    """
    def __init__(self):
        """
        """
        pass

    async def start(self, cmd):
        """
        """
        proc = await asyncio.create_subprocess_shell(cmd, stderr=PIPE)
        stdout_data, stderr_data = await proc.communicate()

        if stdout_data:
            print(stdout_data)

        if stderr_data:
            self.handle_error(stderr_data)

        # Shell commands are supposed to return 0 on success.
        # When an error occurs, the cmd is supposed to print a message
        # on stderr. This message is caught and passed to
        # the `handle_error` method.
        return True if proc.returncode is 0 else False

    def handle_error(self, err):
        """
        """
        msg = ("You have to overwrite this method and provide your own"
               " implementation in your subclass.")
        raise NotImplementedError(msg)
