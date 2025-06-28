# Vulnerability Report Generator & Gmail Sender

This Python-based desktop tool helps automate the process of generating professional PDF vulnerability assessment reports and sending them to clients via Gmail. It accepts user input (manual, .txt, or .csv) for findings, creates a structured PDF, composes an email, and sends it securely using the user's Gmail account.

## Features

-   **Input Flexibility:** Accept findings via direct text paste, or by importing from `.txt` or `.csv` files.
-   **PDF Report Generation:** Creates a clean, structured PDF report including:
    -   Title Page (Domain, Date)
    -   Executive Summary
    -   Detailed Findings
    -   Risk Overview
    -   Recommendations (default list, can be overridden by input)
-   **Professional Email Composition:** Automatically drafts a polite email summarizing the findings and mentioning the attached report. The user can edit this email before sending.
-   **Secure Gmail Integration:** Sends emails using Gmail's SMTP server with `STARTTLS` encryption.
    -   Requires user's Gmail address and an **App Password**.
    -   Credentials are used for sending only and are **not stored** by the application.
-   **User-Friendly GUI:** Simple interface built with Tkinter.
-   **Legal Compliance Focus:** Reminds users of the importance of complying with Gmail's policies and anti-spam laws.

## Dependencies

The tool relies on the following Python libraries:

-   **fpdf2:** For PDF generation.
    -   `pip install fpdf2`

(Tkinter is part of the Python standard library, so no separate installation is needed for it.)

## Installation

1.  **Clone the repository or download the source files.**
    ```bash
    # Example if it were a git repo
    # git clone <repository_url>
    # cd <repository_directory>
    ```
2.  **Install the required dependency:**
    Open a terminal or command prompt and run:
    ```bash
    pip install fpdf2
    ```

## Running the Application

1.  Navigate to the directory where you saved the application files (`main.py`, `pdf_generator.py`, `email_generator.py`, `email_sender.py`).
2.  Run the main application file using Python:
    ```bash
    python main.py
    ```
    This will launch the GUI.

## Setting Up Gmail for Use with This Tool

To send emails through your Gmail account, you **MUST** configure your account for secure access via applications:

1.  **Enable 2-Step Verification (2FA):**
    -   Go to your Google Account settings: [https://myaccount.google.com/](https://myaccount.google.com/)
    -   Navigate to the "Security" tab.
    -   Under "Signing in to Google," click on "2-Step Verification" and follow the on-screen instructions to enable it if it's not already active. This is mandatory for generating App Passwords.

2.  **Generate an App Password:**
    -   Once 2FA is enabled, go back to the "Security" tab in your Google Account settings.
    -   Find the "Signing in to Google" section again, and click on "App passwords". You might be asked to sign in.
    -   If you don't see "App passwords", it might be because:
        -   2-Step Verification is not set up for your account.
        -   2-Step Verification is only set up for security keys.
        -   Your account is through work, school, or other organization that manages these settings.
        -   You’ve turned on Advanced Protection for your account.
    -   Under "Select app and device for which you want to generate the app password":
        -   For "Select app," choose "Mail."
        -   For "Select device," choose "Windows Computer" (or "Other (Custom name)" and give it a name like "Python Report Tool").
    -   Click "Generate."
    -   A 16-character password will be displayed (e.g., `xxxx xxxx xxxx xxxx`). **This is your App Password.**
    -   **Copy this password immediately.** Do not include the spaces. You will use this password in the "Gmail App Password" field in the tool.
    -   Click "Done."

    **Important:**
    -   Use this generated App Password in the application, NOT your regular Gmail password.
    -   Each App Password is used once to sign in, but you don't need to memorize it as long as the application has it (though this tool doesn't store it between sessions).

## Usage Instructions

1.  **Input Findings:**
    -   **Paste:** Copy your findings and click "Paste Findings."
    -   **Import File:** Click "Import File (.txt, .csv)" to load findings from a file.
        -   `.txt` format: Each line as `Key: Value` (e.g., `Domain: example.com`).
        -   `.csv` format: Each line as `Key,Value` (e.g., `Domain,example.com`).
2.  **Review Parsed Data:** The tool will attempt to parse the input. The email subject and body will be auto-populated based on this data.
3.  **Enter Your Name:** Fill in the "Your Name (for email sign-off)" field. This will be used in the email signature.
4.  **Generate PDF Report:**
    -   Click "Generate PDF Report."
    -   You will be prompted to choose a location and name for the PDF file.
    -   Upon successful generation, the email subject and body will be updated/populated again.
5.  **Prepare Email:**
    -   Enter the "Recipient Email."
    -   Enter "Your Gmail Address."
    -   Enter the "Gmail App Password" you generated.
    -   Review and **edit the Email Subject and Body** as needed.
6.  **Agree to Terms:**
    -   Read the "Important" section regarding Gmail usage.
    -   Check the box: "I have read and agree to the terms and responsible usage guidelines mentioned above."
7.  **Send Email:**
    -   Click "Send Email via Gmail." The tool will attempt to send the email with the PDF attached.
    -   You will receive feedback on whether the email was sent successfully or if an error occurred.

## Responsible Usage

-   **Consent:** Only send reports to clients who have explicitly consented to receive them.
-   **Compliance:** You are responsible for adhering to Gmail's Terms of Service, Acceptable Use Policy, and all relevant anti-spam legislation (e.g., CAN-SPAM, GDPR).
-   **Security:** Keep your App Password secure. If you suspect it's compromised, revoke it from your Google Account settings and generate a new one.
-   **No Storage:** This tool does **not** store your Gmail address or App Password after it is closed. You need to enter them each time you use the email sending feature.

This tool is intended for legitimate professional communication. Misuse for spamming or unauthorized activities is strictly prohibited.
