#!/usr/bin/env python
# coding: utf-8


import ast
import asyncio
import functools
import importlib

from .exceptions import UnsupportedActionError, UnsupportedActionArgumentError


class Action(object):
    """
    An Action is what Ellis executes when a Rule reaches its limit.

    It's mostly a function with parameters. i.e. an Action is valid if it is
    *callable*.

    :Example of Actions:

        * A function that sends an e-mail,
        * A function that starts or stops a service,
        * A function that uses iptable to ban an IP address, ...

    .. note::
        Please use :func:`from_string` to create a new Action. This will make
        sure it exists, it is imported and it is callable.
    """
    def __init__(self, module, func, args=None):
        """
        Initializes a newly created Action with the given module name,
        function name and function arguments.

        *module* is the name of the module containing the function. The module
        **must** be provided by the *actions* package to be imported.

        *func* is the name of the function to execute.

        *args* (optional) is a dict of arguments to pass to the function.

        Raises :class:`exceptions.ValueError` if the given module can not be
        imported, if the given function doesn't exist in the given module or
        if the Action is not valid (see :func:`is_valid`).
        """
        self.mod_name = module
        self.func_name = func
        self.func = None
        self.args = args if args is not None else {}

        # Let's try to import the required module from the 'actions' package:
        try:
            mod = importlib.import_module("ellis_actions." + self.mod_name)
        except ImportError:
            raise ValueError(("Provided action ({mod}.{func}) does not exist "
                              "(unable to import '{mod}' module from the "
                              "'ellis_actions' package)")
                             .format(mod=self.mod_name, func=self.func_name))

        # If it succeeded, we can go on and try to retrieve the function from
        # the imported module:
        try:
            self.func = getattr(mod, self.func_name)
        except AttributeError:
            raise ValueError("Provided action ({mod}.{func}) does not exist"
                             .format(mod=self.mod_name, func=self.func_name))

        # We finally have to check that the action is valid:
        if not self.is_valid():
            raise ValueError("Provided action ({mod}.{func}) is not valid"
                             .format(mod=self.mod_name, func=self.func_name))

    def __repr__(self):
        """
        """
        s = "{0}.{1}".format(self.mod_name, self.func_name)

        if self.args:
            s = '{0}({1})'.format(s, self.args)

        return s

    def is_valid(self):
        """
        Checks if the Action is valid or not.

        An Action is considered valid if its function is *callable*.

        Returns True if the Action is valid, False otherwise.
        """
        return callable(self.func)

    def _prepare(self, kwargs=None):
        """
        Updates the function arguments and creates a :class:`asyncio.Task`
        from the Action.

        *kwargs* is an optional dictionnary of additional arguments to pass to
        the Action function.

        .. warning::
            *kwargs* will overwrite existing keys in *self.args*.

        .. note::
            If the Action func is blocking (not a coroutine function), it will
            be executed in an `Executor`_.

        .. _Executor: https://docs.python.org/3/library/asyncio-eventloop.html#executor
        """
        if kwargs is not None:
            # Note: This will overwrite existing keys in self.args.
            #       This is the wanted behavior.
            self.args.update(kwargs)

        if asyncio.iscoroutinefunction(self.func):
            task = asyncio.ensure_future(self.func(**self.args))
        else:
            # FIXME: is that clean enough ?
            task = asyncio.get_event_loop() \
                   .run_in_executor(None,
                                    functools.partial(self.func,
                                                      **self.args))

        return task

    async def run(self, kwargs=None):
        """
        Wraps the action in a :class:`asyncio.Task` and schedules its
        execution.

        *kwargs* is an (optional) dictionnary of additional arguments to pass
        to the Action function.
        """
        task = self._prepare(kwargs)

        try:
            await task
        except Exception as e:
            # FIXME: write a better Exception handler.
            print("EXC:\n  {0}".format(e))

    @classmethod
    def from_string(cls, action_str):
        """
        Creates a new Action instance from the given string.

        The given string **must** match one of those patterns:

            * module.function
            * module.function()
            * module.function(arg1=value1, arg2=value2)

        Any other form will trigger an Exception.

        The function parses the given string and tries to load the function
        from the given module.

        Raises :class:`exceptions.SyntaxError` if the compiled source code is
        invalid.

        Raises :class:`exceptions.ValueError` if the given source code contains
        null bytes.

        Raises :class:`exceptions.UnsupportedActionError` if the given source
        code can not be parsed (doesn't match one of the supported patterns).

        Raises :class:`exceptions.UnsupportedActionArgumentError` if one the
        given argument has an unsupported type (we only support
        :class:`ast.Num` and :class:`ast.Str`).

        Returns a new :class:`Action` instance.
        """
        args = {}

        try:
            mod_obj = ast.parse(action_str)
        except (SyntaxError, ValueError) as e:
            raise e
        else:
            call_obj = mod_obj.body[0].value

            if isinstance(call_obj, ast.Attribute):
                # Seems like we have a simple function name
                # (for example `module.function`)
                module = call_obj.value.id
                func = call_obj.attr

            elif isinstance(call_obj, ast.Call):
                # Seems like we have a function call, maybe with
                # a few parameters.
                # Note that we only support `module.function()` format.
                # You can't use `function()`.
                try:
                    module = call_obj.func.value.id
                    func = call_obj.func.attr
                except AttributeError:
                    raise UnsupportedActionError(action_str)
                else:
                    # If we have arguments, they MUST be named:
                    for kwarg in call_obj.keywords:
                        # We only support Strings and Numerics:
                        if isinstance(kwarg.value, ast.Num):
                            args.update({kwarg.arg: kwarg.value.n})
                        elif isinstance(kwarg.value, ast.Str):
                            args.update({kwarg.arg: kwarg.value.s})
                        else:
                            raise UnsupportedActionArgumentError(action_str,
                                                                 kwarg)

            else:
                raise UnsupportedActionError(action_str)

        return cls(module, func, args)
