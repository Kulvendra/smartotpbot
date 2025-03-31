# otp_fetcher.py

# otp_fetcher.py

import websocket
import json
import threading
import re

CONFIG={}
with open("config.json", 'r') as file:
    CONFIG = json.load(file)


JWT_TOKEN =  CONFIG["token"] 

def fetch_otp(token,pdata,timeout=10) -> str:
    otp_response = {}

    url = f"wss://test.techyindia.xyz/check-otp?token={token}"

    payload = pdata
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

    return otp_response.get("otp", "OTP not found.")



data = {'serialNumber': '1893743404354', 'mobileId': '67ea3d43eb9abb69f376c972', 'businessCode': 'fff', 'server': 'server2', 'resend': False}

# {'serialNumber': '1893743404354', 'mobileId': '67ea3d43eb9abb69f376c972', 'businessCode': 'fff', 'server': 'server2', 'resend': False}
otp_msg = fetch_otp(JWT_TOKEN,data)
print("Received OTP:", otp_msg)