#!/usr/bin/env python3
"""
IHEP Proposal Sender - Ready to Execute
Configure and send your grant/investor proposals
"""

import os
from pathlib import Path
from email_sender import EmailConfig, Proposal, ProposalMailer

# ==============================================================================
# CONFIGURATION - EDIT THIS SECTION
# ==============================================================================

# STEP 1: Choose your email provider and enter credentials
EMAIL_PROVIDER = "gmail"  # Options: gmail, sendgrid, aws_ses, office365

EMAIL_CONFIG = EmailConfig(
    # Gmail settings (using App Password)
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="jason@trademomentumllc.com",  # CHANGE THIS
    smtp_password="yygq ltbm qnci nnmw",  # CHANGE THIS (16-character App Password)
    from_email="jason@trademomentumllc.com",  # CHANGE THIS
    from_name="Jason Jarmacz - IHEP Principal Investigator",
    use_tls=True
)

# STEP 2: Define your proposals
# Find proposal files in /Users/nexus1/Documents/ihep-app/ihep/docs/

DOCS_DIR = Path("/Users/nexus1/Documents/ihep-app/ihep/docs")

PROPOSALS = [
    # DOL WIOA Workforce Development Grant
    Proposal(
        recipient_email="workforce.grants@dol.gov",  # CHANGE TO ACTUAL CONTACT
        recipient_name="Grants Management Specialist",
        organization="U.S. Department of Labor - WIOA Program",
        proposal_type="grant",
        file_path=str(DOCS_DIR / "DOL WIOA WORKFORCE DEVELOPMENT PROPOSAL.docx"),
        subject="IHEP Workforce Development Grant Proposal - WIOA Program",
        custom_message="""
        This proposal outlines our peer mediator training program that directly aligns with
        WIOA workforce development objectives. We are requesting funding to train 100 peer
        mediators in the first cohort, with a clear pathway to certification and employment.
        """
    ),

    # Ford Foundation - Economic Justice Initiative
    Proposal(
        recipient_email="economic.justice@fordfoundation.org",  # CHANGE TO ACTUAL CONTACT
        recipient_name="Program Officer",
        organization="Ford Foundation - Economic Justice Initiative",
        proposal_type="grant",
        file_path=str(DOCS_DIR / "FORD FOUNDATION - ECONOMIC JUSTICE INITIATIVE.docx"),
        subject="IHEP Economic Empowerment Proposal - Ford Foundation",
        custom_message="""
        Our Digital Twin platform addresses systemic economic inequities faced by individuals
        living with HIV/AIDS. This proposal demonstrates how technology can create pathways
        to financial stability and economic justice for marginalized communities.
        """
    ),

    # NIH SBIR Phase I
    Proposal(
        recipient_email="sbir@nih.gov",  # CHANGE TO ACTUAL CONTACT
        recipient_name="SBIR Program Officer",
        organization="National Institutes of Health - SBIR Program",
        proposal_type="grant",
        file_path=str(DOCS_DIR / "IHEP_NIH_SBIR_Phase_I_Proposal.docx"),
        subject="IHEP NIH SBIR Phase I Application - Digital Health Innovation",
        custom_message="""
        This Phase I SBIR proposal presents our morphogenetic AI platform for healthcare
        financial navigation. We seek funding to validate our technical approach and
        demonstrate commercial feasibility.
        """
    ),

    # Google Ventures (GV) - Warm intro via Google Cloud partnership
    Proposal(
        recipient_email="proposals@gv.com",  # UPDATE with specific partner contact from Google
        recipient_name="Investment Partner",
        organization="Google Ventures (GV)",
        proposal_type="investor",
        file_path=str(DOCS_DIR / "investor proposal overview fixed.docx"),
        subject="IHEP Investment Opportunity - Digital Health Platform (Google Cloud Partner)",
        custom_message="""
        IHEP is a Google Cloud partner with a validated digital health platform addressing
        a $50B+ market opportunity. Our morphogenetic AI technology has been validated through
        our existing Google Cloud partnership, and we're seeking Series A funding to scale
        our peer mediator training program nationally.

        Key metrics: 98.5% production readiness, HIPAA compliant, 1000+ concurrent user capacity.

        I'd welcome the opportunity to discuss how IHEP aligns with GV's digital health portfolio.
        """
    ),

    # ADDITIONAL INVESTORS - Add specific contacts as you get them:
    # See INVESTOR_CONTACTS.md for target list

    # Proposal(
    #     recipient_email="bio@a16z.com",
    #     recipient_name="Partner Name",
    #     organization="Andreessen Horowitz - Bio + Health",
    #     proposal_type="investor",
    #     file_path=str(DOCS_DIR / "investor proposal overview fixed.docx"),
    #     subject="IHEP Series A Investment Opportunity",
    # ),

    # Partnership Proposals (add as needed)
    # Proposal(
    #     recipient_email="partnerships@organization.org",
    #     recipient_name="Partnership Director",
    #     organization="Partner Organization",
    #     proposal_type="partnership",
    #     file_path=str(DOCS_DIR / "IHEP_PARTNERSHIP_MATERIALS.md"),
    #     subject="IHEP Partnership Proposal",
    # ),
]

# ==============================================================================
# EXECUTION - NO CHANGES NEEDED BELOW THIS LINE
# ==============================================================================

def verify_files():
    """Verify all proposal files exist"""
    print("Verifying proposal files...")
    missing = []

    for proposal in PROPOSALS:
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

    print(f"\n✓ All {len(PROPOSALS)} proposal files found")
    return True


def preview_emails():
    """Show what will be sent"""
    print("\n" + "="*60)
    print("EMAIL PREVIEW")
    print("="*60)

    for i, proposal in enumerate(PROPOSALS, 1):
        print(f"\nEmail {i}:")
        print(f"  To:           {proposal.recipient_name} <{proposal.recipient_email}>")
        print(f"  Organization: {proposal.organization}")
        print(f"  Subject:      {proposal.subject}")
        print(f"  Attachment:   {os.path.basename(proposal.file_path)}")
        print(f"  Type:         {proposal.proposal_type}")


def confirm_send():
    """Get user confirmation"""
    print("\n" + "="*60)
    print("READY TO SEND")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Provider:     {EMAIL_PROVIDER}")
    print(f"  SMTP Server:  {EMAIL_CONFIG.smtp_host}:{EMAIL_CONFIG.smtp_port}")
    print(f"  From:         {EMAIL_CONFIG.from_name} <{EMAIL_CONFIG.from_email}>")
    print(f"  Proposals:    {len(PROPOSALS)}")

    print("\n⚠️  WARNING: This will send real emails to the recipients listed above.")
    response = input("\nType 'SEND' to proceed or anything else to cancel: ")

    return response.strip().upper() == 'SEND'


def send_test_email(mailer: ProposalMailer):
    """Send a test email to yourself"""
    print("\n" + "="*60)
    print("TEST EMAIL")
    print("="*60)

    test_proposal = Proposal(
        recipient_email=EMAIL_CONFIG.from_email,  # Send to yourself
        recipient_name="Test Recipient",
        organization="Test Organization",
        proposal_type="grant",
        file_path=PROPOSALS[0].file_path if PROPOSALS else "",
        subject="IHEP Email System Test - Please Ignore",
        custom_message="This is a test email to verify the email system is working correctly."
    )

    print(f"\nSending test email to {EMAIL_CONFIG.from_email}...")

    result = mailer.send_proposal(test_proposal)

    if result['status'] == 'success':
        print("\n✓ Test email sent successfully!")
        print("Please check your inbox to verify formatting and attachments.")
        return True
    else:
        print(f"\n✗ Test email failed: {result.get('error')}")
        return False


def send_individual_email(mailer: ProposalMailer):
    """Send a single selected proposal"""
    print("\n" + "="*60)
    print("SELECT PROPOSAL TO SEND")
    print("="*60)

    for i, proposal in enumerate(PROPOSALS, 1):
        print(f"\n{i}. {proposal.organization}")
        print(f"   To:      {proposal.recipient_name} <{proposal.recipient_email}>")
        print(f"   Subject: {proposal.subject}")
        print(f"   File:    {os.path.basename(proposal.file_path)}")

    print(f"\n{len(PROPOSALS) + 1}. Cancel")

    choice = input(f"\nSelect proposal to send (1-{len(PROPOSALS) + 1}): ").strip()

    try:
        choice_num = int(choice)
        if choice_num == len(PROPOSALS) + 1:
            print("\nCancelled.")
            return

        if 1 <= choice_num <= len(PROPOSALS):
            proposal = PROPOSALS[choice_num - 1]

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
    print("IHEP PROPOSAL EMAIL SENDER")
    print("="*60)
    print()

    # Check configuration
    if EMAIL_CONFIG.smtp_user == "your-email@gmail.com":
        print("⚠️  ERROR: Email configuration not set up")
        print("\nPlease edit send_proposals.py and configure:")
        print("  1. smtp_user (your email)")
        print("  2. smtp_password (your App Password)")
        print("  3. from_email (your email)")
        print("\nFor Gmail App Password setup:")
        print("  https://myaccount.google.com/apppasswords")
        return

    # Verify files exist
    if not verify_files():
        return

    # Create mailer
    mailer = ProposalMailer(EMAIL_CONFIG)

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
            preview_emails()

        elif choice == '2':
            if send_test_email(mailer):
                print("\nReview the test email before sending to actual recipients.")

        elif choice == '3':
            send_individual_email(mailer)

        elif choice == '4':
            preview_emails()
            if confirm_send():
                print("\n" + "="*60)
                print("SENDING EMAILS")
                print("="*60)

                results = mailer.send_batch(PROPOSALS)

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
