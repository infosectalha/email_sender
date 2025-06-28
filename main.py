import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vulnerability Report Generator")
        self.root.geometry("800x700")

        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text="Input Findings", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        self.findings_text = tk.Text(input_frame, height=10, width=70)
        self.findings_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        input_button_frame = ttk.Frame(input_frame)
        input_button_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.paste_button = ttk.Button(input_button_frame, text="Paste Findings", command=self.paste_findings)
        self.paste_button.pack(pady=2, fill=tk.X)

        self.import_file_button = ttk.Button(input_button_frame, text="Import File (.txt, .csv)", command=self.import_file_dialog)
        self.import_file_button.pack(pady=2, fill=tk.X)

        # --- PDF Section ---
        pdf_frame = ttk.LabelFrame(main_frame, text="PDF Report", padding="10")
        pdf_frame.pack(fill=tk.X, pady=5)

        self.generate_pdf_button = ttk.Button(pdf_frame, text="Generate PDF Report", command=self.generate_pdf)
        self.generate_pdf_button.pack(pady=5)

        # --- Email Section ---
        email_frame = ttk.LabelFrame(main_frame, text="Email Client", padding="10")
        email_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Recipient Email
        recipient_frame = ttk.Frame(email_frame)
        recipient_frame.pack(fill=tk.X, pady=2)
        ttk.Label(recipient_frame, text="Recipient Email:").pack(side=tk.LEFT, padx=5)
        self.recipient_email_entry = ttk.Entry(recipient_frame, width=40)
        self.recipient_email_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # User's Gmail
        user_gmail_frame = ttk.Frame(email_frame)
        user_gmail_frame.pack(fill=tk.X, pady=2)
        ttk.Label(user_gmail_frame, text="Your Gmail Address:").pack(side=tk.LEFT, padx=5)
        self.user_gmail_entry = ttk.Entry(user_gmail_frame, width=40)
        self.user_gmail_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # App Password
        app_password_frame = ttk.Frame(email_frame)
        app_password_frame.pack(fill=tk.X, pady=2)
        ttk.Label(app_password_frame, text="Gmail App Password:").pack(side=tk.LEFT, padx=5)
        self.app_password_entry = ttk.Entry(app_password_frame, width=40, show="*")
        self.app_password_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Sender Name
        sender_name_frame = ttk.Frame(email_frame)
        sender_name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sender_name_frame, text="Your Name (for email sign-off):").pack(side=tk.LEFT, padx=5)
        self.sender_name_entry = ttk.Entry(sender_name_frame, width=40)
        self.sender_name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)


        # Email Subject
        subject_frame = ttk.Frame(email_frame)
        subject_frame.pack(fill=tk.X, pady=2)
        ttk.Label(subject_frame, text="Email Subject:").pack(side=tk.LEFT, padx=5)
        self.email_subject_entry = ttk.Entry(subject_frame, width=60)
        self.email_subject_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)


        # Email Body
        ttk.Label(email_frame, text="Email Body:").pack(anchor=tk.W, padx=5, pady=(5,0))
        self.email_body_text = tk.Text(email_frame, height=10)
        self.email_body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

        # Legal Agreement & Info
        legal_info_text = (
            "Important:\n"
            "- This tool sends emails using your Gmail account via SMTP.\n"
            "- Your Gmail credentials (App Password) are used for sending only and are NOT stored by this tool.\n"
            "- Enable 2-Factor Authentication (2FA) on your Gmail account and generate an App Password to use with this tool.\n"
            "- You are responsible for complying with Gmail's Terms of Service, Acceptable Use Policy, and all applicable anti-spam laws (e.g., CAN-SPAM, GDPR).\n"
            "- Use this tool responsibly and only to send reports to clients who have consented to receive them."
        )

        ttk.Label(email_frame, text=legal_info_text, wraplength=750, justify=tk.LEFT).pack(pady=(10,5), padx=5, anchor=tk.W)

        self.agree_var = tk.BooleanVar()
        self.agree_check = ttk.Checkbutton(email_frame,
                                           text="I have read and agree to the terms and responsible usage guidelines mentioned above.",
                                           variable=self.agree_var, command=self.toggle_send_button)
        self.agree_check.pack(pady=5, anchor=tk.W, padx=5)

        self.send_email_button = ttk.Button(email_frame, text="Send Email via Gmail", command=self.send_email, state=tk.DISABLED) # Changed text slightly
        self.send_email_button.pack(pady=5)

        # --- Status Bar ---
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize placeholder variables
        self.parsed_data = {}
        self.pdf_filepath = ""

    def paste_findings(self):
        try:
            clipboard_content = self.root.clipboard_get()
            self.findings_text.delete('1.0', tk.END)
            self.findings_text.insert('1.0', clipboard_content)
            self.status_bar.config(text="Findings pasted from clipboard.")
        except tk.TclError:
            self.status_bar.config(text="Nothing to paste or clipboard format error.")
            messagebox.showwarning("Paste Error", "Could not get content from clipboard.")
        self.parse_input_data() # Parse after pasting

    def import_file_dialog(self):
        filepath = filedialog.askopenfilename(
            title="Import Findings File",
            filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.findings_text.delete('1.0', tk.END)
                self.findings_text.insert('1.0', content)
                self.status_bar.config(text=f"File imported: {filepath}")
                self.parse_input_data() # Parse after importing
            except Exception as e:
                self.status_bar.config(text=f"Error importing file: {e}")
                messagebox.showerror("Import Error", f"Could not read file: {e}")
        else:
            self.status_bar.config(text="File import cancelled.")

    def parse_input_data(self):
        content = self.findings_text.get("1.0", tk.END).strip()
        self.parsed_data = {}
        lines = content.splitlines()

        if not lines:
            self.status_bar.config(text="No data to parse.")
            # Potentially clear previously parsed data or show a warning
            # messagebox.showwarning("Parsing Info", "Input area is empty. Nothing to parse.")
            return

        # Attempt to detect if it's CSV-like (e.g., contains commas and no colons in first few lines)
        # This is a very basic detection
        is_csv_like = False
        if lines:
            sample_lines = lines[:min(3, len(lines))] # Check first 3 lines
            if all(',' in line and ':' not in line for line in sample_lines if line.strip()):
                is_csv_like = True
            # If there's only one line and it contains commas, treat as CSV header or data
            elif len(lines) == 1 and ',' in lines[0]:
                 is_csv_like = True


        if is_csv_like:
            # Basic CSV parsing: treat each line as "Key,Value"
            # More robust CSV parsing would use the `csv` module
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                parts = line.split(',', 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    self.parsed_data[key] = value
                else:
                    # Handle lines that are not simple Key,Value (e.g. could be a headerless single column)
                    # For now, we'll use a generic key or skip
                    self.parsed_data[f"csv_row_{i+1}_col_1"] = line.strip()
            self.status_bar.config(text=f"Parsed {len(self.parsed_data)} CSV-like entries.")
        else:
            # TXT-like parsing: "Key: Value"
            for line in lines:
                if not line.strip():
                    continue
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    self.parsed_data[key] = value
                else:
                    # If no colon, store the whole line with a generic key or skip
                    # For now, we'll skip lines not matching "Key: Value" format in text mode
                    pass # Or: self.parsed_data[f"text_line_{i+1}"] = line.strip()
            self.status_bar.config(text=f"Parsed {len(self.parsed_data)} key-value pairs.")

        if not self.parsed_data and content:
             messagebox.showwarning("Parsing Issue", "Could not parse any data. Please check format:\nTXT: 'Key: Value' per line\nCSV: 'Key,Value' per line")
        elif self.parsed_data:
            print("Parsed data:", self.parsed_data) # For debugging, can be removed
            # Automatically try to populate email subject and body using the new generator
            self.auto_populate_email_fields()


from pdf_generator import generate_report as gr_generate_report # Alias to avoid potential name clash
from email_generator import compose_email_subject, compose_email_body

    def generate_pdf(self):
        if not self.parsed_data:
            messagebox.showerror("Error", "No data to generate PDF. Please input or import findings first.")
            self.status_bar.config(text="PDF Generation failed: No data.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Save Report As"
        )

        if not filepath:
            self.status_bar.config(text="PDF generation cancelled.")
            return

        try:
            success, message = gr_generate_report(self.parsed_data, filepath)
            if success:
                self.pdf_filepath = filepath # Store for attaching to email
                self.status_bar.config(text=f"PDF report generated: {filepath}")
                messagebox.showinfo("Success", message) # Use message from generator
                # Attempt to auto-populate email fields now that PDF is ready and data is confirmed
                self.auto_populate_email_fields()
            else:
                self.status_bar.config(text=f"PDF Generation Failed: {message}")
                messagebox.showerror("PDF Generation Error", message + "\n(Check console for more details if applicable)")
        except Exception as e:
            self.status_bar.config(text=f"Critical Error during PDF generation: {e}")
            messagebox.showerror("PDF Generation Critical Error", f"An unexpected error occurred: {e}\n(Check console for more details)")
            print(f"PDF Generation Exception: {e}") # For debugging

    def auto_populate_email_fields(self):
        """
        Populates the email subject and body fields based on parsed data
        using the email_generator module.
        """
        if not self.parsed_data:
            # Clear fields if no data, or leave them as is? For now, leave as is.
            # Could also disable the email section if no data.
            return

        # Subject
        subject = compose_email_subject(self.parsed_data)
        self.email_subject_entry.delete(0, tk.END)
        self.email_subject_entry.insert(0, subject)

        # Body
        sender_name = self.sender_name_entry.get().strip()
        # We pass sender_name so email_generator can use it or a default
        body = compose_email_body(self.parsed_data, sender_name)
        self.email_body_text.delete('1.0', tk.END)
        self.email_body_text.insert('1.0', body)

        self.status_bar.config(text="Email subject and body populated.")

from email_sender import send_gmail

    def send_email(self):
        if not self.agree_var.get():
            messagebox.showwarning("Agreement Required", "Please agree to the terms before sending an email.")
            return

        recipient_email = self.recipient_email_entry.get().strip()
        user_gmail = self.user_gmail_entry.get().strip()
        app_password = self.app_password_entry.get().strip() # Ensure this is fetched correctly

        subject = self.email_subject_entry.get().strip()
        body = self.email_body_text.get("1.0", tk.END).strip()

        # Basic validation
        if not recipient_email:
            messagebox.showerror("Error", "Recipient email is required.")
            return
        if not user_gmail:
            messagebox.showerror("Error", "Your Gmail address is required.")
            return
        if not app_password:
            messagebox.showerror("Error", "Gmail App Password is required.")
            return
        if not subject:
            messagebox.showerror("Error", "Email subject is required.")
            return
        if not body:
            messagebox.showerror("Error", "Email body cannot be empty.")
            return

        # Check for PDF attachment
        attachment_path = self.pdf_filepath
        if not attachment_path or not os.path.exists(attachment_path):
            if messagebox.askyesno("No Attachment", "No PDF report found or path is invalid. Send email without attachment?"):
                attachment_path = None
            else:
                self.status_bar.config(text="Email sending cancelled by user (no attachment).")
                return

        self.status_bar.config(text="Sending email...")
        self.root.update_idletasks() # Update GUI to show status

        try:
            # Consider running this in a separate thread for complex apps to avoid GUI freeze
            # For this tool, direct call might be acceptable for simplicity.
            success, message = send_gmail(
                sender_email=user_gmail,
                app_password=app_password,
                recipient_email=recipient_email,
                subject=subject,
                body=body, # Assuming email_sender handles HTML/Plain conversion or we send as plain
                attachment_filepath=attachment_path
            )

            if success:
                self.status_bar.config(text=message)
                messagebox.showinfo("Success", message)
            else:
                self.status_bar.config(text=f"Email Failed: {message}")
                messagebox.showerror("Email Error", message)
        except Exception as e:
            self.status_bar.config(text=f"Critical Error: {e}")
            messagebox.showerror("Critical Error", f"An unexpected error occurred during email sending: {e}")


    def toggle_send_button(self):
        if self.agree_var.get():
            self.send_email_button.config(state=tk.NORMAL)
        else:
            self.send_email_button.config(state=tk.DISABLED)

    def update_status(self, message):
        self.status_bar.config(text=message)


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()
