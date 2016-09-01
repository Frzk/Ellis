#!/usr/bin/env python
# coding: utf-8


from .action import Action
from .filter import Filter


class Rule(object):
    """
    A Rule is a combination of a :class:`filter.Filter` and an 
    :class:`action.Action`.

   """
    def __init__(self, name, filter, limit, action):
        """
        Initializes a newly created Rule with the following arguments:

        *name* is the name of the Rule. It helps you identify the Rule.

        *filter* is a string containing the regular expressions that Rìg will 
        try to detect. It is converted in a :class:`filter.Filter` object.

        Each match increments a counter for the Rule. When *limit* is reached, 
        the action is executed.

        *action* is a string designating the action to execute when *limit* is 
        reached. It is converted in a :class:`action.Action` object.

        Raises ValueError if the limit is invalid (<=0, not an integer).

        Raises ValueError if the *filter* can't be converted in a 
        :class:`filter.Filter` object.

        Raises ValueError if 
        """
        self.name = name
        self.filter = None
        self.limit = None
        self.action = None

        self.check_limit(limit) \
            .build_filter(filter) \
            .build_action(action)

    def __repr__(self):
        """
        """
        return str(self)

    def __str__(self):
        """
        """
        return '<Rule - name: {0}, action: {1}, limit: {2}>' \
               .format(self.name, self.action, self.limit)

    def check_limit(self, limit):
        """
        """
        if limit > 0:
            self.limit = limit
        else:
            raise ValueError("Rule limit must be strictly > 0 ({0} given)"
                             .format(limit))

        return self

    def build_filter(self, filter):
        """
        """
        try:
            self.filter = Filter.from_string(filter, self.limit)
        except ValueError:
            raise

        return self

    def build_action(self, action):
        """
        """
        try:
            self.action = Action.from_string(action)
        except ValueError:
            raise

        return self

    def run_action(self, kwargs=None):
        """
        """
        self.action.run(kwargs)
