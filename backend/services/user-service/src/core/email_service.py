"""
Email service for sending verification and password reset emails
Supports SendGrid, SMTP, and local development mode
"""
import os
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import aiosmtplib
from jinja2 import Template

logger = logging.getLogger(__name__)


class EmailService:
    """Production-ready email service with multiple backends"""
    
    def __init__(self):
        self.email_backend = os.getenv("EMAIL_BACKEND", "smtp")  # smtp, sendgrid, console
        self.from_email = os.getenv("FROM_EMAIL", "noreply@guidora.ai")
        self.from_name = os.getenv("FROM_NAME", "Guidora")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # SMTP settings
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        # SendGrid (future)
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using configured backend"""
        try:
            if self.email_backend == "console":
                return self._send_console(to_email, subject, html_content)
            elif self.email_backend == "sendgrid":
                return await self._send_sendgrid(to_email, subject, html_content)
            else:  # smtp (default)
                return await self._send_smtp(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _send_console(self, to_email: str, subject: str, html_content: str) -> bool:
        """Development mode: print to console"""
        logger.info("=" * 80)
        logger.info(f"📧 EMAIL (Console Mode)")
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 80)
        logger.info(html_content)
        logger.info("=" * 80)
        return True
    
    async def _send_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send via SMTP (Gmail, etc.)"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text version
            if text_content:
                message.attach(MIMEText(text_content, "plain"))
            
            # Add HTML version
            message.attach(MIMEText(html_content, "html"))
            
            # Send via aiosmtplib (async)
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            logger.info(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
    
    async def _send_sendgrid(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send via SendGrid API (future implementation)"""
        logger.warning("SendGrid not implemented yet, falling back to console")
        return self._send_console(to_email, subject, html_content)
    
    async def send_verification_email(self, to_email: str, token: str, user_name: str = "") -> bool:
        """Send email verification link"""
        verification_link = f"{self.frontend_url}/verify-email?token={token}"
        
        html_content = self._get_verification_template(user_name, verification_link)
        text_content = f"""
Welcome to Guidora!

Please verify your email by clicking this link:
{verification_link}

This link will expire in 24 hours.

If you didn't create a Guidora account, please ignore this email.
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Verify Your Guidora Account",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_password_reset_email(self, to_email: str, token: str, user_name: str = "") -> bool:
        """Send password reset link"""
        reset_link = f"{self.frontend_url}/reset-password?token={token}"
        
        html_content = self._get_reset_template(user_name, reset_link)
        text_content = f"""
Password Reset Request

Click this link to reset your Guidora password:
{reset_link}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email.
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Reset Your Guidora Password",
            html_content=html_content,
            text_content=text_content
        )
    
    def _get_verification_template(self, user_name: str, link: str) -> str:
        """HTML template for email verification"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; background: #667eea; color: white !important; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Guidora! 🚀</h1>
        </div>
        <div class="content">
            <p>Hi{' ' + user_name if user_name else ''},</p>
            <p>Thank you for signing up with Guidora! We're excited to help you on your career journey.</p>
            <p>Please verify your email address to activate your account:</p>
            <center>
                <a href="{link}" class="button">Verify Email Address</a>
            </center>
            <p>Or copy this link into your browser:</p>
            <p style="word-break: break-all; color: #667eea;">{link}</p>
            <p><strong>This link expires in 24 hours.</strong></p>
            <p>If you didn't create a Guidora account, you can safely ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2025 Guidora. All rights reserved.</p>
            <p>AI-powered career guidance platform</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_reset_template(self, user_name: str, link: str) -> str:
        """HTML template for password reset"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; background: #f5576c; color: white !important; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reset Your Password 🔐</h1>
        </div>
        <div class="content">
            <p>Hi{' ' + user_name if user_name else ''},</p>
            <p>We received a request to reset your Guidora password.</p>
            <p>Click the button below to choose a new password:</p>
            <center>
                <a href="{link}" class="button">Reset Password</a>
            </center>
            <p>Or copy this link into your browser:</p>
            <p style="word-break: break-all; color: #f5576c;">{link}</p>
            <div class="warning">
                <strong>⚠️ Security Notice:</strong><br>
                This link expires in 1 hour. If you didn't request a password reset, please ignore this email and your password will remain unchanged.
            </div>
        </div>
        <div class="footer">
            <p>© 2025 Guidora. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """


# Singleton instance
email_service = EmailService()
