# Smart Email Outreach & Client Manager Tool

This Python-based desktop tool is designed for cybersecurity freelancers and consultants to manage client outreach, send targeted email campaigns, generate basic PDF reports, and track client interactions. It leverages Jinja2 for email templating, SQLite for local CRM functionalities, and Gmail (via App Password) for sending emails.

## Features

-   **Campaign Management:**
    -   Load recipients and campaign-specific data from CSV files.
    -   Send the same email (using a template) to multiple clients.
    -   Send different emails to different clients by specifying templates and custom notes in the CSV.
-   **Email Templating (Jinja2):**
    -   Utilizes Jinja2 for dynamic email content.
    -   Comes with pre-defined templates for common outreach scenarios (cold outreach, free scan follow-up, paid scan offer, upsell).
    -   Templates are easily customizable (HTML files in `templates/` directory).
    -   Automatic inclusion of a professional HTML signature (editable in `signature_handler.py`).
-   **Secure Gmail Integration:**
    -   Sends emails via Gmail's SMTP server using `STARTTLS`.
    -   Requires user's Gmail address and a **Gmail App Password** (2FA must be enabled).
    -   Credentials are used for sending only and are **not stored** by the application.
-   **PDF Report Generation & Attachment:**
    -   Generate basic vulnerability reports using `fpdf2`.
    -   Attach existing PDFs to emails on a per-recipient basis via CSV specification (`pdf_attachment_path` column).
    -   Automatically generate and attach new PDFs based on data provided in CSV columns (e.g., `pdf_domain`, `pdf_risk_summary`, `pdf_details`). Generated reports are saved in `generated_reports/`.
-   **Client Tracking/CRM (SQLite):**
    *   Stores client information (email, name, status, tags, notes) and interaction history in a local SQLite database (`clients.db`).
    *   Automatically logs sent emails, including the template used and subject.
    *   Client status can be updated (e.g., "Prospect", "Contacted", "Replied").
-   **User-Friendly GUI (Tkinter):**
    *   Interface for selecting templates, loading recipient CSVs, previewing/editing emails, and managing sending configurations.
    *   Lists campaign recipients and allows selection for individual preview.
-   **Legal Compliance Reminder:** UI includes reminders for responsible email practices and Gmail policy compliance.

## Dependencies

-   **Jinja2:** For email templating.
    -   `pip install Jinja2`
-   **fpdf2:** For PDF generation.
    -   `pip install fpdf2`

(Tkinter and SQLite3 are part of the Python standard library.)

## Installation

1.  **Clone the repository or download the source files.**
    Ensure all Python files (`main.py`, `template_manager.py`, `crm_manager.py`, `signature_handler.py`, `email_sender.py`, `pdf_generator.py`) and the `templates/` directory are in the same main directory.
2.  **Install required dependencies:**
    Open a terminal or command prompt and run:
    ```bash
    pip install Jinja2 fpdf2
    ```

## Running the Application

1.  Navigate to the directory containing `main.py`.
2.  Run the application:
    ```bash
    python main.py
    ```
    This will launch the GUI. The `clients.db` database and `generated_reports/` directory will be created in this same directory upon first use if they don't exist.

## Setting Up Gmail

(This is the same as the previous version - crucial for email sending)
To send emails through your Gmail account, you **MUST** configure your account for secure access:
1.  **Enable 2-Step Verification (2FA)** on your Google Account ([https://myaccount.google.com/security](https://myaccount.google.com/security)).
2.  **Generate an App Password:**
    -   In Google Account Security settings, go to "App passwords".
    -   Select app "Mail" and device "Windows Computer" (or "Other").
    -   Copy the generated 16-character App Password. Use this in the tool, not your regular Gmail password.

## Usage Instructions

1.  **Initial Setup:**
    *   Ensure the `templates/` directory contains your desired `.html` email templates.
    *   (Optional) Modify the signature in `signature_handler.py` if needed.
2.  **Launch the Application (`python main.py`).**
3.  **Configure Sending Settings (Right Pane):**
    *   Enter "Your Gmail Address".
    *   Enter the "Gmail App Password" you generated.
    *   Verify/edit "Your Name (Sign-off)".
    *   Check the "I agree to responsible usage..." box to enable sending buttons.
4.  **Prepare Campaign (Left Pane):**
    *   **Select Default Template:** Choose a base email template from the dropdown. This will be used if a template isn't specified for a recipient in the CSV.
    *   **Load Recipients from CSV:** Click "Load Recipients from CSV". Select your CSV file.
        *   **CSV Format:** The CSV file **must** have an `email` column header.
        *   **Recommended Columns:**
            *   `email` (required): Recipient's email address.
            *   `name` or `client_name`: Recipient's name (used in salutations like `Dear {{ client_name }}`).
            *   `domain`: Recipient's domain (used in template placeholders like `{{ domain }}`).
            *   `template`: Specify a template filename (e.g., `cold_outreach.html`) for this specific recipient, overriding the default selected in the UI.
            *   `custom_note`: A custom message or note to be inserted into the email template (using `{{ custom_note }}`).
            *   `pdf_attachment_path`: Full path to a pre-existing PDF to attach for this recipient.
            *   `pdf_domain`, `pdf_risk_summary`, `pdf_details`: Data to generate a new PDF for this recipient. If these are present, a PDF will be generated and attached (unless `pdf_attachment_path` is also present and valid, which takes precedence). Other `pdf_*` columns will also be passed to the PDF generator.
            *   Any other columns will be available in the template context (e.g., if CSV has `service_interest`, template can use `{{ service_interest }}`).
        *   Loaded recipients will appear in the "Campaign Recipients" list.
5.  **Preview and Edit Emails (Right Pane):**
    *   Select a recipient from the list in the left pane.
    *   The right pane will show the rendered email subject and body for that recipient using their specific data and template.
    *   You can edit the subject and body directly in the preview pane before sending.
    *   The PDF attachment status ("Attached (CSV): ...", "Attached (Generated): ...", or "No PDF...") will be shown.
6.  **Sending Emails:**
    *   **Send Previewed Email:** Sends the currently displayed (and possibly edited) email to the selected recipient only.
    *   **Send Full Campaign:** Iterates through all recipients in the loaded list and sends the emails.
        *   A confirmation dialog will appear.
        *   Emails are rendered using the data from the CSV for each recipient.
        *   A small delay is introduced between sends.
7.  **Client Tracking (CRM):**
    *   When an email is sent, the interaction is automatically logged in the `clients.db` SQLite database.
    *   Client records are added or updated (e.g., status set to "Contacted", `last_interaction_date` updated).
    *   (Currently, viewing/managing CRM data directly via the UI is limited; it's primarily for background logging. You can use an SQLite browser to view `clients.db`.)

## Email Templates

-   Templates are standard HTML files located in the `templates/` directory.
-   Use Jinja2 templating syntax (e.g., `{{ variable_name }}`, `{% if condition %}`, `{{ variable | default('fallback') }}`).
-   The following variables are generally available from the CSV or app:
    *   `client_name`, `domain`, `custom_note`.
    *   Any other columns from your CSV.
    *   `SIGNATURE_HTML | safe`: Renders the standard HTML signature.
-   **Example `cold_outreach.html` context variables:** `client_name`, `domain`, `custom_note`.

## PDF Generation Data in CSV

If you want the tool to generate a PDF for a recipient during a campaign, include these columns in your CSV:
-   `pdf_domain`: The domain for the PDF report (can be same as `domain`).
-   `pdf_risk_summary`: A summary of risks for the PDF.
-   `pdf_details`: Other details/findings for the PDF.
-   Other `pdf_*` columns (e.g., `pdf_ssl_status`) will be collected and passed to the PDF generator. The key used in `pdf_generator.py` will be the column name minus `pdf_` and capitalized (e.g. `pdf_ssl_status` -> `Ssl_status`).

If `pdf_attachment_path` is specified in the CSV and points to a valid existing PDF, that PDF will be used instead of generating a new one.

## Responsible Usage

-   **Consent:** Only send emails to individuals who have consented or for legitimate outreach purposes as permitted by applicable laws (e.g., CAN-SPAM, GDPR).
-   **Compliance:** You are responsible for adhering to Gmail's Terms of Service, Acceptable Use Policy, and all anti-spam legislation.
-   **Security:** Protect your Gmail App Password.
-   **No Storage of Credentials:** This tool does not store your Gmail address or App Password after it is closed.

This tool is intended for legitimate professional communication. Misuse is strictly prohibited.
