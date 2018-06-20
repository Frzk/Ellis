=======
 Ellis
=======

Ellis monitors systemd-journald_ logs for specific entries and triggers actions based on them.

Ellis can obviously be used as an `Intrusion Prevention System (IPS)`_ but can also be used in a more general way to run a Python script whenever a pattern appears in the logs.

About
=====

I started Ellis as a pet project with two ideas in mind:

* I wanted to build something based on `Python's asyncio framework`_ because it looked very interesting and powerful - I needed to learn more about it ! ;
* I also wanted to be warned whenever someone would successfully log on my PC through SSH.

And then I realized that the combination of these two ideas would make a perfect candidate ! It then evolved into something more generic that looks a lot like the well-known fail2ban_.

Ellis specifically focuses on systemd-journald. It's written in Python and uses the asyncio framework for better performance (well, I hope so).

Features
========

* Monitors systemd-journald_ logs for given patterns ;
* Executes given commands when a pattern has been detected more than *N* times ;
* Uses ipset_ or nftables_ to block traffic from malicious hosts ;
* Can send e-mails to warn you about something ;
* Handles multiple services (or systemd-units) ;
* Single, simple config file.

Installing and configuring
==========================

Please read the Wiki_.

Contributing / Helping
======================

Code reviews, patches, comments, bug reports and feature requests are welcome. Please read the `Contributing guide`_ for further details.


.. _systemd-journald: https://www.freedesktop.org/software/systemd/systemd-journald.service.html
.. _Intrusion Prevention System (IPS): https://en.wikipedia.org/wiki/Intrusion_prevention_system
.. _Python's asyncio framework: https://docs.python.org/3/library/asyncio.html
.. _fail2ban: http://www.fail2ban.org/
.. _ipset: http://ipset.netfilter.org/
.. _nftables: https://netfilter.org/projects/nftables/
.. _Wiki: https://github.com/Frzk/Ellis/wiki
.. _Contributing guide: CONTRIBUTING.rst
