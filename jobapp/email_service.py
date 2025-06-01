"""
Professional Email Service for Django Job Portal
Handles email sending with multiple providers and robust error handling
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
from typing import Optional, List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    """
    Professional email service with multiple provider support
    """
    
    def __init__(self):
        self.providers = self._get_email_providers()
        self.current_provider = 'gmail'  # Default provider
        
    def _get_email_providers(self) -> Dict[str, Dict[str, Any]]:
        """Configure email providers"""
        return {
            'gmail': {
                'host': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'user': os.environ.get('EMAIL_HOST_USER', 'hirely8@gmail.com'),
                'password': os.environ.get('EMAIL_HOST_PASSWORD', ''),
                'from_email': os.environ.get('DEFAULT_FROM_EMAIL', 'hirely8@gmail.com')
            },
            'outlook': {
                'host': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True,
                'user': os.environ.get('OUTLOOK_EMAIL_USER', ''),
                'password': os.environ.get('OUTLOOK_EMAIL_PASSWORD', ''),
                'from_email': os.environ.get('OUTLOOK_FROM_EMAIL', '')
            },
            'sendgrid': {
                'host': 'smtp.sendgrid.net',
                'port': 587,
                'use_tls': True,
                'user': 'apikey',
                'password': os.environ.get('SENDGRID_API_KEY', ''),
                'from_email': os.environ.get('SENDGRID_FROM_EMAIL', '')
            }
        }
    
    def _validate_provider_config(self, provider_name: str) -> bool:
        """Validate if provider configuration is complete"""
        provider = self.providers.get(provider_name)
        if not provider:
            return False
        
        required_fields = ['host', 'port', 'user', 'password', 'from_email']
        return all(provider.get(field) for field in required_fields)
    
    def _send_with_smtp(self, provider_config: Dict[str, Any], 
                       to_emails: List[str], subject: str, 
                       html_content: str, text_content: str = None) -> bool:
        """Send email using SMTP directly"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = provider_config['from_email']
            msg['To'] = ', '.join(to_emails)
            
            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connect and send
            with smtplib.SMTP(provider_config['host'], provider_config['port']) as server:
                server.starttls()
                server.login(provider_config['user'], provider_config['password'])
                server.send_message(msg)
                
            logger.info(f"✅ Email sent successfully via {self.current_provider} to {to_emails}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication failed for {self.current_provider}: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error for {self.current_provider}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email via {self.current_provider}: {e}")
            return False
    
    def send_contact_email(self, name: str, email: str, message: str, 
                          recipient_email: str = None) -> Dict[str, Any]:
        """
        Send contact form email with professional formatting
        """
        if not recipient_email:
            recipient_email = 'hirely8@gmail.com'
        
        # Generate email content
        subject = f"🎯 New Contact Form Submission from {name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; margin: -30px -30px 20px -30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .info-box {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; }}
                .message-box {{ background-color: #ffffff; border: 1px solid #e9ecef; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef; color: #6c757d; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #6c757d; margin-left: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 New Contact Form Submission</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Hirely Job Portal</p>
                </div>
                
                <div class="info-box">
                    <p><span class="label">👤 Name:</span><span class="value">{name}</span></p>
                    <p><span class="label">📧 Email:</span><span class="value">{email}</span></p>
                    <p><span class="label">📅 Submitted:</span><span class="value">{self._get_current_time()}</span></p>
                </div>
                
                <div class="message-box">
                    <h3 style="color: #495057; margin-top: 0;">💬 Message:</h3>
                    <p style="line-height: 1.6; color: #6c757d;">{message}</p>
                </div>
                
                <div class="footer">
                    <p>This email was sent automatically from the Hirely Job Portal contact form.</p>
                    <p><strong>Hirely</strong> - Your Gateway to Career Success</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        New Contact Form Submission - Hirely Job Portal
        
        Name: {name}
        Email: {email}
        Submitted: {self._get_current_time()}
        
        Message:
        {message}
        
        ---
        This email was sent automatically from the Hirely Job Portal contact form.
        """
        
        return self._send_email_with_fallback([recipient_email], subject, html_content, text_content)
    
    def _send_email_with_fallback(self, to_emails: List[str], subject: str, 
                                 html_content: str, text_content: str = None) -> Dict[str, Any]:
        """
        Attempt to send email with fallback to other providers
        """
        result = {
            'success': False,
            'provider_used': None,
            'error_message': None,
            'fallback_attempts': []
        }
        
        # Try providers in order of preference
        provider_order = ['gmail', 'outlook', 'sendgrid']
        
        for provider_name in provider_order:
            if not self._validate_provider_config(provider_name):
                result['fallback_attempts'].append({
                    'provider': provider_name,
                    'status': 'skipped',
                    'reason': 'incomplete_configuration'
                })
                continue
            
            provider_config = self.providers[provider_name]
            self.current_provider = provider_name
            
            logger.info(f"🔄 Attempting to send email via {provider_name}...")
            
            success = self._send_with_smtp(provider_config, to_emails, subject, html_content, text_content)
            
            if success:
                result['success'] = True
                result['provider_used'] = provider_name
                logger.info(f"✅ Email sent successfully via {provider_name}")
                return result
            else:
                result['fallback_attempts'].append({
                    'provider': provider_name,
                    'status': 'failed',
                    'reason': 'smtp_error'
                })
                logger.warning(f"⚠️ Failed to send via {provider_name}, trying next provider...")
        
        # If all providers failed
        result['error_message'] = "All email providers failed"
        logger.error("❌ Failed to send email via all configured providers")
        
        # Fall back to console output for development
        if settings.DEBUG:
            logger.info("📝 Falling back to console output for development")
            print(f"\n{'='*60}")
            print(f"📧 EMAIL DEBUG OUTPUT")
            print(f"{'='*60}")
            print(f"To: {', '.join(to_emails)}")
            print(f"Subject: {subject}")
            print(f"Content:\n{text_content or strip_tags(html_content)}")
            print(f"{'='*60}\n")
            
            result['success'] = True
            result['provider_used'] = 'console'
        
        return result
    
    def _get_current_time(self) -> str:
        """Get current formatted time"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all email providers"""
        status = {}
        for provider_name in self.providers:
            config_valid = self._validate_provider_config(provider_name)
            status[provider_name] = {
                'configured': config_valid,
                'config': {k: '***' if k == 'password' else v 
                          for k, v in self.providers[provider_name].items()}
            }
        return status

# Global instance
email_service = EmailService() 