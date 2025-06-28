import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_gmail(sender_email, app_password, recipient_email, subject, body, attachment_filepath=None):
    """
    Sends an email through Gmail using SMTP with SSL.

    Args:
        sender_email (str): The sender's Gmail address.
        app_password (str): The Gmail App Password for the sender's account.
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The HTML or plain text body of the email.
        attachment_filepath (str, optional): Path to the file to attach. Defaults to None.

    Returns:
        tuple: (bool, str) indicating success status and a message.
               e.g., (True, "Email sent successfully!") or (False, "Error message")
    """
    if not all([sender_email, app_password, recipient_email, subject, body]):
        return False, "Missing required email parameters (sender, password, recipient, subject, or body)."

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Attach the body (as HTML, can be changed to plain if needed)
    message.attach(MIMEText(body, "html")) # Assuming body might contain HTML, use "plain" for plain text

    if attachment_filepath:
        if not os.path.exists(attachment_filepath):
            return False, f"Attachment file not found: {attachment_filepath}"
        try:
            with open(attachment_filepath, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=os.path.basename(attachment_filepath))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_filepath)}"'
            message.attach(part)
        except Exception as e:
            return False, f"Error attaching file: {e}"

    # SMTP server configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # For STARTTLS

    try:
        # Create a secure SSL context
        context = ssl.create_default_context()

        # Connect to the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted

        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail login failed. Check email address and App Password. Ensure 2FA is enabled and an App Password is used."
    except smtplib.SMTPServerDisconnected:
        return False, "Server disconnected unexpectedly. Please try again."
    except smtplib.SMTPConnectError:
        return False, f"Could not connect to Gmail SMTP server ({smtp_server}:{smtp_port}). Check network connection."
    except ssl.SSLError as e:
        return False, f"SSL error during connection: {e}. Your network might be intercepting traffic or Gmail's certificate is untrusted."
    except Exception as e:
        return False, f"An unexpected error occurred while sending email: {e}"

if __name__ == '__main__':
    # --- IMPORTANT ---
    # To test this, you MUST:
    # 1. Replace placeholders with your actual Gmail, App Password, and a recipient.
    # 2. Ensure the sender Gmail account has 2-Step Verification enabled.
    # 3. Generate an App Password for this application in the sender's Google Account settings.
    #    (Google Account -> Security -> 2-Step Verification -> App passwords)
    # 4. Create a dummy file e.g., 'test_attachment.txt' or 'sample_report.pdf' in the same directory.

    print("Testing email_sender.py...")

    # --- Configuration ---
    # !!! REPLACE THESE WITH YOUR ACTUAL CREDENTIALS AND A TEST RECIPIENT FOR TESTING !!!
    SENDER_GMAIL = "your_email@gmail.com"  # Your Gmail address
    SENDER_APP_PASSWORD = "your_app_password"    # Your generated App Password
    RECIPIENT_TEST_EMAIL = "recipient_test@example.com" # A test recipient email

    # Create a dummy attachment for testing
    dummy_attachment_name = "test_report_for_email.pdf"
    try:
        with open(dummy_attachment_name, "w") as f:
            f.write("This is a test PDF content for email attachment.")
        print(f"Created dummy attachment: {dummy_attachment_name}")
    except Exception as e:
        print(f"Could not create dummy attachment: {e}")
        # dummy_attachment_name = None # Proceed without attachment if creation fails

    if SENDER_GMAIL == "your_email@gmail.com" or SENDER_APP_PASSWORD == "your_app_password":
        print("\nWARNING: Please update SENDER_GMAIL and SENDER_APP_PASSWORD in email_sender.py to test.")
    else:
        print(f"\nAttempting to send test email from {SENDER_GMAIL} to {RECIPIENT_TEST_EMAIL}...")

        subject_test = "Test Email from Report Generator Tool"
        body_test = """
        <html>
        <body>
            <p>Hello,</p>
            <p>This is a <b>test email</b> sent from the Python Report Generator application.</p>
            <p>If you received this, the <code>send_gmail</code> function in <code>email_sender.py</code> is working correctly.</p>
            <p>An attachment should be included if '{dummy_attachment_name}' was created.</p>
            <p>Regards,<br>Automated Test</p>
        </body>
        </html>
        """

        # Test 1: Send with attachment
        if os.path.exists(dummy_attachment_name):
            success, message = send_gmail(
                SENDER_GMAIL, SENDER_APP_PASSWORD, RECIPIENT_TEST_EMAIL,
                subject_test + " (With Attachment)", body_test, dummy_attachment_name
            )
            print(f"\nTest 1 (With Attachment) Result: Success={success}, Message='{message}'")
        else:
            print(f"\nTest 1 (With Attachment) SKIPPED: Dummy attachment '{dummy_attachment_name}' not found.")

        # Test 2: Send without attachment
        success_no_attach, message_no_attach = send_gmail(
            SENDER_GMAIL, SENDER_APP_PASSWORD, RECIPIENT_TEST_EMAIL,
            subject_test + " (No Attachment)", body_test.replace(f"'{dummy_attachment_name}' was created", "no attachment was specified")
        )
        print(f"\nTest 2 (No Attachment) Result: Success={success_no_attach}, Message='{message_no_attach}'")

        # Test 3: Failure case (e.g., wrong password)
        # Note: This will actually try to log in. For a true unit test, mocking would be better.
        print("\nTest 3 (Intentional Failure - Bad Password - if App Password is not 'badpassword'):")
        success_fail, message_fail = send_gmail(
            SENDER_GMAIL, "badpassword", RECIPIENT_TEST_EMAIL,
            "Test Email - Failure Test", "This email should not send."
        )
        print(f"Test 3 Result: Success={success_fail}, Message='{message_fail}'")

    # Clean up dummy attachment
    if os.path.exists(dummy_attachment_name):
        try:
            os.remove(dummy_attachment_name)
            print(f"\nCleaned up dummy attachment: {dummy_attachment_name}")
        except Exception as e:
            print(f"Error cleaning up dummy attachment: {e}")
