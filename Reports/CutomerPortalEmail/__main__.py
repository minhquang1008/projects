import requests
import time
import pandas as pd
from email_class import sendMail

beginningID = 10591

while True:
    print(beginningID)
    response = requests.get(f"https://cp-uat-app.phs.vn:8080/api/reports/email-noti/{beginningID}")
    print(response.status_code)
    if response.status_code != 200:
        time.sleep(5)
        continue
    subscriptionsData = response.json()
    subscriptionsData = subscriptionsData['data']
    df = pd.json_normalize(subscriptionsData)
    # get last id từ response
    lastID = response.json().get('meta').get('last_id')

    for i in range(1, len(df)):
        # tạo 1 list những địa chỉ mail người nhận
        if any(df['email.recipients'].iloc[i]):
            emails = [i.get('email') for i in df['email.recipients'].iloc[i] if len(i) != 0]
            # tên người nhận tương ứng để ghép vào nội dung mail
            titles = [i.get('title') for i in df['email.recipients'].iloc[i] if len(i) != 0]
            # tạo dictionary để map tên người nhận vào email tương ứng
            mapping = {emails[i]: titles[i] for i in range(len(emails))}
            title = df['email.title'].iloc[i]
            body = df['email.content'].iloc[i]
            for email in emails:
                # nếu beginning ID khác lastID vừa get được nghĩa là có record mới, thực hiện gửi mail
                if beginningID != lastID:
                    sendMail(email, title, body, mapping)
                    # cập nhật lại beginningID
                    beginningID = lastID
    time.sleep(20)
