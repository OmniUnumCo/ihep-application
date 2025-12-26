# IHEP Proposal Email Sender

## Quick Start - Send Your Proposals in 5 Minutes

### Prerequisites

```bash
# Install Python if not already installed
python3 --version  # Should be 3.8+

# No additional packages needed - uses Python standard library only!
```

### Setup (2 minutes)

#### Option 1: Gmail (Recommended - Easiest)

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "IHEP Proposal Sender"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

3. **Edit send_proposals.py**
   ```python
   EMAIL_CONFIG = EmailConfig(
       smtp_host="smtp.gmail.com",
       smtp_port=587,
       smtp_user="jason@yourdomain.com",  # Your Gmail address
       smtp_password="abcd efgh ijkl mnop",  # Your App Password (no spaces)
       from_email="jason@yourdomain.com",
       from_name="Jason Jarmacz - IHEP",
       use_tls=True
   )
   ```

#### Option 2: Office 365

```python
EMAIL_CONFIG = EmailConfig(
    smtp_host="smtp.office365.com",
    smtp_port=587,
    smtp_user="jason@yourdomain.com",  # Your Office 365 email
    smtp_password="your-password",      # Your Office 365 password
    from_email="jason@yourdomain.com",
    from_name="Jason Jarmacz - IHEP",
    use_tls=True
)
```

#### Option 3: SendGrid (For High Volume)

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Create API key in Settings > API Keys
3. Configure:

```python
EMAIL_CONFIG = EmailConfig(
    smtp_host="smtp.sendgrid.net",
    smtp_port=587,
    smtp_user="apikey",  # Literally the word "apikey"
    smtp_password="<YOUR_SENDGRID_API_KEY>",
    from_email="jason@yourdomain.com",
    from_name="Jason Jarmacz - IHEP",
    use_tls=True
)
```

### Configure Recipients (3 minutes)

Edit the `PROPOSALS` list in `send_proposals.py`:

```python
PROPOSALS = [
    # DOL WIOA Grant
    Proposal(
        recipient_email="grants@dol.gov",  # CHANGE THIS
        recipient_name="Grants Officer",   # CHANGE THIS
        organization="U.S. Department of Labor",
        proposal_type="grant",
        file_path=str(DOCS_DIR / "DOL WIOA WORKFORCE DEVELOPMENT PROPOSAL.docx"),
        subject="IHEP Workforce Development Grant Proposal",
        custom_message="..."
    ),

    # Add more proposals as needed
]
```

### Send Proposals

```bash
cd /Users/nexus1/Documents/ihep-app/ihep/proposal-mailer
python3 send_proposals.py
```

**Menu Options:**
1. **Preview emails** - See what will be sent
2. **Send test email** - Send to yourself first (RECOMMENDED)
3. **Send all proposals** - Send to actual recipients
4. **Exit**

### Recommended Workflow

1. **Test First** - Select option 2 to send a test email to yourself
2. **Verify** - Check your inbox, verify formatting and attachment
3. **Preview** - Select option 1 to review all emails
4. **Send** - Select option 3 to send all proposals

---

## Features

✅ **Professional Email Templates**
- HTML formatted with IHEP branding
- Customized by proposal type (grant/investor/partnership)
- Automatic signatures

✅ **Attachment Support**
- PDF and DOCX files
- Multiple attachments per email
- Automatic encoding

✅ **Error Handling**
- File verification before sending
- Retry logic for failures
- Detailed error messages

✅ **Logging**
- JSON log of all sent emails
- Timestamps and status tracking
- Error details for debugging

✅ **Security**
- TLS encryption
- No hardcoded passwords in code
- App Password support (Gmail)

---

## Current Proposals Ready to Send

Your proposal files are located in:
`/Users/nexus1/Documents/ihep-app/ihep/docs/`

**Grant Proposals:**
1. `DOL WIOA WORKFORCE DEVELOPMENT PROPOSAL.docx`
2. `FORD FOUNDATION - ECONOMIC JUSTICE INITIATIVE.docx`
3. `IHEP_NIH_SBIR_Phase_I_Proposal.docx`

**Investor Proposals:**
4. `investor proposal overview fixed.docx`

**Supporting Documentation:**
- `IHEP_GRANT_APPLICATIONS_FOR_WORKFORCE_DEVELOPMENT_FUNDING.md`
- `IHEP_PARTNERSHIP_MATERIALS.md`
- `IHEP_PARTNERSHIP_OUTREACH_MATERIALS.md`

---

## Troubleshooting

### "Authentication failed"

**Gmail:**
- Make sure you're using an App Password (not your regular password)
- App Password must be 16 characters with no spaces
- 2-Factor Authentication must be enabled

**Office 365:**
- Check if SMTP is enabled in admin settings
- Verify username is full email address

### "File not found"

```bash
# Verify file exists
ls -lh /Users/nexus1/Documents/ihep-app/ihep/docs/*.docx
```

If files are in a different location, update `DOCS_DIR` in `send_proposals.py`

### "Connection refused"

- Check internet connection
- Verify SMTP host and port
- Check if firewall is blocking port 587

### "Attachment too large"

Most SMTP servers limit attachment size to 25MB. If your proposal is larger:
1. Compress PDF: Preview > File > Export as PDF > Reduce File Size
2. Use a file sharing service and include link in email

---

## Email Limits

**Gmail:**
- 500 emails/day (personal account)
- 2000 emails/day (Google Workspace)
- 25MB per email

**SendGrid:**
- Free tier: 100 emails/day
- Paid: Unlimited with plan

**Office 365:**
- 10,000 emails/day
- 30 emails/minute

---

## Security Best Practices

1. **Never commit credentials to Git**
   ```bash
   # .gitignore already includes:
   *.env
   *config*.py
   ```

2. **Use App Passwords** (Gmail)
   - More secure than main password
   - Can be revoked independently

3. **Use Environment Variables** (Optional)
   ```bash
   export SMTP_PASSWORD="your-password"
   ```

   Then in code:
   ```python
   import os
   smtp_password=os.environ.get('SMTP_PASSWORD')
   ```

---

## Advanced: RabbitMQ Queue (Future Enhancement)

For high-volume sending or retry logic, we can add RabbitMQ:

```bash
# Install RabbitMQ
brew install rabbitmq
brew services start rabbitmq

# Install Python client
pip install pika

# Use queue-based sender (see email_queue.py)
```

This allows:
- Asynchronous sending
- Automatic retries
- Rate limiting
- Priority queues
- Delivery confirmations

**For now, direct SMTP is faster and simpler for your immediate needs.**

---

## Support

**Quick Help:**
```bash
# Test SMTP connection
python3 -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls(); print('Connection OK')"

# Check file sizes
du -h /Users/nexus1/Documents/ihep-app/ihep/docs/*.{docx,pdf}
```

**Contact:**
- Technical Issues: Check logs in `email_send_log_*.json`
- Gmail Setup: https://support.google.com/accounts/answer/185833
- SendGrid Support: https://docs.sendgrid.com/

---

**Last Updated:** 2025-12-17
**Version:** 1.0
**Status:** Production Ready
