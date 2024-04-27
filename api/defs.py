import random
import smtplib
from email.mime.text import MIMEText

from api.models import User


def send_otp(email):
    otp = ''.join(random.choices('0123456789', k=4))

    sender_email = 'spark.contact.it@gmail.com'  # Change to your email
    sender_password = 'jocn twgx cnwt yvyt'  # Change to your email password

    message = f'Your OTP for password reset is: {otp}'

    msg = MIMEText(message)
    msg['Subject'] = 'Password Reset OTP'
    msg['From'] = sender_email
    msg['To'] = email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [email], msg.as_string())
        server.quit()

        # Save OTP in the user object
        try:
            user = User.objects.get(email=email)
            user.otp = otp
            user.save()
        except User.DoesNotExist:
            pass

        return otp
    except Exception as e:
        print("Error sending email:", e)
        return None
