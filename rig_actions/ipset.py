#!/usr/bin/env python
# coding: utf-8

import asyncio

from asyncio.subprocess import PIPE


class IpsetError(Exception):
    pass


class IpsetNoRights(Exception):
    pass


class IpsetSetNotFound(Exception):
    pass


class IpsetAlreadyInSet(Exception):
    pass


class Ipset(object):
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
        # This is what ipset does (see the manpages).
        #
        # When an error occurs, ipset is supposed to print a message on stderr.
        # This message is caught and transformed into an Exception
        # by our `handle_error` method.
        #
        # So basically, this function should either return True or raise
        # an Exception.
        #
        # However, we'd better be careful and still handle the hypothetic
        # case where ipset would not return 0 and would not print anything
        # to stderr. Hence the following construction:
        return True if proc.returncode is 0 else False

    async def add(self, setname, ip, timeout=0):
        """
        """
        cmd = ("ipset add -exist {} {} timeout {}"
               .format(setname, ip, timeout))

        return await self.start(cmd)

    async def list(self, setname=None):
        """
        """
        cmd = "ipset list"

        if setname is not None:
            cmd = "{} {}".format(cmd, setname)

        return await self.start(cmd)

    def handle_error(self, err):
        """
        """
        msg = err.decode()

        if "Kernel error received: Operation not permitted" in msg:
            raise IpsetNoRights(msg)
        elif "The set with the given name does not exist" in msg:
            raise IpsetSetNotFound(msg)
        elif "Element cannot be added to the set: it's already added" in msg:
            raise IpsetAlreadyInSet(msg)
        else:
            raise IpsetError(msg)


async def ban(ip, ipset_name=None, timeout=0):
    """
    """
    if ipset_name is None:
        ipset_name = "rig_blacklist"

    ipset = Ipset()
    print("Adding {0} to {1}".format(ip, ipset_name))

    return await ipset.add(ipset_name, ip, timeout)
