#!/usr/bin/env python
# coding: utf-8


import asyncio

from smtplibaio import SMTP


async def send(from_addr, to_addrs, subject="Ellis", msg="", **kwargs):
    """
    Sends an e-mail to the provided address.

    :param from_addr: E-mail address of the sender.
    :type from_addr: str
    :param to_addrs: E-mail address(es) of the receiver(s).
    :type to_addrs: list or str
    :param msg: Message to be sent.
    :type msg: str
    """
    async with SMTP() as client:
        msg = "Subject: {0}\n\n{1}".format(subject, msg)

        if kwargs:
            # To append kwargs to the given message, we first
            # transform it into a more human friendly string:
            values = "\n".join(["{0}: {1}".format(k, v)
                                for k, v
                                in kwargs.items()])

            # Actually append caught values to the message:
            msg = ("{0}\n\nThe following variables have been caught:"
                   "\n{1}".format(msg, values))

        try:
            await client.sendmail(from_addr, to_addrs, msg)
        except:
            # FIXME: print a friendly message to stdout.
            raise
