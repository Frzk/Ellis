#!/usr/bin/env python
# coding: utf-8


class Matches(dict):
    """
    Matches is a simple dictionnary of :class:`Counter`s that keeps track of 
    matching counts for all :class:`rule.Rule`s.

    When a new entry appears in the journald log, it is tested against several 
    :class:`rule.Rule`s :class:`filter.Filter`s. When a match is found, a 
    counter for this match has to be incremented by one so Rìg can trigger 
    the :class:`rule.Rule` :class:`action.Action` when the :class:`rule.Rule` 
    limit is reached. Matches allows us to do that.
    """
    def __init__(self):
        """
        Initializes a newly created Matches object.
        """
        super().__init__(self)

    def __missing__(self, key):
        """
        Sets `self[key]` to a new :class:`Counter`.

        *key* is a key that does not exist yet in self. It should be a 
        :class:`rule.Rule` name.

        Returns the newly created element (a :class:`Counter` instance).

        .. seealso::
            About :func:`__missing__`: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
        """
        self[key] = Counter()

        return self[key]

    def __str__(self):
        """
        """
        s = ''

        for rule_name in self:
            s += '{0}:\n{1}'.format(rule_name, self[rule_name])

        return s

    def add(self, rule, kwargs=None):
        """
        Increments the counter for the given *rule* and *kwargs*.

        If this pair of *rule* and *kwargs* doesn't already have a counter, it 
        is created.

        *rule* is the :class:`rule.Rule` instance that got the match.

        *kwargs* is an optional dict of vars captured by the 
        :class:`filter.Filter` that match the log entry.
        """
        index = self[rule.name].increment(kwargs)

        if self[rule.name][index] >= rule.limit:
            rule.action.run(kwargs)


class Counter(dict):
    """
    A Counter is a dict that keeps track of matching counts for **one specific 
    :class:`rule.Rule`**.
    """
    def __init__(self):
        """
        Initializes a newly created Counter.
        """
        super().__init__(self)

    def __missing__(self, key):
        """
        Sets `self[key]` to zero.

        *key* is a key that does not exist yet in self.

        Returns the newly created element (zero).
        """
        self[key] = 0

        return self[key]

    def __str__(self):
        """
        """
        s = ''

        for i in self:
            count = self[i]

            if i is not None:
                s = '  |-- {0} times for {1}\n'.format(count, i)
            else:
                s = '  |-- {0} times\n'.format(count)

        return s

    def increment(self, kwargs):
        """
        Increments the counter for the given *kwargs*.

        The counter index is computed from *kwargs*.

        *kwargs* is an optional dict of vars captured by the 
        :class:`filter.Filter` that match the log entry. An immutable version 
        of *kwargs* is used as an index to keep track of several counters for 
        the same :class:`rule.Rule`. It can be `None`.

        Returns the index of the updated counter.
        """
        index = None

        if kwargs:
            # index = hash(tuple(sorted(kwargs.items())))
            # Better keep something readable so we can output it.
            index = tuple(sorted(kwargs.items()))

        self[index] += 1

        return index

