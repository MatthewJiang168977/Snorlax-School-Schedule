from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import time
from dotenv import load_dotenv
import os 
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from emails_utils import reminder_email

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
class ClassSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    class_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)  
    location = db.Column(db.String(100), nullable=False)  
    days = db.Column(db.String(20), nullable=False)  # e.g., "Mon,Wed,Fri"
    email_sent = db.Column(db.Boolean, default=False)

app.debug = True

app.secret_key = 'This is your secret key to utilize session in Flask'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input', methods=("GET", "POST"))
def input():
    if request.method == "POST":
        email = request.form["Email Address"]
        class_name = request.form["Class Name"]
        days = request.form["date"]
        start_time = request.form["start"]
        end_time = request.form["end"]
        location = request.form["location"]

        new_class = ClassSchedule( 
            email=email,
            class_name = class_name, 
            class_time = time.fromisoformat(start_time),
            end_time = time.fromisoformat(end_time),
            location = location,
            days = days 
        )
        db.session.add(new_class)
        db.session.commit()
    return render_template('input.html')

def check_reminder(): 
    now = datetime.now(pytz.timezone("America/Phoenix"))
    thirty_minutes_later = now+timedelta(minutes=30)
    target_hour = thirty_minutes_later.hour 
    target_min = thirty_minutes_later.minute
    curr_day = now.strftime("%a")

    print(f"⏰ Checking reminders at {now.strftime('%Y-%m-%d %H:%M:%S')} for classes at {target_hour}:{target_min:02d} on {curr_day}")

    with app.app_context():
        all_classes = ClassSchedule.query.filter_by(email_sent=False).all()
        print(f"📚 Found {len(all_classes)} classes in DB")
        for c in all_classes: 
            print(f"   ➤ {c.class_name} on {c.days} at {c.class_time}")
            if curr_day in c.days:
                # Combine today's date with the class time
                class_datetime = now.replace(hour=c.class_time.hour, minute=c.class_time.minute, second=0, microsecond=0)

                # If the class starts between now and 30 minutes from now
                if now <= class_datetime <= thirty_minutes_later:
                    print(f"     ✅ Time match! Calling reminder_email for {c.email}")
                    reminder_email(
                        to_email=c.email, 
                        class_name=c.class_name,
                        start_time=c.class_time.strftime('%I:%M %p'),
                        end_time=c.end_time.strftime('%I:%M %p'),
                        location=c.location
                    )
                    c.email_sent = True

def reset_email_flags():
    with app.app_context():
        now = datetime.now(pytz.timezone("America/Phoenix"))
        # Reset flags for classes where class_time is before the current time
        past_classes = ClassSchedule.query.filter(ClassSchedule.class_time < now.time()).all()
        for c in past_classes:
            c.email_sent = False
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_reminder, trigger="interval", seconds=10)
scheduler.add_job(func=reset_email_flags, trigger="cron", hour=0, minute=0, timezone="America/Phoenix")
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        #db.drop_all()
        db.create_all()
    app.run(port=4455, debug=True, use_reloader=False)