from twilio.rest import Client
import os

def send_sms(to_number, message):
    try:
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        message = client.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=to_number
        )
        
        return True, message.sid
    except Exception as e:
        return False, str(e)

def send_milk_receipt(phone_number, entry_data):
    message = (
        f"MilkMagic Receipt\n"
        f"Date: {entry_data['date']}\n"
        f"Shift: {entry_data['shift']}\n"
        f"Quantity: {entry_data['quantity']}L\n"
        f"Amount: ₹{entry_data['amount']}\n"
        "Thank you!"
    )
    
    return send_sms(phone_number, message) 