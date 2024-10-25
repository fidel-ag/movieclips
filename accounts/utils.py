from smtplib import SMTPException
from socket import gaierror
from django.conf import settings
from django.core.mail import send_mail,EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .token import account_activation_token

def retrieve_Number_of_coins(payment_id,All_payment_data):
    for i in All_payment_data:
        if All_payment_data[i][0]==payment_id:
            return All_payment_data[i][1]

def get_token(user):
    message ={'uid': urlsafe_base64_encode( force_bytes(user.id)),
    'token': account_activation_token.make_token(user)}

        
    return message



def send_welcome_email_html(user_email,username, site_url):
    subject = "Welcome to LeadEditor.io – Take Control of Your VSLs!"
    
    html_content = f"""<p><span style="font-size:11pt;font-family:Arial,sans-serif;">Welcome to LeadEditor.io &ndash; Take Control of Your VSLs!</span></p>



<p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Hi {username},</span></strong></p>
<p><span style="font-size:11pt;font-family:Arial,sans-serif;">Your&nbsp;</span><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">LeadEditor.io</span></strong><span style="font-size:11pt;font-family:Arial,sans-serif;">&nbsp;account is live! You&rsquo;re now ready to test, edit, and optimize your leads with ease.</span></p>
<p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Next Steps:</span></strong></p>
<ol>
    <li style="list-style-type:decimal;font-size:11pt;font-family:Arial,sans-serif;">
        <p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Log in:</span></strong><span style="font-size:11pt;font-family:Arial,sans-serif;">&nbsp;Login to LeadEditor.io</span></p>
    </li>
    <li style="list-style-type:decimal;font-size:11pt;font-family:Arial,sans-serif;">
        <p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Start Testing:</span></strong><span style="font-size:11pt;font-family:Arial,sans-serif;">&nbsp;Upload your creatives and try new lead variations.</span></p>
    </li>
    <li style="list-style-type:decimal;font-size:11pt;font-family:Arial,sans-serif;">
        <p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Need Assistance?</span></strong><span style="font-size:11pt;font-family:Arial,sans-serif;">&nbsp;Contact us at support@LeadEditor.io.</span></p>
    </li>
</ol>
<p><span style="font-size:11pt;font-family:Arial,sans-serif;">Let&rsquo;s boost your video performance!</span></p>
<a href="{site_url}" style="font-size:11pt; font-family:Arial, sans-serif; color:black; text-decoration:none;">
    <strong><span style="font-size:11pt; font-family:Arial, sans-serif;">Login Now</span></strong>
</a>

<p><span style="font-size:11pt;font-family:Arial,sans-serif;">Best,</span><span style="font-size:11pt;font-family:Arial,sans-serif;"><br></span><span style="font-size:11pt;font-family:Arial,sans-serif;">The LeadEditor.io Team</span></p>
"""
    try:

        email = EmailMultiAlternatives(
            subject,
            strip_tags(html_content),  # Fallback text version
            settings.EMAIL_HOST_USER,
            [user_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except:
        return False
    
    # try:
    #     send_mail("aaaaaa","test",settings.EMAIL_HOST_USER,[user_email])
    #     return 'success'
    # except (ConnectionAbortedError, SMTPException, gaierror):
    #     return "error"

def send_password_reset(user_email,username, site_url):
    subject = "Reset Your Password for LeadEditor.io"
    html_content=f"""<p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Hi {username},</span></strong></p>
<p><span style="font-size:11pt;font-family:Arial,sans-serif;">You can reset your password using the link below:</span></p>
<a href="{site_url}" style="font-size:11pt; font-family:Arial, sans-serif; color:black; text-decoration:none;">
    <strong><span style="font-size:11pt; font-family:Arial, sans-serif;">Login Now</span></strong>
</a>
<p><span style="font-size:11pt;font-family:Arial,sans-serif;">This link will expire in&nbsp;</span><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">24 hours</span></strong><span style="font-size:11pt;font-family:Arial,sans-serif;">. If you didn&rsquo;t request this, just ignore the message.</span></p>
<p><span style="font-size:11pt;font-family:Arial,sans-serif;">Need help? Contact support@LeadEditor.io.</span></p>
<p><span style="font-size:11pt;font-family:Arial,sans-serif;">Best regards,</span><span style="font-size:11pt;font-family:Arial,sans-serif;"><br></span><span style="font-size:11pt;font-family:Arial,sans-serif;">The LeadEditor.io Team</span></p>"""
    try:

        email = EmailMultiAlternatives(
                subject,
                strip_tags(html_content),  # Fallback text version
                settings.EMAIL_HOST_USER,
                [user_email],
            )
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True
    except:
        return False
def send_client_message(user_email,username,message):
    subject="CLient Message"
    html_content=f"""
    <p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Client email : {user_email} </span></strong></p>
    <p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Client Full name :  {username} </span></strong></p>
    <p><strong><span style="font-size:11pt;font-family:Arial,sans-serif;">Client messaage : </span></strong></p>
<p><span style="font-size:11pt;font-family:Arial,sans-serif;">{message}</span></p>"""
    try:
        email = EmailMultiAlternatives(
                subject,
                strip_tags(html_content),  # Fallback text version
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
            )
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True
    except:
        return False

