#!/usr/bin/env python
# coding: utf-8


__version__ = "0.wip"
__author__ = "François Kubler"
__copyright__ = "Copyright (c) 2016 François Kubler"
__license__ = "GPLv3"


import sys
import warnings

from rig import Rig
from exceptions import NoRuleError


def customized_warning(message, category=UserWarning, filename='', lineno=-1):
    """
    Customized function to display warnings.
    Monkey patch for `warnings.showwarning`.
    """
    print("WARNING: {0}".format(message))


def print_err(*objs):
    """
    Print given objects to stderr.
    """
    print(*objs, file=sys.stderr, end='')


def main():
    """
    """
    warnings.showwarning = customized_warning

    try:
        rig = Rig()
    except NoRuleError:
        msg = ("There are no valid rules in the config file. "
               "Rig can not run without rules.")
        print_err(msg)
    else:
        rig.start()


if __name__ == '__main__':
    main()
