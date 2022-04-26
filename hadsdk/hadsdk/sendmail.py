# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Class for generating notification emails for CDDS processes
"""
import smtplib


class Sendmail(object):
    """Provides method for sending simple text email."""

    def __init__(self, email_env, process):
        """Initialises sendmail.

        Parameters
        ----------
        email_env: dict
            email configuration details
        process: str
            CDDS process type (e.g. extract)

        """
        self.smtpserver = email_env['server']
        self.sender = email_env['sender']
        self.receivers = email_env['receivers'].split("|")
        self.subject_prefix = email_env['subject_prefix']
        self.header = "CDDS Status Email: {} Process".format(process.upper())
        self.footer = " ----- end message -------"

    def send(self, mailto, subject, message):
        """
        Creates email and sends it to the specified recipient and
        the configured list of additional email receivers.

        Parameters
        ----------
        mailto: str
            target address for email
        subject: str
            email subject
        message: str
            email text body
        """
        receiver_list = self.receivers
        receiver_list.append(mailto)
        address_str = ", ".join(receiver_list)
        message_str = "{}\n\n{}\n\n{}".format(self.header, message,
                                              self.footer)

        emailmsg = """\
From: {}
To: {}
Subject: {}

{}
""".format(self.sender, address_str, self.subject_prefix + ' ' + subject,
           message_str)

        mail = smtplib.SMTP(self.smtpserver)
        mail.sendmail(self.sender, receiver_list, emailmsg)
        mail.quit()
