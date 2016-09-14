#!/usr/bin/env python
# coding: utf-8

import ipaddress

from rig.shell_commander import ShellCommander


class IpsetError(Exception):
    pass


class IpsetNoRights(Exception):
    pass


class IpsetSetNotFound(Exception):
    pass


class IpsetAlreadyInSet(Exception):
    pass


class Ipset(ShellCommander):
    """
    """
    def __init__(self):
        """
        """
        super().__init__()

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
        except ipaddress.AddressValueError:
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
    address, ipset_name = ipset.chose_blacklist(ip)
    print("Adding {0} to {1}".format(address, ipset_name))

    return await ipset.add(ipset_name, address, timeout)
