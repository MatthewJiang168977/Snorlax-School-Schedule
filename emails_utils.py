from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
print("API Key starts with:", SENDGRID_API_KEY[:10]) 
def reminder_email(to_email, class_name, start_time, end_time, location): 
    print("ARE U WORKING")
    message = Mail( 
        from_email="coolpenguin36440@gmail.com",
        to_emails=to_email,
        subject=f'Reminder: {class_name} starts at {start_time}', 
        plain_text_content=f"""
Hello!

This is a reminder that your class "{class_name}" starts at {start_time} and ends at {end_time}.
Location: {location}

Don't be late!
"""
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print(f"Email sent to {to_email} for class {class_name}")
    except Exception as e:
        print(f"Error sending email: {e}")
