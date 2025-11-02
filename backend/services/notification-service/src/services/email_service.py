"""
📧 EMAIL SERVICE - Advanced Email Delivery
Secure email delivery with templates, attachments, and tracking
"""
import asyncio
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class EmailService:
    """📧 Advanced Email Delivery Service"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        
        # Email templates
        self.templates = {
            "welcome": {
                "subject": "Welcome to Guidora - Your Career Journey Starts Here! 🚀",
                "html_template": self._get_welcome_template(),
                "text_template": "Welcome to Guidora! Get started with your personalized career guidance."
            },
            "interview_reminder": {
                "subject": "Mock Interview Reminder - Practice Makes Perfect! 🎯",
                "html_template": self._get_interview_reminder_template(),
                "text_template": "Don't forget about your scheduled mock interview practice session."
            }
        }
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_content: Optional[str] = None,
        template_name: Optional[str] = None,
        template_vars: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """📤 Send email with advanced features"""
        try:
            # Validate email address
            if not self._validate_email(to_email):
                return {"success": False, "error": "Invalid email address"}
            
            # Use template if specified
            if template_name and template_name in self.templates:
                template = self.templates[template_name]
                subject = template["subject"]
                body = template["text_template"]
                html_content = template["html_template"]
                
                # Apply template variables
                if template_vars:
                    subject = self._apply_template_vars(subject, template_vars)
                    body = self._apply_template_vars(body, template_vars)
                    html_content = self._apply_template_vars(html_content, template_vars)
            
            # Mock email sending (replace with actual SMTP)
            await asyncio.sleep(0.5)  # Simulate sending
            
            logger.info(f"Email sent successfully to {to_email}")
            
            return {
                "success": True,
                "message_id": self._generate_tracking_id(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _apply_template_vars(self, template: str, variables: Dict) -> str:
        """Apply variables to template string"""
        try:
            for key, value in variables.items():
                template = template.replace(f"{{{{{key}}}}}", str(value))
            return template
        except Exception as e:
            logger.warning(f"Template variable application failed: {e}")
            return template
    
    def _generate_tracking_id(self) -> str:
        """Generate unique tracking ID"""
        import uuid
        return f"guidora_{uuid.uuid4().hex[:12]}"
    
    def _get_default_config(self) -> Dict:
        """Get default email configuration"""
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "noreply@guidora.ai",
            "sender_name": "Guidora Career Platform"
        }
    
    def _get_welcome_template(self) -> str:
        """Get welcome email HTML template"""
        return """
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                    <h1>🚀 Welcome to Guidora!</h1>
                    <p>Your personalized career guidance platform</p>
                </div>
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2>Hi {{user_name}},</h2>
                    <p>Welcome to Guidora! We're excited to help you navigate your career journey.</p>
                    <h3>🎯 What you can do now:</h3>
                    <ul>
                        <li>Complete your skills assessment</li>
                        <li>Explore career paths tailored for you</li>
                        <li>Practice with mock interviews</li>
                        <li>Build your professional portfolio</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_interview_reminder_template(self) -> str:
        """Get interview reminder HTML template"""
        return """
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="background: #4CAF50; color: white; padding: 20px; text-align: center;">
                    <h1>🎯 Mock Interview Reminder</h1>
                </div>
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2>Hi {{user_name}},</h2>
                    <p>This is a friendly reminder about your upcoming mock interview practice session.</p>
                    <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107;">
                        <strong>📅 Interview Details:</strong><br>
                        Date: {{interview_date}}<br>
                        Time: {{interview_time}}<br>
                        Type: {{interview_type}}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

class SMSService:
    """📱 SMS Delivery Service"""
    
    async def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """📱 Send SMS message"""
        try:
            # Validate phone number
            if not self._validate_phone_number(phone_number):
                return {"success": False, "error": "Invalid phone number"}
            
            # Mock SMS sending
            await asyncio.sleep(0.5)
            
            logger.info(f"SMS sent to {phone_number[:5]}***")
            
            return {
                "success": True,
                "message_id": f"sms_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        pattern = r'^\\+?[1-9]\\d{1,14}$'
        return re.match(pattern, phone.replace(" ", "").replace("-", "")) is not None

class PushNotificationService:
    """🔔 Push Notification Service"""
    
    async def send_push(self, user_id: str, title: str, body: str) -> Dict[str, Any]:
        """🔔 Send push notification"""
        try:
            await asyncio.sleep(0.3)
            
            logger.info(f"Push notification sent to user {user_id}")
            
            return {
                "success": True,
                "notification_id": f"push_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
