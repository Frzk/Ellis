#!/usr/bin/env python
# coding: utf-8


import re
import sre_constants
import warnings


class Filter(list):
    """
    A Filter is a list of :class:`re.RegexObject` used to detect patterns in
    the journald log.

    When a new entry appears in the journald log, it is tested against all
    :class:`rule.Rule`s' Filter to check if one of them matches.

    A Filter can have multiple :class:`re.RegexObject`, each one corresponding
    to a different pattern. This means that if, for example, you want to
    detect failed SSH login attempts, you can have a single :class:`rule.Rule`
    with 3 different patterns (regular expressions).

    The :class:`re.RegexObject`s are initialized from the strings provided in
    the configuration file.

    A Filter **must have** at least one valid :class:`re.RegexObject`.

    .. note::
        To ease the writing of filters, we provide *tags*. These tags are
        pre-built regular expressions. They are available in
        `Filter.known_tags`.

        Currently, :class:`Filter` supports 2 tags :

            * <IP> : matches both IPv4 and IPv6 addresses (and more).
            * <PORT> : matches a valid port number (1..65534).

    .. note::
        Please use :func:`from_string` to create a new Filter. This will make
        sure the given regular expression(s) is (are) valid.
    """

    known_tags = {
        '<IP>': ('\S+'),

        '<PORT>': (r'([1-9]'            # 1..9
                   r'|[1-9][0-9]{1,3}'  # 10..9999
                   r'|[1-5][0-9]{4}'    # 10000..59999
                   r'|6[0-4][0-9]{3}'   # 60000..64999
                   r'|65[0-4][0-9]{2}'  # 65000..65499
                   r'|655[0-2][0-9]'    # 65500..65529
                   r'|6553[0-4])'),     # 65530..65534
    }

    def __init__(self, regexes):
        """
        Initializes a newly created Filter with the given list of
        :class:`re.RegexObject`.

        *regexes* is a list of :class:`re.RegexObject`s.

        Raises :class:`exceptions.ValueError` if the given list evaluates to
        False (empty list, None, ...)
        """
        if regexes:
            list.__init__(self, regexes)
        else:
            raise ValueError("Unable to initialize a Filter without at least "
                             "one valid pattern, please fix your config file")

    @classmethod
    def replace_tags(cls, raw_filter):
        """
        Searches for known tags in the given string and replaces them with the
        corresponding regular expression.

        *raw_filter* is an (optionnaly tagged) regular expression.

        Returns the regular expression with known tags replaces by the
        corresponding regular expression.
        """
        for k, v in iter(cls.known_tags.items()):
            raw_filter = raw_filter.replace(k, v)

        return raw_filter

    @classmethod
    def build_regex_list(cls, filter_str, rule_limit):
        """
        Creates a list of :class:`re.RegexObject`s from the given string.

        *filter_str* is a string containing the regular expressions used to
        build the Filter.

        If *filter_str* contains newlines chars, it is split in different
        regular expressions (one per line).

        If one of these strings can not be compiled into a
        :class:`re.RegexObject`, a warning is issued and the pattern is
        ignored.

        *rule_limit* is the Rule's limit above which the Action is executed.

        If *rule_limit* is > 1 and *filter_str* doesn't have at least one named
        capturing group, a warning is issued and the pattern is ignored.

        Returns a list of :class:`re.RegexObject`s built upon the given string.
        """
        regexes = []

        for f in filter_str.splitlines():
            try:
                regex = re.compile(f, flags=re.MULTILINE|re.IGNORECASE)
            except sre_constants.error:
                warnings.warn("Unable to compile this pattern: \"{0}\". "
                              "It will be ignored"
                              .format(f))
            else:
                # If the Rule limit is > 1, the pattern MUST have a capturing
                # group.
                # (this capturing group will be used later as an index to
                # count the matches.)
                # If the pattern doesn't respect this, it will be ignored.
                if rule_limit > 1 and not regex.groupindex:
                    warnings.warn("The pattern \"{0}\" doesn't have a "
                                  "capturing group but needs one."
                                  "It will be ignored"
                                  .format(f))
                else:
                    regexes.append(regex)

        return regexes

    @classmethod
    def from_string(cls, raw_filter, rule_limit):
        """
        Creates a new Filter instance from the given string.

        *raw_filter* is the raw filter : a string that may contain several
        regular expressions (separated by a newline char) and tags.

        *rule_limit* is the Rule's limit above which the Action is executed.

        Raises :class:`exceptions.ValueError` if the given string could not be
        compiled in at least one suitable :class:`re.RegexObject`.

        Returns a new :class:`Filter` instance.
        """
        parsed_filter = cls.replace_tags(raw_filter)
        regexes = cls.build_regex_list(parsed_filter, rule_limit)

        return cls(regexes)
