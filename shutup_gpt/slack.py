import requests

def send_message_to_slack(text, hook_url):
    webhook_url = hook_url,
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'text': text
    }
    response = requests.post(url=webhook_url, headers=headers, json=data)
    return response.text
