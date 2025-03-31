import requests

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code}")
        print(response.text)

# Example usage
if __name__ == "__main__":
    BOT_TOKEN = "7709984983:AAGRnPJfk_T-h9vQYSPh0JhpK9FqMFPCMq4"
    CHAT_ID = "YOUR_CHAT_ID_HERE"
    MESSAGE = "Hello from Python! 👋...#kullu"

    send_telegram_message(BOT_TOKEN, CHAT_ID, MESSAGE)




