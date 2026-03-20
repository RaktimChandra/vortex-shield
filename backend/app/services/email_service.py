from typing import Dict, List
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

class EmailService:
    def __init__(self, smtp_host: str = None, smtp_port: int = 587, smtp_user: str = None, smtp_password: str = None):
        self.smtp_host = smtp_host or "smtp.gmail.com"
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
    
    def send_email(self, to_email: str, subject: str, html_content: str):
        """Send email using SMTP"""
        if not self.smtp_user or not self.smtp_password:
            print(f"Email would be sent to {to_email}: {subject}")
            return True
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    def send_claim_approved_email(self, user_email: str, user_name: str, claim_data: Dict):
        """Send claim approval notification"""
        subject = "✅ Your Claim Has Been Approved - VORTEX Shield"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .amount {{ font-size: 36px; font-weight: bold; color: #10b981; text-align: center; margin: 20px 0; }}
                .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 14px; }}
                .button {{ display: inline-block; background: #0ea5e9; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Claim Approved!</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>Great news! Your claim has been approved and processed successfully.</p>
                    
                    <div class="amount">₹{claim_data.get('approved_amount', 0):,.2f}</div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span>Claim ID:</span>
                            <strong>{claim_data.get('id', 'N/A')}</strong>
                        </div>
                        <div class="detail-row">
                            <span>Trigger Type:</span>
                            <strong>{claim_data.get('trigger_type', 'N/A').title()}</strong>
                        </div>
                        <div class="detail-row">
                            <span>Processing Time:</span>
                            <strong>{claim_data.get('processing_time_seconds', 0)}s</strong>
                        </div>
                        <div class="detail-row">
                            <span>Payment Status:</span>
                            <strong style="color: #10b981;">Completed</strong>
                        </div>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="http://localhost:3000/dashboard/claims" class="button">View Claim Details</a>
                    </p>
                    
                    <p style="margin-top: 30px;">The payout has been processed and will be credited to your account shortly.</p>
                </div>
                <div class="footer">
                    <p>© 2024 VORTEX Shield 2.0 | Built by Team VORTEX</p>
                    <p>This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_claim_rejected_email(self, user_email: str, user_name: str, claim_data: Dict):
        """Send claim rejection notification"""
        subject = "❌ Claim Update - VORTEX Shield"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .reason {{ background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Claim Update</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>We regret to inform you that your recent claim could not be approved.</p>
                    
                    <div class="reason">
                        <strong>Reason:</strong> {claim_data.get('rejection_reason', 'The claim did not meet approval criteria.')}
                    </div>
                    
                    <p>If you believe this is an error or have questions, please contact our support team.</p>
                </div>
                <div class="footer">
                    <p>© 2024 VORTEX Shield 2.0 | Built by Team VORTEX</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_risk_alert_email(self, user_email: str, user_name: str, risk_data: Dict):
        """Send risk alert notification"""
        subject = "⚠️ Risk Alert - VORTEX Shield"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .alert {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Risk Alert</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>We've detected elevated risk levels in your area.</p>
                    
                    <div class="alert">
                        <strong>Risk Level:</strong> {risk_data.get('risk_level', 'HIGH')}<br>
                        <strong>Type:</strong> {risk_data.get('disruption_type', 'Weather')}<br>
                        <strong>Severity:</strong> {risk_data.get('severity', 'Moderate')}
                    </p>
                    
                    <p>Your coverage remains active and will automatically trigger if conditions meet the claim thresholds.</p>
                </div>
                <div class="footer">
                    <p>© 2024 VORTEX Shield 2.0 | Built by Team VORTEX</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_weekly_summary_email(self, user_email: str, user_name: str, summary_data: Dict):
        """Send weekly summary"""
        subject = "📊 Your Weekly Summary - VORTEX Shield"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .stat {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: #0ea5e9; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Weekly Summary</h1>
                    <p>Week of {summary_data.get('week', 'Current Week')}</p>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>Here's your weekly insurance summary:</p>
                    
                    <div class="stat">
                        <div>Claims Filed</div>
                        <div class="stat-value">{summary_data.get('claims_filed', 0)}</div>
                    </div>
                    
                    <div class="stat">
                        <div>Total Protected</div>
                        <div class="stat-value">₹{summary_data.get('total_protected', 0):,.2f}</div>
                    </div>
                    
                    <div class="stat">
                        <div>Trust Score</div>
                        <div class="stat-value">{summary_data.get('trust_score', 0.85):.2f}</div>
                    </div>
                    
                    <p style="margin-top: 30px;">Your coverage is active and protecting your income 24/7.</p>
                </div>
                <div class="footer">
                    <p>© 2024 VORTEX Shield 2.0 | Built by Team VORTEX</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)

email_service = EmailService()
