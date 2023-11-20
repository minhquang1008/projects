from win32com.client import Dispatch
import re
import codecs

def sendMail(email, title, body, mapping):

    file = codecs.open("basic.html", "r", "utf-8")
    template = file.read()
    mail = Dispatch('outlook.application').CreateItem(0)
    # mail.To = email
    mail.To = 'quangpham@phs.vn'
    mail.Subject = title
    body = body
    body = re.sub(r'{recipients.title}', mapping.get(email), body)
    content = str(template)
    content = re.sub(r'whatever', body, content)
    mail.HTMLBody = content
    mail.Send()

