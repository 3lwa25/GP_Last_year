"""
Django management command to test the email service
Usage: python manage.py test_email
"""

from django.core.management.base import BaseCommand
from jobapp.email_service import email_service
import os

class Command(BaseCommand):
    help = 'Test the email service with different providers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            help='Specific provider to test (gmail, outlook, sendgrid)',
            default='all'
        )
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            default='hirely8@gmail.com'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Testing Email Service Configuration'))
        self.stdout.write('=' * 60)
        
        # Show current email configuration
        self.stdout.write('\n📋 Email Provider Status:')
        status = email_service.get_provider_status()
        
        for provider, info in status.items():
            status_icon = '✅' if info['configured'] else '❌'
            self.stdout.write(f"{status_icon} {provider.upper()}: {'Configured' if info['configured'] else 'Not Configured'}")
            
            if info['configured']:
                config = info['config']
                self.stdout.write(f"   Host: {config['host']}")
                self.stdout.write(f"   Port: {config['port']}")
                self.stdout.write(f"   User: {config['user']}")
                self.stdout.write(f"   From: {config['from_email']}")
        
        # Test email sending
        configured_providers = [name for name, info in status.items() if info['configured']]
        
        if not configured_providers:
            self.stdout.write(self.style.ERROR('\n❌ No email providers are configured!'))
            self.stdout.write('\n📝 To configure Gmail:')
            self.stdout.write('   1. Set EMAIL_HOST_USER=hirely8@gmail.com')
            self.stdout.write('   2. Set EMAIL_HOST_PASSWORD=your_gmail_app_password')
            self.stdout.write('   3. Set DEFAULT_FROM_EMAIL=hirely8@gmail.com')
            return
        
        self.stdout.write(f'\n🚀 Testing email with configured providers: {", ".join(configured_providers)}')
        
        # Send test email
        result = email_service.send_contact_email(
            name='Email Test',
            email='test@hirely.com',
            message='This is a test email from the Django management command to verify email functionality.',
            recipient_email=options['to']
        )
        
        self.stdout.write('\n📊 Test Results:')
        self.stdout.write('=' * 40)
        
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f"✅ Email sent successfully via: {result['provider_used']}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Email sending failed: {result['error_message']}"))
            
            if result['fallback_attempts']:
                self.stdout.write('\n🔄 Fallback Attempts:')
                for attempt in result['fallback_attempts']:
                    status_icon = '❌' if attempt['status'] == 'failed' else '⏭️'
                    self.stdout.write(f"   {status_icon} {attempt['provider']}: {attempt['status']} ({attempt['reason']})")
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('🏁 Email service test completed.') 