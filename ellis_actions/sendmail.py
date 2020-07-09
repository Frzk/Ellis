#!/usr/bin/env python
# coding: utf-8

from .shell_commander import ShellCommander


class SendmailNotFound(Exception):
    pass


class Sendmail(ShellCommander):
    """
    """
    CMD = 'sendmail'

    def __init__(self):
        """
        """
        super().__init__()

    async def send(self, msg):
        """

        """
        args = ['-t', '-oi']

        return await self.start(__class__.CMD, args, msg)

    def handle_error(self, err):
        """
        """
        msg = err.decode()

        print(f"FIXME (raise a custom  Exception) - {msg}")


async def send(from_addr, to_addr, subject='Ellis', msg='', **kwargs):
    """
    Uses `sendmail` to send an e-mail to the provided address.
    """
    headers = f"To: {to_addr}"
    headers = f"{headers}\nFrom: {from_addr}"
    headers = f"{headers}\nSubject: {subject}"

    msg = f"{headers}\n\n{msg}"

    if kwargs:
        # To append kwargs to the given message, we first transform it
        # into a more human friendly string:
        values = "\n".join([f"{k}: {v}" for k, v in kwargs.items()])

        # Actually append caught values to the message:
        msg = f"{msg}\n\nThe following variables have been caught:\n{values}"

    # Message MUST be `bytes`:
    email = msg.encode('utf-8')

    # Finally, we can send the e-mail:
    sendmail = Sendmail()

    return await sendmail.send(email)
