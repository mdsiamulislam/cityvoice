import os
import firebase_admin
from firebase_admin import messaging, credentials
from django.conf import settings

def send_notification(token, title, body):
    # ১. Firebase ইনিশিয়ালাইজেশন
    if not firebase_admin._apps:
        # আপনার দেয়া পাথটি এখানে সেট করা হয়েছে
        # ফাইল নেম আপনার ডাউনলোড করা ফাইলের নামের সাথে মিলিয়ে নিন (যেমন: serviceAccountKey.json)
        cred_path = r'C:\Users\Betopia\Downloads\firebaseKey.json' 
        
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Firebase Initialization Error: {e}")
            return None

    # ২. মেসেজ কনফিগুরেশন
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                priority='max',
                default_sound=True,
                notification_count=1,
                # icon এবং color আপনার অ্যাপের কনফিগ অনুযায়ী কাজ করবে
                # icon='ic_notification', 
                # color='#0D1024',
            ),
        ),
        token=token,
    )

    print(f"Attempting to send notification to: {token[:10]}...")

    # ৩. মেসেজ পাঠানো
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
        return response
    except Exception as e:
        print(f"Firebase Sending Error: {e}")
        return str(e)