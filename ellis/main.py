#!/usr/bin/env python
# coding: utf-8


import argparse
import sys
import warnings

from .ellis import Ellis
from .exceptions import NoRuleError


__version__ = "1.0.dev1"
__author__ = ("François Kubler <francois+ellis@kubler.org>",)
__copyright__ = "Copyright (c) 2016 François Kubler"
__license__ = "GPLv3"
__url__ = "https://github.com/Frzk/Ellis"


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
    Parses optional command line arguments.
    """
    info = {
            "prog": "Ellis",
            "description": "%(prog)s version {0}".format(__version__),
            "epilog": "For further help please head over to {0}"
                      .format(__url__),
            "usage": argparse.SUPPRESS,
    }

    argp = argparse.ArgumentParser(**info)

    # Add an optional string argument 'config':
    argp.add_argument("-c", "--config",
                      dest='config_file',
                      metavar='FILE',
                      help="read configuration from FILE",
                      type=str)

    # Parse command line:
    args = argp.parse_args()

    return vars(args)


def main():
    """
    Entry point for Ellis.
    """
    # Monkey patch warnings.showwarning:
    warnings.showwarning = customized_warning

    # Read command line args, if any:
    args = read_cmdline()

    # Configuration file, if given on the command line:
    config_file = args['config_file']

    try:
        ellis = Ellis(config_file)
    except NoRuleError:
        msg = ("There are no valid rules in the config file. "
               "Ellis can not run without rules.")
        print_err(msg)
    else:
        ellis.start()
