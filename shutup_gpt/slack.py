import requests

def send_message_to_slack(text):
    webhook_url = 'https://hooks.slack.com/services/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'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'text': text
    }
    response = requests.post(url=webhook_url, headers=headers, json=data)
    return response.text

# Usage
send_message_to_slack("**Shut up GPT is live!** 🚀 High score is reset. Let's see who will claim it! 🏆")
