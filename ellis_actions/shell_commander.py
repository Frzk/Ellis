#!/usr/bin/env python
# coding: utf-8

import asyncio
import shlex

from asyncio.subprocess import PIPE


class ShellCommander(object):
    """
    """
    def __init__(self):
        """
        """
        pass

    async def start(self, cmd, cmd_args=[], input_bytes=None):
        """
        """
        # Make sure the provided arguments are safe:
        args = __class__.escape_args(*cmd_args)

        # Build full command:
        command = f"{cmd} {args}"

        # And then launch the command:
        proc = await asyncio.create_subprocess_shell(command, stdin=PIPE,
                                                     stdout=PIPE, stderr=PIPE)

        stdout_data, stderr_data = await proc.communicate(input_bytes)

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

    @classmethod
    def escape_args(cls, *args):
        """
        Transforms the given list of unescaped arguments into a
        suitable, shell-escaped str that is ready to be append
        to the command.

        Removes whitespaces and shell metacharacters for each argument
        in given args.
        """
        escaped_args = [shlex.quote(str(arg)) for arg in args]

        return " ".join(escaped_args)
