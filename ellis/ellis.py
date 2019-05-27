#!/usr/bin/env python
# coding: utf-8


import asyncio
import configparser
import os
import signal
import warnings

from systemd import journal

from .exceptions import NoRuleError
from .matches import Matches
from .rule import Rule
from .search_matches import SearchMatches


class Ellis(object):
    """
    """
    def __init__(self, config_file=None):
        """
        Initializes a newly created Ellis object.

        The initialization process takes care of reading the configuration
        file and build the necessary parts (rules, systemd units to watch,...)
        according to it.
        """
        self.rules = []
        self.units = set()
        self.config = configparser.ConfigParser()

        # Load config, rules and units:
        self.load_config(config_file) \
            .load_rules() \
            .load_units()

        # If we have rules, we can setup the matches object and the loop.
        # If not, an exception should have been raised.
        self.journal_reader = journal.Reader()
        self.matches = Matches()
        self.loop = asyncio.get_event_loop()
        self.loop.set_exception_handler(self.exceptions_handler)

    def __enter__(self):
        """
        """
        return self.start()

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        """
        """
        # FIXME: handle exceptions.
        self.exit()

    def load_config(self, config_file=None):
        """
        If `config_file` is not None, tries to load Ellis configuration from
        the given location. If, for some reason,  the file can't be read,
        Ellis will not start.

        If no configuration file is given (`config_file` is None), tries to
        load Ellis configuration from these potential locations,
        in this specific order:

            1. `/etc/ellis.conf`
            2. `/etc/ellis/ellis.conf`
            3. `./ellis.conf`

        If more than one of these files exist, the configuration is merged
        which can lead to one or more section(s) being overriden.

        The last file (`./ellis.conf`) takes precedence over the second one,
        which takes precedence over the first one.
        """
        if config_file is None:
            config_file = [
                '/etc/ellis.conf',
                '/etc/ellis/ellis.conf',
                os.path.join(os.path.dirname(__file__), 'ellis.conf'),
            ]

        self.config.read(config_file, encoding='utf-8')

        return self

    def load_rules(self):
        """
        Loads the Rules from the config file.

        An invalid Rule (no Filter or no Action) will trigger a warning
        message and will be ignored.
        """
        for rule_name in self.config.sections():

            limit = 1

            try:
                limit = self.config.getint(rule_name, 'limit')
            except ValueError:
                warnings.warn("Rule '{0}': invalid value for 'limit' option. "
                              "Limit must be an integer > 0. "
                              "Going on with the default value of 1."
                              .format(rule_name))
            except configparser.NoOptionError:
                warnings.warn("Rule '{0}': no value specified for 'limit' "
                              "option. Going on with the default value of 1."
                              .format(rule_name))

            try:
                filter_str = self.config.get(rule_name, 'filter')
                action_str = self.config.get(rule_name, 'action')
            except configparser.NoOptionError as e:
                warnings.warn("Ignoring '{0}' rule: {1}."
                              .format(rule_name, e))
            else:
                try:
                    rule = Rule(rule_name, filter_str, limit, action_str)
                except ValueError as e:
                    warnings.warn("Ignoring '{0}' rule: {1}."
                                  .format(rule_name, e))
                else:
                    self.rules.append(rule)

        if not self.rules:
            raise NoRuleError()

        return self

    def load_units(self):
        """
        Build a set of systemd units that Ellis will watch.

        This set will be used to filter journald entries so that we only
        process entries that were produced by these units.
        This should result in better performance.
        """
        # Of course, we only consider valid Rules.
        for rule in self.rules:
            try:
                systemd_unit = self.config.get(rule.name, 'systemd_unit')

            except configparser.NoOptionError:
                warnings.warn("Rule '{0}' doesn't have a `systemd_unit` "
                              "option set.\nThe filters will be checked "
                              "against all journald entries, which will "
                              "probably result in poor performance."
                              .format(rule.name))

                # At this point,  we can clear `self.units` because in any
                # case, we will need to process every journald entries
                # for THIS Rule.
                self.units.clear()

                # And we can also stop looping through rules.
                break

            else:
                # Append ".service" if not present.
                # Note that we don't check if the service actually exists.
                # FIXME ?
                if not systemd_unit.endswith(".service"):
                    systemd_unit += ".service"

                self.units.add(systemd_unit)

        return self

    def reader(self):
        """
        """
        op = self.journal_reader.process()

        if op is journal.APPEND:
            for entry in self.journal_reader:
                # print("{__REALTIME_TIMESTAMP} {MESSAGE}".format(**entry))
                asyncio.ensure_future(self.process_entry(entry["MESSAGE"]))

    async def process_entry(self, message):
        """
        """
        for rule in self.rules:
            async for match in SearchMatches(rule, message):
                if match:
                    await self.matches.add(rule, match.groupdict())

    def start(self):
        """
        """
        print("Starting Ellis with {0} rule{1}."
              .format(len(self.rules), 's' if len(self.rules) > 1 else ''))

        # Configure our journal:
        self.journal_reader.log_level(journal.LOG_INFO)

        # And seek to the end so we can get new messages:
        self.journal_reader.seek_tail()
        self.journal_reader.get_previous()

        # DEBUG MODE:
        # self.loop.set_debug(True)

        # Configure our journald reader to watch only some units:
        for unit in self.units:
            self.journal_reader.add_match(_SYSTEMD_UNIT=unit)

        # Then add our journald reader to our loop:
        self.loop.add_reader(self.journal_reader.fileno(), self.reader)

        return self

    def exit(self):
        """
        """
        self.loop.remove_reader(self.journal_reader.fileno())

        self.journal_reader.flush_matches()
        self.journal_reader.close()

        self.loop.stop()
        self.loop.close()

    def run(self):
        """
        """
        self.loop.run_forever()

    def exceptions_handler(self, loop, context):
        """
        """
        exception = context['exception']

        print("CAUGHT EXCEPTION:\n")
        print("  Message: {0}\n".format(context['message']))

        try:
            print("  Future: {0}\n".format(context['future']))
            print("  Exception: {0}".format(exception))
        except:
            pass
