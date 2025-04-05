from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import requests
import websocket
import threading
import re
import time
import sys
import os

CONFIG={
    "email": "Skyhighsuppliesgroup@gmail.com",
    "password": "Punnu@6669",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NzkyOGJjZDRlMDRjMTNhYmM1YmI4YTYiLCJyb2xlIjoidXNlciIsInNlc3Npb24iOjE3NDMzNDk4MzA5MTYsImlhdCI6MTc0MzYxMzg2NSwiZXhwIjoxNzc1MTcxNDY1fQ.Sztt8_Ai63sIGLiM4ipwVwPkv5y0baO1dGzboUYGTPM",
    "bot_token": "7709984983:AAGRnPJfk_T-h9vQYSPh0JhpK9FqMFPCMq4",
    "servers": [
        {
            "businessCode": "fff",
            "server": "server1"
        }
    ]
}
DATA={}


Bot_TOKEN =  CONFIG["bot_token"] 
JWT_TOKEN =  CONFIG["token"] 
SERVERS = CONFIG["servers"] 
SELECTED_SERVER = 1
EMAIL =  CONFIG["email"] 
PASSWORD =  CONFIG["password"] 


def login():
    url = "https://test.techyindia.xyz/users/login"
    payload = json.dumps({
    "email": EMAIL,
    "password": PASSWORD,
    "flag": True,
    "session": 1743349830916
    })
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
    'content-type': 'application/json',
    'origin': 'https://www.techyindia.xyz',
    'priority': 'u=1, i',
    'referer': 'https://www.techyindia.xyz/',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    res = response.json()
   
    CONFIG["token"] = res["token"]
       
    print(response.text)
    return res

def cancel_otp(serialNumber,server,mobileId):

    url = "https://test.techyindia.xyz/otp/cancelOtp"

    payload = json.dumps({
    "serialNumber": serialNumber,
    "server": server,
    "mobileId": mobileId
    })
    print("cancel_otp")
    print(payload)

    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
    'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NzkyOGJjZDRlMDRjMTNhYmM1YmI4YTYiLCJyb2xlIjoidXNlciIsInNlc3Npb24iOjE3NDMzNDk4MzA5MTYsImlhdCI6MTc0MzM5NzA2NCwiZXhwIjoxNzc0OTU0NjY0fQ.Izb5XMr03mviVubaNnVl4Vgb5X9WcvEohYROko15idk',
    'content-type': 'application/json',
    'origin': 'https://www.techyindia.xyz',
    'priority': 'u=1, i',
    'referer': 'https://www.techyindia.xyz/',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

def fetch_otp(token: str, serial_number: str, mobile_id: str, business_code: str, server="server2", resend=False, timeout=10) -> str:
    otp_response = {}
    print("Fetching OTP")
  
    url = f"wss://test.techyindia.xyz/check-otp?token={token}"

    payload = {
        "serialNumber": serial_number,
        "mobileId": mobile_id,
        "businessCode": business_code,
        "server": server,
        "resend": resend
    }
    print(payload)

    def on_open(ws):
        ws.send(json.dumps(payload))

    def on_message(ws, message):
        data = json.loads(message)
        otp_message = data.get("otpMessage", "")
        match = re.search(r"\b(\d{6})\b", otp_message)
        otp_response["otp"] = match.group(1) if match else None
        ws.close()

    def on_error(ws, error):
        otp_response["error"] = str(error)

    def on_close(ws, code, reason):
        pass

    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header=["Origin: https://www.techyindia.xyz"]
    )

    thread = threading.Thread(target=ws.run_forever)
    thread.start()
    thread.join(timeout)
    res = otp_response.get("otp", "OTP not found")
    print(res)
    return res

def wait_for_otp(jwt_token, serial, mobile_id, business_code,server, max_wait=30):
    start_time = time.time()

    while time.time() - start_time < max_wait:
        otp_msg = fetch_otp(jwt_token, serial, mobile_id, business_code,server)

        if otp_msg and "OTP not found" not in otp_msg:
            return otp_msg  # ✅ Got valid OTP, return it
            
        time.sleep(3)
    return None  # ❌ Timed out

def get_valid_number(jwt_token, servers, timeout=120):
    start_time = time.time()
    otp_data = None

    while time.time() - start_time < timeout:
        for server in servers:
            otp_data = generate_new_otp(jwt_token, server)
            
            if "balance" in otp_data:
                return otp_data , server
    return None,None  # Timeout reached without success

def generate_new_otp(token,server_payload):
    url = "https://test.techyindia.xyz/mobile/generate"

    # payload = json.dumps({
    # "businessCode": "fff",
    # "server": "server3"
    # })

    payload = json.dumps(server_payload)

    print("Payload =>", server_payload)
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
    'authorization': token,
    'content-type': 'application/json',
    'origin': 'https://www.techyindia.xyz',
    'priority': 'u=1, i',
    'referer': 'https://www.techyindia.xyz/',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return response.json()

def flipkart_login(number):
    url = "https://1.rome.api.flipkart.com/api/7/user/otp/generate"

    payload = json.dumps({
    "loginId": number
    })
    headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://www.flipkart.com',
    'Referer': 'https://www.flipkart.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'X-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 FKUA/website/42/website/Desktop',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'Cookie': 'S=d1t12DT8/PzQ/PwhZSU4/Pz8DQNOjmrObkQ1Khi1O7+kuW+ipU8EFPDwtVipFxPaqU37le22MUTGVtpqot3kxutJRYA==; SN=2.VI34D965945B674238837A75862D0B057E.SI4CF2EF1FD1B9483D83D59E889E56C79B.VS19095D184C7C4F9F8B2805009041A206.1743407968; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3NDUxMzU5NjgsImlhdCI6MTc0MzQwNzk2OCwiaXNzIjoia2V2bGFyIiwianRpIjoiYzY0ZWRkODAtODYxMC00M2YzLTk0YjUtOWUzNDQ2NzNkOTU4IiwidHlwZSI6IkFUIiwidElkIjoibWFwaSIsInZzIjoiTE8iLCJ6IjoiQ0giLCJtIjp0cnVlLCJnZW4iOjR9.ZeH0isM6SST5F60NCMTphaCMuN39_bUEiqJqIYYM08E; ud=9.s6h1kDq2uZzvJmCRXlyNkglOl9LGdOurJCFsaS7eNV6hyY7CkzNIBI2nnPtPkufV6Xnas-ZTkPiRe68kLw4GkQ'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response



# Define the start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.effective_user.first_name
    custom_message = f"Hi {user_first_name}! 😊\nWelcome! I’m here to help you.\n/generate to generate OTP \n/login to login again!\n/cancel to cancel last request!\n/help to see what I can do!"
    await update.message.reply_text(custom_message)

# Define the help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = "Here’s what I can do:\n\n/start - Begin a conversation\n/help - Show available commands"
    await update.message.reply_text(help_message)

async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = login()
    await update.message.reply_text(response["message"])

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    


    if "number" in DATA:
        serialNumber = DATA["number"]["mobile"][0]["serialNumber"]
        server = DATA["server"]["server"]
        mobileId = DATA["number"]["mobile"][0]["_id"]
        response = cancel_otp(serialNumber,server,mobileId)
        message = response["message"]
    else:
        response = {}
        message = "First generate a number"
    await update.message.reply_text(message)

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = "Getting Number please wait for 2 minutes..."
    await update.message.reply_text(help_message)
    


    otp_data,server_data = get_valid_number(JWT_TOKEN, SERVERS)
    print(otp_data,server_data)


    if otp_data:

        DATA = {
            "number":otp_data,
            "server":server_data
            }

 

        mobile_number = otp_data["mobile"][0]["mobileno"]
        serial = otp_data["mobile"][0]["serialNumber"]
        mobile_id =  otp_data["mobile"][0]["_id"]
        business_code =otp_data["mobile"][0]["businessCode"]

        mobile_number_str = mobile_number.removeprefix("+91")

        await update.message.reply_text(f"Mobile Number :{mobile_number_str}")
        flipkart_login(mobile_number)

        otp_msg = wait_for_otp(JWT_TOKEN, serial, mobile_id, business_code,server_data["server"])

  
        if otp_msg:
            response = f"Mobile Number :{mobile_number_str}\nOTP : {otp_msg}\n"
        else:
            cancel_otp(serial,server_data["server"],mobile_id)
            response = f"Mobile Number :{mobile_number_str}\nOTP not found"
    else:   
        print(otp_data)
        response ="Sorry Due High Traffic this Service Mobile no is currently not available Please Try after sometime"

    await update.message.reply_text(response)



# Main function to run the bot
def main():
    print("Script has been started..!!")
    app = ApplicationBuilder().token(Bot_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("generate", generate_command))
    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("cancel", cancel_command))




    app.run_polling()

# Run the bot
if __name__ == "__main__":
    main()
