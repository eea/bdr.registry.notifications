import smtplib


MSG = """Subject: test

This is a test.
"""

s = smtplib.SMTP()
s.connect("localhost", 25)
s.helo()

for i in range(5000):
    s.sendmail("test@example.com", "test-%s@example.com" % i, MSG)
s.quit()
