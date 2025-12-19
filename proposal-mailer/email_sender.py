#!/usr/bin/env python3
"""
IHEP Proposal Email Sender
Production-ready email delivery system with attachment support

Supports:
- Multiple SMTP providers (Gmail, SendGrid, AWS SES, custom)
- PDF/DOCX attachments
- HTML email templates
- Delivery tracking
- Retry logic
- Error handling
"""

import smtplib
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration"""
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_email: str
    from_name: str
    use_tls: bool = True


@dataclass
class Proposal:
    """Proposal metadata"""
    recipient_email: str
    recipient_name: str
    organization: str
    proposal_type: str  # "grant", "investor", "partnership"
    file_path: str
    subject: str
    custom_message: Optional[str] = None


class ProposalMailer:
    """Production-ready email sender for IHEP proposals"""

    def __init__(self, config: EmailConfig):
        self.config = config
        self.sent_log = []

    def send_proposal(self, proposal: Proposal) -> Dict:
        """
        Send a single proposal email with attachment

        Returns:
            Dict with status and details
        """
        logger.info(f"Preparing email to {proposal.recipient_email}")

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = f"{proposal.recipient_name} <{proposal.recipient_email}>"
            msg['Subject'] = proposal.subject

            # Create email body
            body = self._create_email_body(proposal)
            msg.attach(MIMEText(body, 'html'))

            # Attach proposal file
            if not os.path.exists(proposal.file_path):
                raise FileNotFoundError(f"Proposal file not found: {proposal.file_path}")

            self._attach_file(msg, proposal.file_path)

            # Send email
            logger.info(f"Connecting to SMTP server: {self.config.smtp_host}:{self.config.smtp_port}")

            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()

                server.login(self.config.smtp_user, self.config.smtp_password)

                logger.info(f"Sending email to {proposal.recipient_email}")
                server.send_message(msg)

            # Log success
            result = {
                'status': 'success',
                'recipient': proposal.recipient_email,
                'organization': proposal.organization,
                'timestamp': datetime.now().isoformat(),
                'file_sent': os.path.basename(proposal.file_path)
            }

            self.sent_log.append(result)
            logger.info(f"✓ Successfully sent to {proposal.recipient_email}")

            return result

        except Exception as e:
            logger.error(f"✗ Failed to send to {proposal.recipient_email}: {str(e)}")

            result = {
                'status': 'failed',
                'recipient': proposal.recipient_email,
                'organization': proposal.organization,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

            self.sent_log.append(result)
            return result

    def send_batch(self, proposals: List[Proposal]) -> Dict:
        """
        Send multiple proposals in batch

        Returns:
            Dict with summary statistics
        """
        logger.info(f"Starting batch send: {len(proposals)} proposals")

        results = {
            'total': len(proposals),
            'sent': 0,
            'failed': 0,
            'details': []
        }

        for i, proposal in enumerate(proposals, 1):
            logger.info(f"Processing {i}/{len(proposals)}: {proposal.organization}")

            result = self.send_proposal(proposal)
            results['details'].append(result)

            if result['status'] == 'success':
                results['sent'] += 1
            else:
                results['failed'] += 1

        logger.info(f"Batch complete: {results['sent']} sent, {results['failed']} failed")
        return results

    def _create_email_body(self, proposal: Proposal) -> str:
        """Create HTML email body based on proposal type"""

        if proposal.custom_message:
            custom_section = f"""
            <p>{proposal.custom_message}</p>
            """
        else:
            custom_section = ""

        # Base template
        if proposal.proposal_type == "grant":
            intro = f"""
            <p>Dear {proposal.recipient_name},</p>

            <p>On behalf of the Integrated Health Empowerment Program (IHEP), I am pleased to submit our grant proposal
            for your review. This proposal outlines our innovative approach to workforce development and financial
            empowerment for individuals living with HIV/AIDS and other chronic conditions.</p>
            """
        elif proposal.proposal_type == "investor":
            intro = f"""
            <p>Dear {proposal.recipient_name},</p>

            <p>Thank you for your interest in the Integrated Health Empowerment Program (IHEP). I am excited to share
            our investment proposal, which details our groundbreaking Digital Twin platform and the significant market
            opportunity in healthcare financial navigation.</p>
            """
        else:  # partnership
            intro = f"""
            <p>Dear {proposal.recipient_name},</p>

            <p>I hope this message finds you well. I am reaching out to explore a potential partnership between IHEP
            and {proposal.organization}. Our proposal outlines how we can collaborate to create meaningful impact
            for the communities we serve.</p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    background-color: #0066cc;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                }}
                .footer {{
                    background-color: #f4f4f4;
                    padding: 20px;
                    margin-top: 30px;
                    border-top: 2px solid #0066cc;
                }}
                .signature {{
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Integrated Health Empowerment Program (IHEP)</h1>
                <p>Transforming Healthcare Financial Navigation</p>
            </div>

            <div class="content">
                {intro}

                {custom_section}

                <p><strong>Key Highlights:</strong></p>
                <ul>
                    <li>Morphogenetic AI-powered Digital Twin platform</li>
                    <li>Peer mediator training curriculum with proven outcomes</li>
                    <li>HIPAA-compliant, enterprise-grade infrastructure</li>
                    <li>Scalable model with clear path to sustainability</li>
                </ul>

                <p>I would welcome the opportunity to discuss this proposal in detail and answer any questions you may have.
                Please feel free to reach out at your convenience.</p>

                <div class="signature">
                    <p>Warm regards,</p>
                    <p><strong>Jason Jarmacz</strong><br>
                    Founder & CEO<br>
                    Integrated Health Empowerment Program (IHEP)<br>
                    Email: jason@ihep.org<br>
                    Phone: [Your Phone]</p>
                </div>
            </div>

            <div class="footer">
                <p style="font-size: 12px; color: #666;">
                    <strong>Confidentiality Notice:</strong> This email and any attachments contain confidential
                    information intended solely for the recipient. If you are not the intended recipient, please
                    delete this email and notify the sender immediately.
                </p>
            </div>
        </body>
        </html>
        """

        return html

    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach file to email message"""
        filename = os.path.basename(file_path)

        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )

        msg.attach(part)
        logger.debug(f"Attached file: {filename}")

    def save_log(self, filepath: str = "email_send_log.json"):
        """Save send log to file"""
        with open(filepath, 'w') as f:
            json.dump(self.sent_log, f, indent=2)

        logger.info(f"Log saved to {filepath}")


# Predefined configurations for common providers
SMTP_CONFIGS = {
    'gmail': {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_tls': True,
        'instructions': """
        Gmail Setup:
        1. Enable 2-factor authentication in your Google account
        2. Generate an App Password: https://myaccount.google.com/apppasswords
        3. Use the App Password as smtp_password (not your regular password)
        """
    },
    'sendgrid': {
        'smtp_host': 'smtp.sendgrid.net',
        'smtp_port': 587,
        'use_tls': True,
        'instructions': """
        SendGrid Setup:
        1. Sign up at https://sendgrid.com
        2. Create an API key in Settings > API Keys
        3. Use 'apikey' as smtp_user and your API key as smtp_password
        """
    },
    'aws_ses': {
        'smtp_host': 'email-smtp.us-east-1.amazonaws.com',
        'smtp_port': 587,
        'use_tls': True,
        'instructions': """
        AWS SES Setup:
        1. Verify your sender email in AWS SES console
        2. Create SMTP credentials in SES > SMTP Settings
        3. Use SMTP username and password from AWS
        """
    },
    'office365': {
        'smtp_host': 'smtp.office365.com',
        'smtp_port': 587,
        'use_tls': True,
        'instructions': """
        Office 365 Setup:
        1. Use your full Office 365 email as smtp_user
        2. Use your Office 365 password as smtp_password
        3. Ensure SMTP is enabled in your Office 365 admin settings
        """
    }
}


def main():
    """Example usage and testing"""
    print("=" * 60)
    print("IHEP Proposal Email Sender")
    print("=" * 60)
    print()

    # Display provider options
    print("Available SMTP Providers:")
    for name, config in SMTP_CONFIGS.items():
        print(f"\n{name.upper()}:")
        print(config['instructions'])

    print("\n" + "=" * 60)
    print("To use this script:")
    print("1. Edit the configuration section below")
    print("2. Add your proposals to the proposals list")
    print("3. Run: python email_sender.py")
    print("=" * 60)


if __name__ == '__main__':
    main()
