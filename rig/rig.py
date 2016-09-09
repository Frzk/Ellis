#!/usr/bin/env python
# coding: utf-8


import asyncio
import configparser
import os
import signal
import socket
import sys
import warnings

from systemd import journal

from .exceptions import NoRuleError
from .matches import Matches
from .rule import Rule
from .search_matches import SearchMatches


class Rig(object):
    """
    
    """
    def __init__(self, config_file=None):
        """
        Initializes a newly created Rig object.

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
        self.matches = Matches()
        self.loop = asyncio.get_event_loop()
        self.loop.set_exception_handler(self.exceptions_handler)

    def load_config(self, config_file=None):
        """
        If `config_file` is not None, tries to load Rìg configuration from
        the given location. If, for some reason,  the file can't be read,
        Rìg will not start.

        If no configuration file is given (`config_file` is None), tries to
        load Rìg configuration from these potential locations,
        in this specific order:

            1. `/etc/rig.conf`
            2. `/etc/rig/rig.conf`
            3. `./rig.conf`

        If more than one of these files exist, the configuration is merged
        which can lead to one or more section(s) being overriden.

        The last file (`./rig.conf`) takes precedence over the second one,
        which takes precedence over the first one.
        """
        if config_file is None:
            config_file = [
                '/etc/rig.conf',
                '/etc/rig/rig.conf',
                os.path.join(os.path.dirname(__file__), 'rig.conf'),
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
        Build a set of systemd units that Rìg will watch.

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

    def reader(self, journal_reader):
        """
        """
        op = journal_reader.process()

        if op is journal.APPEND:
            for entry in journal_reader:
                # print("{__REALTIME_TIMESTAMP} {MESSAGE}".format(**entry))
                future = asyncio.ensure_future(
                    self.process_entry(entry["MESSAGE"])
                )

    async def process_entry(self, message):
        """
        """
        for rule in self.rules:
            async for match in SearchMatches(rule, message):
                if match:
                    await self.matches.add(rule, match.groupdict())

        #     for match in rule.filter.search(message):
        #         if match:
        #             self.matches.increment(rule, match.groupdict())

    def start(self):
        """
        """
        print("Starting Rìg with {0} rule{1}."
              .format(len(self.rules), 's' if len(self.rules) > 1 else ''))

        with journal.Reader() as j:
            # Configure our journal:
            j.log_level(journal.LOG_INFO)

            # And seek to the end so we can get new messages:
            j.seek_tail()
            j.get_previous()

            # DEBUG MODE:
            # self.loop.set_debug(True)

            # Configure our journald reader to watch only some units:
            for unit in self.units:
                j.add_match(_SYSTEMD_UNIT=unit)

            # Then add our journald reader to our loop:
            self.loop.add_reader(j.fileno(), self.reader, j)

            # FIXME: How the f!ck am I supposed to handle CTRL+C properly ?!
            try:
                for s in (signal.SIGINT, signal.SIGTERM):
                    self.loop.add_signal_handler(s, self.exit)
            except ValueError as e:
                # FIXME:
                raise e
            except RuntimeError as e:
                # FIXME:
                raise e
            else:
                # FIXME: is that clean enough ?
                self.loop.run_forever()
                self.loop.remove_reader(j.fileno())
                self.loop.close()

    def exit(self):
        """
        """
        # FIXME: do we still need that ?
        #     test as soon as Rig is really processing entries.

        # pendings = asyncio.Task.all_tasks()

        # for task in pendings:
        #     if not task.cancelled():
        #         task.cancel()
        #         task.exception()

        self.loop.stop()
        # FIXME: would it be better to use self.loop.call_soon ?

    def exceptions_handler(self, loop, context):
        """
        """
        print("CAUGHT EXCEPTION:\n")
        print("  Message: {0}\n".format(context['message']))

        try:
            print("  Exception: {0}\n".format(context['exception']))
            print("  Future: {0}".format(context['future']))
        except:
            pass
