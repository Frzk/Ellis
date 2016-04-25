# Rìg

Rìg monitors [systemd-journald](https://www.freedesktop.org/software/systemd/systemd-journald.service.html) logs for specific entries and triggers actions based on them.

Rìg can obviously be used as an [Intrusion Prevention System (IPS)](https://en.wikipedia.org/wiki/Intrusion_prevention_system) but can also be used in a more general way to run a Python script whenever a pattern appears in the logs.

## About

I started Rìg as a pet project with two ideas in mind:

  - I wanted to build something based on Python's **asyncio** framework because it looked very interesting and powerful - I needed to learn more about it ! ;
  - I also wanted to be warned whenever someone would successfully log on my PC through SSH.

And then I realized that the combination of these two ideas would make a perfect candidate ! It then evolved into something more generic that looks a lot like the well-known [`fail2ban`](http://www.fail2ban.org/).

Rìg specifically focuses on `systemd-journald`. It's written in Python and uses the [asyncio framework](https://docs.python.org/3/library/asyncio.html) for better performance (well, I hope so).

## Features

  - Monitors `journald` logs for given patterns ;
  - Executes given commands when a pattern has been detected for the same IP address more than *x* times ;
  - Uses `ipset` to block traffic from malicious hosts ;
  - Handles multiple services (or systemd-units) ;
  - Single, simple config file.

## Contributing / Helping

Code reviews, patches, comments, bug reports and requests are welcome. Please read the Contributing guide for further details.
