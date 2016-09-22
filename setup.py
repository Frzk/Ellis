#!/usr/bin/env python
# coding: utf-8


import re

from setuptools import setup


# Get version from `ellis/main.py`:
version = re.search('^__version__\s*=\s*"(.*)"',
                    open('ellis/main.py').read(),
                    re.M) \
            .group(1)


setup(name='ellis',
      version=version,
      description='Ellis monitors systemd-journald and triggers actions.',
      url='http://github.com/Frzk/Ellis',
      author='François KUBLER',
      author_email='francois+ellis@kubler.org',

      entry_points={
          "console_scripts": ['ellis = ellis.main:main']
      },

      # data_files=[
      #     ('/usr/lib/systemd/system', ['ellis.service']),
      # ],

      packages=[
          'ellis',
          'ellis_actions'
      ],

      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.5',
          'Topic :: Security',
          'Topic :: Utilities',
          'Topic :: System :: Monitoring',
      ],

      install_requires=[
          'smtplibaio >= 1.0.4',
          'systemd-python >= 231',
      ])
