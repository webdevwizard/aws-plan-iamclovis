import base64
import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId, Email)
try:
    # Python 3
    import urllib.request as urllib
except ImportError:
    # Python 2
    import urllib2 as urllib
import time
import config

def scheduleEmail(addr, html, macroPDF, recommPDF):
    email = Email()
    email.email = 'Justin@iamclovis.com'
    email.name = 'Justin'
    message = Mail(
        from_email=email,
        to_emails=addr,
        subject='Your Custom Nutrition Plan',
        html_content=html)
    encoded = base64.b64encode(macroPDF).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('application/pdf')
    attachment.file_name = FileName('Your Custom Macros.pdf')
    attachment.disposition = Disposition('attachment')
    attachment.content_id = ContentId('1')
    message.add_attachment(attachment)
    attachment1 = Attachment()
    encoded1 = base64.b64encode(recommPDF).decode()
    attachment1.file_content = FileContent(encoded1)
    attachment1.file_type = FileType('application/pdf')
    attachment1.file_name = FileName('Your Custom Recommendations.pdf')
    attachment1.disposition = Disposition('attachment')
    attachment1.content_id = ContentId('2')
    message.add_attachment(attachment1)
    message.send_at = int(time.time()) # 
    try:
        sendgrid_client = SendGridAPIClient(config.SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)