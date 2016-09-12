#!/usr/bin/env python
# coding: utf-8

import asyncio
import ipaddress

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
        cmd = "ipset add -exist {} {} timeout {}" \
              .format(setname, ip, timeout)

        return await self.start(cmd)

    async def list(self, setname=None):
        """
        """
        cmd = "ipset list"

        if setname is not None:
            cmd = "{} {}".format(cmd, setname)

        return await self.start(cmd)

    def chose_blacklist(self, ip):
        """
        Given an IP address, figure out the ipset we have to use.

        If the address is an IPv4, we have to use `self.blacklist4`.
        If the address is an IPv6, we have to use `self.blacklist6`.

        Raises ipaddress.AddressValueError if the address is neither
        an IPv4 nor an IPv6.
        """
        blacklist = 'rig_blacklist{0}'

        try:
            address = ipaddress.ip_address(ip)
        except AddressValueError:
            raise
        else:
            if address.version is 6:
                # We don't ban private IPv6:
                if address.is_private:
                    msg = "We don't ban private addresses ({0} given)." \
                          .format(address)
                    raise ipaddress.AddressValueError(msg)
                else:
                    # Do we have an embedded IPv4 ?
                    if address.ipv4_mapped is not None:
                        address = address.ipv4_mapped
                    elif address.sixtofour is not None:
                        address = address.sixtofour

        blacklist = blacklist.format(address.version)

        return (address, blacklist)

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


async def ban(ip, timeout=0):
    """
    """
    ipset = Ipset()
    ipset_name, address = ipset.chose_blacklist(ip)
    print("Adding {0} to {1}".format(address, ipset_name))

    return await ipset.add(ipset_name, address, timeout)
