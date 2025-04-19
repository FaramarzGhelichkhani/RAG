# -*- coding: utf-8 -*-
import requests

# curl https://api-llm.emofid.com/v1/chat/completions \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer $Mofid_API_KEY" \
#   -d '{
#      "model": "gpt-4o-mini",
#      "messages": [{"role": "user", "content": "Say this is a test!"}]
#    }'
Mofid_API_KEY = "sk-hr1wc4oajsZkb7gvYkENXQ"

def connect2llm(model, message, api_key):
    url = "https://api-llm.emofid.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": f"{model}",
        "messages": [{"role": "user", "content": f"{message}"}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code >= 200 and response.status_code < 300:
        resp = response.json()
        resp = resp['choices'][0]
        response_message = resp['message']['content']
        print(response_message)
        return response_message
    else:
        print(response.status_code)
        print(response.json())


if __name__ == "__main__": 
    message = '''
    از گزارشی که میدم بر طبق فرمتی که میدم خلاصه درست کن و خلاصه رو بهم تحویل بده.
    فرمت گزارش:
    نام کمپین:
    کد و لاین:
    نوع کمپین:
    صندوق‌های هدف:
    هدف:
    مشتریان تارگت:
    شروع تخمینی اجرا:
    مدت کمپین:
    کانال:
    نمونه گزارش:
    کمپین به نام شناسایی ویژگی‌های مهم مشتریان برای جذب در صندوق توان، با کد و لاین 004_mass که نوع کمپین آن acquisition است. صندوق‌های هدف این کمپین صندوق‌های توان است. هدف این کمپین، استخراج مهم‌ترین فیچرهایی که می‌توان با استفاده از آنها، مشتریان با پتانسیل بالا را در کمپین‌های بعدی صندوق توان جهت سرمایه‌گذاری در این صندوق شناسایی و هدف‌گذاری کرد. مشتریان تارگت آن مشتریانی که طبق خروجی مدل هوش مصنوعی، بالاترین احتمال محاسبه شده را از نظر واکنش مثبت به پیامک سرمایه‌گذاری در صندوق توان داشته‌اند می‌باشد. شروع تخمینی اجرا 5/10/1403 است و مدت کمپین مشخص نیست. کانال کمپین از طریق پیامک است.


    '''
    # connect2llm("gpt-3.5-turbo", message, Mofid_API_KEY)
    connect2llm("gpt-4o-mini", "Say this is a test!", Mofid_API_KEY)