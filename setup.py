#!/usr/bin/env python
# coding: utf-8


import re

from setuptools import setup


# Get version from `rig/main.py`:
version = re.search('^__version__\s*=\s*"(.*)"',
                    open('rig/main.py').read(),
                    re.M) \
            .group(1)


setup(name='rig',
      version=version,
      description='Rìg monitors systemd-journald and triggers actions.',
      url='http://github.com/Frzk/Rig',
      author='François KUBLER',
      author_email='francois+rig@kubler.org',

      entry_points={
          "console_scripts": ['rig = rig.main:main']
      },

      # data_files=[
      #     ('/usr/lib/systemd/system', ['rig.service']),
      # ],

      packages=[
          'rig',
          'rig_actions'
      ],

      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environnement :: Console',
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
