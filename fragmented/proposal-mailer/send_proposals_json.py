#!/usr/bin/env python3
"""
IHEP Proposal Sender - JSON Configuration Version
Loads configuration from config.json
"""

import json
import os
from pathlib import Path
from email_sender import EmailConfig, Proposal, ProposalMailer

# ==============================================================================
# LOAD CONFIGURATION FROM JSON
# ==============================================================================

def load_config(config_file: str = "config.json"):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        config_data = json.load(f)

    # Parse email config
    email_cfg = config_data['email_config']
    email_config = EmailConfig(
        smtp_host=email_cfg['smtp_host'],
        smtp_port=email_cfg['smtp_port'],
        smtp_user=email_cfg['smtp_user'],
        smtp_password=email_cfg['smtp_password'],
        from_email=email_cfg['from_email'],
        from_name=email_cfg['from_name'],
        use_tls=email_cfg['use_tls']
    )

    # Parse proposals
    docs_dir = Path("/Users/nexus1/Documents/ihep-app/ihep/docs")
    proposals = []

    for prop_data in config_data['proposals']:
        proposal = Proposal(
            recipient_email=prop_data['recipient_email'],
            recipient_name=prop_data['recipient_name'],
            organization=prop_data['organization'],
            proposal_type=prop_data['proposal_type'],
            file_path=str(docs_dir / prop_data['file_path']),
            subject=prop_data['subject'],
            custom_message=prop_data.get('custom_message')
        )
        proposals.append(proposal)

    return email_config, proposals


# ==============================================================================
# FUNCTIONS
# ==============================================================================

def verify_files(proposals):
    """Verify all proposal files exist"""
    print("Verifying proposal files...")
    missing = []

    for proposal in proposals:
        if not os.path.exists(proposal.file_path):
            missing.append(proposal.file_path)
            print(f"  ✗ Missing: {proposal.file_path}")
        else:
            size_mb = os.path.getsize(proposal.file_path) / (1024 * 1024)
            print(f"  ✓ Found: {os.path.basename(proposal.file_path)} ({size_mb:.2f} MB)")

    if missing:
        print(f"\n⚠️  Warning: {len(missing)} file(s) not found")
        print("Please check file paths and try again.")
        return False

    print(f"\n✓ All {len(proposals)} proposal files found")
    return True


def preview_emails(proposals):
    """Show what will be sent"""
    print("\n" + "="*60)
    print("EMAIL PREVIEW")
    print("="*60)

    for i, proposal in enumerate(proposals, 1):
        print(f"\nEmail {i}:")
        print(f"  To:           {proposal.recipient_name} <{proposal.recipient_email}>")
        print(f"  Organization: {proposal.organization}")
        print(f"  Subject:      {proposal.subject}")
        print(f"  Attachment:   {os.path.basename(proposal.file_path)}")
        print(f"  Type:         {proposal.proposal_type}")


def confirm_send(email_config, proposals):
    """Get user confirmation"""
    print("\n" + "="*60)
    print("READY TO SEND")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  SMTP Server:  {email_config.smtp_host}:{email_config.smtp_port}")
    print(f"  From:         {email_config.from_name} <{email_config.from_email}>")
    print(f"  Proposals:    {len(proposals)}")

    print("\n⚠️  WARNING: This will send real emails to the recipients listed above.")
    response = input("\nType 'SEND' to proceed or anything else to cancel: ")

    return response.strip().upper() == 'SEND'


def send_test_email(mailer, proposals, email_config):
    """Send a test email to yourself"""
    print("\n" + "="*60)
    print("TEST EMAIL")
    print("="*60)

    test_proposal = Proposal(
        recipient_email=email_config.from_email,
        recipient_name="Test Recipient",
        organization="Test Organization",
        proposal_type="grant",
        file_path=proposals[0].file_path if proposals else "",
        subject="IHEP Email System Test - Please Ignore",
        custom_message="This is a test email to verify the email system is working correctly."
    )

    print(f"\nSending test email to {email_config.from_email}...")

    result = mailer.send_proposal(test_proposal)

    if result['status'] == 'success':
        print("\n✓ Test email sent successfully!")
        print("Please check your inbox to verify formatting and attachments.")
        return True
    else:
        print(f"\n✗ Test email failed: {result.get('error')}")
        return False


def send_individual_email(mailer, proposals):
    """Send a single selected proposal"""
    print("\n" + "="*60)
    print("SELECT PROPOSAL TO SEND")
    print("="*60)

    for i, proposal in enumerate(proposals, 1):
        print(f"\n{i}. {proposal.organization}")
        print(f"   To:      {proposal.recipient_name} <{proposal.recipient_email}>")
        print(f"   Subject: {proposal.subject}")
        print(f"   File:    {os.path.basename(proposal.file_path)}")

    print(f"\n{len(proposals) + 1}. Cancel")

    choice = input(f"\nSelect proposal to send (1-{len(proposals) + 1}): ").strip()

    try:
        choice_num = int(choice)
        if choice_num == len(proposals) + 1:
            print("\nCancelled.")
            return

        if 1 <= choice_num <= len(proposals):
            proposal = proposals[choice_num - 1]

            print("\n" + "="*60)
            print("CONFIRM SEND")
            print("="*60)
            print(f"\nYou are about to send:")
            print(f"  To:           {proposal.recipient_name} <{proposal.recipient_email}>")
            print(f"  Organization: {proposal.organization}")
            print(f"  Subject:      {proposal.subject}")
            print(f"  Attachment:   {os.path.basename(proposal.file_path)}")

            confirm = input("\nType 'SEND' to proceed or anything else to cancel: ").strip().upper()

            if confirm == 'SEND':
                print("\nSending...")
                result = mailer.send_proposal(proposal)

                if result['status'] == 'success':
                    print(f"\n✓ Successfully sent to {proposal.recipient_email}")

                    # Save log
                    log_file = f"email_send_log_{os.getpid()}.json"
                    mailer.save_log(log_file)
                    print(f"Log saved to: {log_file}")
                else:
                    print(f"\n✗ Failed to send: {result.get('error')}")
            else:
                print("\nCancelled.")
        else:
            print("\n⚠️  Invalid selection.")

    except ValueError:
        print("\n⚠️  Invalid input. Please enter a number.")


def main():
    """Main execution"""
    print("="*60)
    print("IHEP PROPOSAL EMAIL SENDER (JSON Config)")
    print("="*60)
    print()

    # Load configuration
    try:
        email_config, proposals = load_config()
        print("✓ Configuration loaded from config.json")
    except FileNotFoundError:
        print("⚠️  ERROR: config.json not found")
        print("Please ensure config.json exists in the same directory.")
        return
    except json.JSONDecodeError as e:
        print(f"⚠️  ERROR: Invalid JSON in config.json")
        print(f"Details: {str(e)}")
        return
    except Exception as e:
        print(f"⚠️  ERROR: Failed to load configuration")
        print(f"Details: {str(e)}")
        return

    # Verify files exist
    if not verify_files(proposals):
        return

    # Create mailer
    mailer = ProposalMailer(email_config)

    # Menu
    while True:
        print("\n" + "="*60)
        print("OPTIONS")
        print("="*60)
        print("1. Preview all emails")
        print("2. Send test email (to yourself)")
        print("3. Send ONE proposal (select from list)")
        print("4. Send ALL proposals")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == '1':
            preview_emails(proposals)

        elif choice == '2':
            if send_test_email(mailer, proposals, email_config):
                print("\nReview the test email before sending to actual recipients.")

        elif choice == '3':
            send_individual_email(mailer, proposals)

        elif choice == '4':
            preview_emails(proposals)
            if confirm_send(email_config, proposals):
                print("\n" + "="*60)
                print("SENDING EMAILS")
                print("="*60)

                results = mailer.send_batch(proposals)

                print("\n" + "="*60)
                print("RESULTS")
                print("="*60)
                print(f"\nTotal:   {results['total']}")
                print(f"Sent:    {results['sent']} ✓")
                print(f"Failed:  {results['failed']} ✗")

                # Save log
                log_file = f"email_send_log_{os.getpid()}.json"
                mailer.save_log(log_file)
                print(f"\nLog saved to: {log_file}")

                # Show failures if any
                if results['failed'] > 0:
                    print("\nFailed emails:")
                    for detail in results['details']:
                        if detail['status'] == 'failed':
                            print(f"  ✗ {detail['recipient']}: {detail['error']}")

                break
            else:
                print("\nSend cancelled.")

        elif choice == '5':
            print("\nExiting.")
            break

        else:
            print("\n⚠️  Invalid option. Please select 1-5.")


if __name__ == '__main__':
    main()
