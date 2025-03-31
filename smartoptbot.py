from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from otp_server import login,get_valid_number,wait_for_otp,cancel_otp,flipkart_login
import json

CONFIG={}
with open("config.json", 'r') as file:
    CONFIG = json.load(file)

Bot_TOKEN =  CONFIG["bot_token"] 
JWT_TOKEN =  CONFIG["token"] 
SERVERS = CONFIG["servers"] 
SELECTED_SERVER = 1
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
    
    with open("data.json", 'r') as file:
        DATA = json.load(file)  

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

        json_data = {
            "number":otp_data,
            "server":server_data
            }
        with open("data.json", "w") as f:
            json.dump(json_data,f, indent=4)

        mobile_number = otp_data["mobile"][0]["mobileno"]
        serial = otp_data["mobile"][0]["serialNumber"]
        mobile_id =  otp_data["mobile"][0]["_id"]
        business_code =otp_data["mobile"][0]["businessCode"]

        mobile_number_str = mobile_number.removeprefix("+91")

        await update.message.reply_text(f"Mobile Number :{mobile_number_str}")
        flipkart_login(mobile_number)

        otp_msg = wait_for_otp(JWT_TOKEN, serial, mobile_id, business_code,server_data["server"])

  
        if otp_msg:
            response = f"Mobile Number :{mobile_number_str}\nOTP : {otp_msg}\nBalance : {otp_data["balance"]}"
        else:
            cancel_otp(serial,server_data["server"],mobile_id)
            response = f"Mobile Number :{mobile_number_str}\nOTP not found"
    else:   
        print(otp_data)
        response ="Sorry Due High Traffic this Service Mobile no is currently not available Please Try after sometime"

    await update.message.reply_text(response)



# Main function to run the bot
def main():
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
