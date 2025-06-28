# Agent Instructions for Vulnerability Report Generator

This document provides guidance for AI agents maintaining or developing this Vulnerability Report Generator tool.

## Project Structure

The project consists of several Python modules:

-   **`main.py`**:
    -   The entry point of the application.
    -   Handles the Tkinter GUI, user interactions, and coordinates calls to other modules.
    -   Manages application state like parsed data and PDF filepath.
-   **`pdf_generator.py`**:
    -   Responsible for creating the PDF report.
    -   Uses the `fpdf2` library.
    -   Defines the structure and content of the PDF.
-   **`email_generator.py`**:
    -   Responsible for composing the subject and body of the email.
    -   Aims to create professional and informative email content based on the input findings.
-   **`email_sender.py`**:
    -   Handles the actual sending of the email via Gmail's SMTP server.
    -   Uses `smtplib` and `ssl` for secure communication (STARTTLS).
    -   Manages email formatting (MIME types) and attachments.
-   **`README.md`**: User-facing documentation.
-   **`AGENTS.md`**: This file.

## Key Libraries and Choices

-   **Tkinter (GUI):** Chosen for its inclusion in the Python standard library, ensuring ease of use and cross-platform compatibility without requiring users to install large external GUI frameworks. While not as feature-rich as Qt (PyQt/PySide) or Kivy, it's sufficient for this tool's simple interface.
-   **fpdf2 (PDF Generation):** Chosen because it's a pure Python library, generally lightweight, and capable of producing structured PDFs. Alternatives like ReportLab are more powerful but can be more complex for basic needs. `pdfkit` (a wkhtmltopdf wrapper) could be an option if HTML-to-PDF rendering was a primary goal, but `fpdf2` offers more direct control for this type of structured report.
-   **smtplib, ssl (Email Sending):** Standard Python libraries for SMTP communication, making them a natural choice for email functionality.
-   **No External Libraries for Input Parsing (beyond basic string methods):** The current input parsing for TXT/CSV is very basic. If more complex CSV structures or other structured data formats (like JSON, YAML) were to be supported, using libraries like `csv` (standard library) or `PyYAML`/`ruamel.yaml` (for YAML) would be advisable.

## Development Principles Followed

-   **Modularity:** Functionality is broken down into separate modules (PDF generation, email composition, email sending) to improve organization and maintainability.
-   **User Feedback:** The tool attempts to provide clear feedback to the user via the status bar and message dialogs for most operations and errors.
-   **Security for Email:** Emphasizes the use of Gmail App Passwords and clarifies that credentials are not stored by the application. Uses STARTTLS for secure SMTP.
-   **Error Handling:** Basic try-except blocks are used for file operations, network communication, and other potentially problematic operations. Error messages are generally relayed to the user.

## Potential Future Enhancements & Considerations

-   **Advanced Input Parsing:**
    -   Support for more robust CSV parsing (e.g., using the `csv` module, handling various delimiters or quoted fields).
    -   Support for other input formats like JSON or YAML.
    -   A more structured way to define expected input fields rather than generic key-value pairs.
-   **PDF Customization & Charts:**
    -   Allow users more control over PDF styling (fonts, colors, logos).
    -   Integrate `matplotlib` or other charting libraries to add visual data representations (bar/pie charts for risk distribution, etc.) to the PDF, as initially requested in the optional requirements.
-   **Email Template Customization:**
    -   Allow users to define or choose from multiple email templates.
-   **GUI Enhancements:**
    -   Consider a more modern GUI toolkit if advanced features are needed (e.g., PyQt, CustomTkinter).
    -   Implement asynchronous operations (threading or asyncio) for potentially long-running tasks like complex PDF generation or network requests to prevent GUI freezes, especially if chart generation or more complex data processing is added.
-   **Configuration/Settings Persistence:**
    -   Option to save user's Gmail address (but **never** the App Password) or default sender name between sessions. This would require careful consideration of secure storage if any sensitive-enough data were to be persisted.
-   **Testing:**
    -   Implement unit tests for the generator and sender modules.
    -   Develop a more structured approach to GUI testing if feasible.
-   **Packaging:**
    -   Use tools like PyInstaller or cx_Freeze to package the application into a standalone executable for easier distribution on Windows and other platforms.
-   **Internationalization (i18n):** Support for multiple languages in the GUI.
-   **Accessibility (a11y):** Ensure the GUI is accessible.

## Maintaining Code Quality

-   **Clarity and Readability:** Strive for clear variable names, comments where necessary, and logical code flow.
-   **Error Handling:** When adding new features, ensure robust error handling and provide informative messages to the user.
-   **Security:** If handling any user credentials or sensitive data, prioritize security best practices. For the current email functionality, the use of App Passwords and not storing them is key.
-   **Dependency Management:** Keep dependencies minimal and clearly documented.

This guidance should help in understanding the current state of the project and making informed decisions for future development.Tool output for `create_file_with_block`:
