import requests
import json
import websocket
import json
import threading
import re
import time

CONFIG={}
with open("config.json", 'r') as file:
    CONFIG = json.load(file)

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

    CONFIG={}
    with open("config.json", 'r') as file:
        CONFIG = json.load(file)

    with open("config.json", 'w') as file:
        CONFIG["token"] = res["token"]
        json.dump(CONFIG, file, indent=4)
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
    return response.json()
