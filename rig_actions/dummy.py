#!/usr/bin/env python
# coding: utf-8

"""
Provides a bunch of useless functions that may help you test some code.
"""

import asyncio
import time

def blocking_wait(sec=5, **kwargs):
    """
    Does nothing for *sec* seconds and then prints out a message. 
    
    .. note:: This function **is** blocking.
    
    .. seealso:: :func:`wait`

    :param sec: Time to wait, in seconds.
    :param kwargs: Additional parameters.
    """
    time.sleep(sec)
    print("Done waiting for {0} sec.".format(sec))

async def wait(sec=5, **kwargs):
    """
    Does nothing for *sec* seconds and then prints out a message.

    .. note:: This function **is not** blocking.

    .. seealso:: :func:`blocking_wait`

    :param sec: Time to wait, in seconds.
    :param kwargs: Additional parameters.
    """
    await asyncio.sleep(sec)
    print("{0}: Done waiting for {1} sec.".format(kwargs['rulename'], sec))

async def raise_exception(**kwargs):
    """
    Raises a dummy Exception.

    :param kwargs: Additional parameters.
    :raises: Exception, always.
    """
    raise Exception("Catch me if you can.")

