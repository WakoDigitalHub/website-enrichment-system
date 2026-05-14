import re


def extract_emails(text):
    return re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)


def test_email_extraction():
    text = "Contact us at info@example.com or support@domain.org"
    emails = extract_emails(text)
    assert "info@example.com" in emails
    assert "support@domain.org" in emails
