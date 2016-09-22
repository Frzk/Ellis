#!/usr/bin/env python
# coding: utf-8


import ast


class NoRuleError(Exception):
    """
    Raised when Ellis is started without Rule.

    Possible cases :
        - The config file doesn't define any Rule.
        - The defined Rule are invalid.
    """
    pass


class UnsupportedActionError(ValueError):
    """
    Raised when a Rule has an action set to something that doesn't look like
    a callable name or a callable call.
    """
    # FIXME: add a link to the doc when it's written.
    msg = ("The action '{0}' does not seem valid. It has to be either a "
           "callable name or a callable call")

    def __init__(self, action):
        """
        """
        error_message = self.msg.format(action)
        super().__init__(error_message)


class UnsupportedActionArgumentError(ValueError):
    """
    Raised when a Rule has an action that seems to be a function call with
    argument(s) and one of these arguments has a type that is not supported.
    """
    # FIXME: add a link to the doc when it's written.
    msg = ("The action '{0}' relies on the argument '{1}' whose type isn't "
           "supported. We only support numbers (integer, float or complex) "
           "and strings ({2} given)")

    types = {
        ast.Bytes: "bytes",
        ast.List: "list",
        ast.Tuple: "tuple",
        ast.Set: "set",
    }

    def __init__(self, action_name, kwarg):
        """
        """
        try:
            arg_type_str = self.types[type(kwarg.value)]
        except KeyError:
            arg_type_str = "Unknown"

        error_message = self.msg.format(action_name, kwarg.arg, arg_type_str)
        super().__init__(error_message)
