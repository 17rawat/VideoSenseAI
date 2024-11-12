from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from email.utils import formataddr
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("video_analyzer:dashboard")

        else:
            error_message = "Invaild username or password"
            return render(
                request, "account/login.html", {"error_message": error_message}
            )

    return render(request, "account/login.html")


def user_signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            error_message = "Username already taken"
            return render(
                request, "account/signup.html", {"error_message": error_message}
            )

        elif User.objects.filter(email=email).exists():
            error_message = "Email already registered"
            return render(
                request, "account/signup.html", {"error_message": error_message}
            )

        else:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect("video_analyzer:dashboard")

            except:  # noqa: E722
                error_message = "Error while creating account"
                return render(
                    request, "account/signup.html", {"error_message": error_message}
                )

    return render(request, "account/signup.html")


def user_logout(request):
    logout(request)
    return redirect("/")


def get_password_reset_email_template(username, reset_link, site_name):
    """Generate password reset email template with spam-prevention best practices"""

    html_message = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <!-- Company Header -->
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2C3E50; margin: 0;">{site_name}</h1>
        </div>
        
        <!-- Main Content -->
        <div style="background-color: #ffffff; padding: 20px; border-radius: 5px;">
            <p>Dear {username},</p>
            
            <p>You are receiving this email because you requested a password reset for your account at {site_name}.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background-color: #3498DB; 
                          color: #ffffff; 
                          padding: 12px 25px; 
                          text-decoration: none; 
                          border-radius: 5px; 
                          display: inline-block;
                          font-weight: bold;">
                    Reset Your Password
                </a>
            </div>
            
            <p>For security, this link will expire in 24 hours.</p>
            
            <p><strong>Didn't request this?</strong> If you didn't request a password reset, please ignore this email or contact our support team if you have concerns.</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #EAECEE;">
                <p>Best regards,<br>{site_name} Team</p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 20px; font-size: 0.8em; color: #7F8C8D;">
            <p>© {datetime.now().year} {site_name}. All rights reserved.</p>
            <p>This is a transactional email regarding your account security.</p>
            
        </div>
    </div>
</body>
</html>
"""
    return {
        "subject": f"{site_name} - Password Reset Request",
        "html_message": html_message,
    }


def forgot_password(request):
    if request.method == "POST":
        try:
            email = request.POST["email"]
            print(email)
            user = User.objects.filter(email=email).first()
            print(user)

            if user:
                token = default_token_generator.make_token(user)
                print(token)

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                print(uid)

                reset_link = request.build_absolute_uri(
                    f"/account/password-reset/{uid}/{token}/"
                )
                # print(reset_link)

                # return redirect(reset_link)

                email_content = get_password_reset_email_template(
                    username=user.username,
                    reset_link=reset_link,
                    site_name=settings.SITE_NAME,
                )

                email_message = EmailMessage(
                    subject=email_content["subject"],
                    body=email_content["html_message"],
                    from_email=formataddr(
                        (settings.SITE_NAME, f"noreply@{settings.SITE_DOMAIN}")
                    ),
                    to=[formataddr((user.username, email))],
                    reply_to=[f"support@{settings.SITE_DOMAIN}"],
                )

                email_message.content_subtype = "html"

                # Add custom headers to improve deliverability
                email_message.extra_headers = {
                    "List-Unsubscribe": f"<mailto:unsubscribe@{settings.SITE_DOMAIN}>",
                    "X-Entity-Ref-ID": f"reset-password-{user.id}",
                    "Precedence": "bulk",
                }
                email_message.send(fail_silently=False)

                print("Email sent successfully")

                success_message = "Password reset link has been sent to your email"
                return render(
                    request,
                    "account/forgot_password.html",
                    {"success_message": success_message},
                )

            error_message = "Email not found in our records"
            return render(
                request,
                "account/forgot_password.html",
                {"error_message": error_message},
            )

        except Exception as e:  # noqa: E722
            error_message = f"An error occurred while processing your request: {str(e)}"
            return render(
                request,
                "account/forgot_password.html",
                {"error_message": error_message},
            )

    return render(request, "account/forgot_password.html")


def password_reset(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Verify the token first, before processing any password change
        if not default_token_generator.check_token(user, token):
            return render(
                request,
                "account/password_reset.html",
                {"error_message": "Invalid or expired reset link"},
            )

        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return redirect("account:password_reset_success")
            else:
                error_message = "Passwords do not match"
                return render(
                    request,
                    "account/password_reset.html",
                    {"error_message": error_message},
                )

        return render(request, "account/password_reset.html")

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(
            request,
            "account/password_reset.html",
            {"error_message": "Invalid reset link"},
        )


@login_required(login_url="/account/login")
def password_reset_success(request):
    return render(request, "account/password_reset_success.html")
