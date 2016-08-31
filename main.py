#!/usr/bin/env python
# coding: utf-8


__version__ = "0.wip"
__author__ = "François Kubler"
__copyright__ = "Copyright (c) 2016 François Kubler"
__license__ = "GPLv3"


import argparse
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


def read_cmdline():
    """
    """
    argp = argparse.ArgumentParser()

    # Add an optional string argument 'config':
    argp.add_argument("-c", "--config",
                      dest='config_file',
                      metavar='FILE',
                      help="read configuration from FILE.",
                      type=str);

    # Parse command line:
    args = argp.parse_args()

    return vars(args)


def main():
    """
    """
    # Monkey patch warnings.showwarning:
    warnings.showwarning = customized_warning

    # Read command line args, if any:
    args = read_cmdline()

    # Configuration file, if given on the command line:
    config_file = args['config_file']

    try:
        rig = Rig(config_file)
    except NoRuleError:
        msg = ("There are no valid rules in the config file. "
               "Rig can not run without rules.")
        print_err(msg)
    else:
        rig.start()
