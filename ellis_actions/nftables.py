#!/usr/bin/env python
# coding: utf-8

import ipaddress

from .shell_commander import ShellCommander


class NFTablesSetNotFound(Exception):
    pass


class NFTables(ShellCommander):
    """
    """
    CMD = 'nft'

    def __init__(self, tablename):
        """
        """
        super().__init__()

        self.tablename = tablename

    async def add(self, setname, ip, timeout):
        """
        Adds the given IP address to the specified set.

        If timeout is specified, the IP will stay in the set for the given
        duration. Else it will stay in the set during the set default timeout.

        timeout must be given in seconds.

        The resulting command looks like this:

        ``nft add element inet firewall ellis_blacklist4 { 192.0.2.10 timeout 30s }``

        """
        # We have to double-quote the '{' '}' at both ends for `format` to work.
        to_ban = "{{ {0} timeout {1}s }}".format(ip, timeout)

        args = ['add', 'element', 'inet', self.tablename, setname, to_ban]

        return await self.start(__class__.CMD, *args)

    def chose_blacklist(self, ip):
        """
        Given an IP address, figure out the set we have to use.

        If the address is an IPv4, we have to use *ellis_blacklist4*.
        If the address is an IPv6, we have to use *ellis_blacklist6*.

        Raises ipaddress.AddressValueError if the address is neither
        an IPv4 nor an IPv6.
        """
        blacklist = 'ellis_blacklist{0}'

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

        print("FIXME (raise a custom  Exception) - {}".format(msg))
        """
        if "Kernel error received: Operation not permitted" in msg:
            raise IpsetNoRights(msg)
        elif "The set with the given name does not exist" in msg:
            raise IpsetSetNotFound(msg)
        elif "Element cannot be added to the set: it's already added" in msg:
            raise IpsetAlreadyInSet(msg)
        else:
            raise IpsetError(msg)
        """


async def ban(ip, table='filter', timeout=600):
    """
    """
    nft = NFTables(table)
    address, set_name = nft.chose_blacklist(ip)
    print("Adding {0} to {1}:{2}".format(address, table, set_name))

    return await nft.add(set_name, address, timeout)
