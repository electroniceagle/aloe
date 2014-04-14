"""
Step definitions for working with Django email.
"""
from smtplib import SMTPException

from django.core import mail
from django.test.html import parse_html

from nose.tools import assert_equals

from lettuce import step


STEP_PREFIX = r'(?:Given|And|Then|When) '
CHECK_PREFIX = r'(?:And|Then) '
EMAIL_PARTS = ('subject', 'body', 'from_email', 'to', 'bcc', 'cc')
GOOD_MAIL = mail.EmailMessage.send


@step(CHECK_PREFIX + r'I have sent (\d+) emails?')
def mail_sent_count(step, count):
    """
    Then I have sent 2 emails
    """
    count = int(count)
    assert len(mail.outbox) == count, "Length of outbox is {0}".format(count)


@step(r'I have not sent any emails')
def mail_not_sent(step):
    """
    I have not sent any emails
    """
    return mail_sent_count(step, 0)


@step(CHECK_PREFIX + (r'I have sent an email with "([^"]*)" in the ({0})'
                      '').format('|'.join(EMAIL_PARTS)))
def mail_sent_content(step, text, part):
    """
    Then I have sent an email with "pandas" in the body
    """
    assert any(text in getattr(email, part)
               for email
               in mail.outbox
               ), "An email contained expected text in the {0}".format(part)


@step(CHECK_PREFIX + (r'I have not sent an email with "([^"]*)" in the ({0})'
                      '').format('|'.join(EMAIL_PARTS)))
def mail_sent_content(step, text, part):
    """
    Then I have sent an email with "pandas" in the body
    """
    assert all(text not in getattr(email, part)
               for email
               in mail.outbox
               ), "An email contained unexpected text in the {0}".format(part)


@step(CHECK_PREFIX + r'I have sent an email with the following in the body:')
def mail_sent_content_multiline(step):
    """
    Check whether an email contains the following text
    """
    for email in mail.outbox:
        try:
            assert_equals(email.body.strip(), step.multiline.strip())

        except AssertionError as e:
            print(e)
            continue

        return True

    raise AssertionError("No email contained the content")


@step(CHECK_PREFIX + r'I have sent an email with the following HTML alternative:')
def mail_sent_contains_html(step):
    """
    Check whether an email contains the following HTML
    """

    for email in mail.outbox:
        try:
            html = next(content for content, mime in email.alternatives
                        if mime == 'text/html')
            dom1 = parse_html(html)
            dom2 = parse_html(step.multiline)

            assert_equals(dom1, dom2)

        except AssertionError as e:
            print(e)
            continue

        return True

    raise AssertionError("No email contained the HTML")


@step(STEP_PREFIX + r'I clear my email outbox')
def mail_clear(step):
    """
    I clear my email outbox
    """
    mail.EmailMessage.send = GOOD_MAIL
    mail.outbox = []


def broken_send(*args, **kwargs):
    """
    Broken send function for email_broken step
    """
    raise SMTPException("Failure mocked by lettuce")


@step(STEP_PREFIX + r'sending email does not work')
def email_broken(step):
    """
    Break email sending
    """
    mail.EmailMessage.send = broken_send
