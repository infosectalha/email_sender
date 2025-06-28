import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import csv # For CSV import

from datetime import datetime # Added for PDF filename timestamp

# Import new managers and handlers
from template_manager import TemplateManager
from crm_manager import CRMManager
# from signature_handler import get_html_signature # Signature is now globally in TemplateManager
from email_sender import send_gmail
from pdf_generator import generate_report as gr_generate_report


class OutreachApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Smart Email Outreach & Client Manager Tool")
        self.root.geometry("1200x800") # Increased size for more elements

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Initialize managers
        self.template_manager = TemplateManager()
        self.crm_manager = CRMManager() # Connection managed by 'with' or explicit open/close

        self.campaign_recipients = [] # List of dicts: {'email': '', 'template_key': '', 'custom_note': '', ...other_data}
        self.current_pdf_report_path = None # Path for a generated PDF for the current campaign/email

        # --- Main Paned Window for resizable sections ---
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Left Pane: Campaign Setup & Recipients ---
        self.left_pane = ttk.Frame(self.paned_window, width=400)
        self.paned_window.add(self.left_pane, weight=1)

        # --- Right Pane: Email Preview & Sending ---
        self.right_pane = ttk.Frame(self.paned_window, width=800)
        self.paned_window.add(self.right_pane, weight=2)

        self._create_left_pane_widgets()
        self._create_right_pane_widgets()
        self._create_status_bar()

        self._load_email_templates() # Populate template dropdown

    def _create_left_pane_widgets(self):
        # --- Campaign Configuration Frame ---
        config_frame = ttk.LabelFrame(self.left_pane, text="Campaign Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(config_frame, text="Email Template:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(config_frame, textvariable=self.template_var, state="readonly", width=30)
        self.template_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)

        self.load_csv_button = ttk.Button(config_frame, text="Load Recipients from CSV", command=self.load_recipients_csv)
        self.load_csv_button.grid(row=1, column=0, columnspan=2, padx=5, pady=10)

        # (Optional) Manual recipient add - simpler for now to focus on CSV
        # ttk.Label(config_frame, text="Manual Email:").grid(row=2, column=0, sticky=tk.W)
        # self.manual_email_entry = ttk.Entry(config_frame, width=30)
        # self.manual_email_entry.grid(row=2, column=1, sticky=tk.EW)
        # self.add_manual_button = ttk.Button(config_frame, text="Add Manual", command=self.add_manual_recipient)
        # self.add_manual_button.grid(row=3, column=1, sticky=tk.E)


        # --- Recipients List Frame (using Treeview) ---
        recipients_frame = ttk.LabelFrame(self.left_pane, text="Campaign Recipients", padding="10")
        recipients_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cols = ("Email", "Template", "Custom Note")
        self.recipients_tree = ttk.Treeview(recipients_frame, columns=cols, show='headings', height=10)
        for col in cols:
            self.recipients_tree.heading(col, text=col)
            self.recipients_tree.column(col, width=120, anchor=tk.W)

        self.recipients_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        rec_scrollbar = ttk.Scrollbar(recipients_frame, orient=tk.VERTICAL, command=self.recipients_tree.yview)
        self.recipients_tree.configure(yscrollcommand=rec_scrollbar.set)
        rec_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.recipients_tree.bind("<<TreeviewSelect>>", self.on_recipient_selected)


    def _create_right_pane_widgets(self):
        # --- Email Preview/Edit Frame ---
        preview_frame = ttk.LabelFrame(self.right_pane, text="Email Preview & Edit", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(preview_frame, text="Subject:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.email_subject_var = tk.StringVar()
        self.email_subject_entry = ttk.Entry(preview_frame, textvariable=self.email_subject_var, width=80)
        self.email_subject_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        self.email_body_text = tk.Text(preview_frame, height=15, width=80, wrap=tk.WORD)
        self.email_body_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        body_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.email_body_text.yview)
        self.email_body_text.configure(yscrollcommand=body_scrollbar.set)
        body_scrollbar.grid(row=1, column=3, sticky="ns")
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(1, weight=1) # Allow subject to expand a bit too

        # --- PDF Attachment (Simplified for now) ---
        # This part might need more elaborate handling if PDF is per client/template
        pdf_attach_frame = ttk.Frame(preview_frame)
        pdf_attach_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        self.attach_pdf_var = tk.BooleanVar()
        # self.attach_pdf_check = ttk.Checkbutton(pdf_attach_frame, text="Attach Generated PDF:", variable=self.attach_pdf_var, command=self.toggle_pdf_attachment)
        # self.attach_pdf_check.pack(side=tk.LEFT)
        self.pdf_path_label = ttk.Label(pdf_attach_frame, text="No PDF generated/selected for this email.")
        self.pdf_path_label.pack(side=tk.LEFT, padx=5)
        # self.generate_or_select_pdf_button = ttk.Button(pdf_attach_frame, text="Generate/Select PDF", command=self.manage_pdf_for_email)
        # self.generate_or_select_pdf_button.pack(side=tk.LEFT, padx=5)
        # For now, PDF generation will be simpler: one PDF for the campaign if a "findings" like input is provided.

        # --- Sending Configuration ---
        send_config_frame = ttk.LabelFrame(self.right_pane, text="Sending Configuration", padding="10")
        send_config_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(send_config_frame, text="Your Gmail:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.user_gmail_entry = ttk.Entry(send_config_frame, width=30)
        self.user_gmail_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        # TODO: Load from config/settings in future

        ttk.Label(send_config_frame, text="App Password:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.app_password_entry = ttk.Entry(send_config_frame, width=30, show="*")
        self.app_password_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)

        ttk.Label(send_config_frame, text="Your Name (Sign-off):").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.sender_name_entry = ttk.Entry(send_config_frame, width=30)
        self.sender_name_entry.insert(0, "Muhammad Talha") # Pre-fill from requirement
        self.sender_name_entry.grid(row=0, column=3, padx=5, pady=2, sticky=tk.EW)

        # Legal Agreement
        self.agree_var = tk.BooleanVar()
        agree_check = ttk.Checkbutton(send_config_frame,
                                           text="I agree to responsible usage & Gmail terms (2FA+App Password needed).",
                                           variable=self.agree_var, command=self.toggle_send_buttons_state)
        agree_check.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky=tk.W)

        # Action Buttons
        action_button_frame = ttk.Frame(self.right_pane)
        action_button_frame.pack(fill=tk.X, padx=5, pady=10)

        self.send_current_email_button = ttk.Button(action_button_frame, text="Send Previewed Email", command=self.send_previewed_email, state=tk.DISABLED)
        self.send_current_email_button.pack(side=tk.LEFT, padx=10)

        self.send_campaign_button = ttk.Button(action_button_frame, text="Send Full Campaign", command=self.send_full_campaign, state=tk.DISABLED)
        self.send_campaign_button.pack(side=tk.LEFT, padx=10)


    def _create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready. Load templates and recipients to begin.", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0,5))

    def _load_email_templates(self):
        templates = self.template_manager.list_templates()
        if templates:
            self.template_combo['values'] = templates
            if templates: # Select first one if available
                 self.template_combo.current(0)
                 self.on_template_selected() # Trigger preview for the first template
            self.update_status(f"{len(templates)} email templates loaded.")
        else:
            self.update_status("No email templates found in 'templates' directory.")
            messagebox.showwarning("Templates Missing", "No email templates found in the 'templates' directory. Please create some .html template files.")

    def on_template_selected(self, event=None):
        # This will be used to render a generic preview or the selected recipient's preview
        selected_template = self.template_var.get()
        if not selected_template:
            return

        # For now, just render with placeholder data or clear preview
        # When a recipient is selected, this will be re-triggered with specific context
        # Let's try to render with some default context for a generic preview
        # The subject will also need to be dynamic, perhaps from the template itself or a convention

        mock_context = {
            'client_name': '{Client Name}',
            'domain': '{Domain}',
            'custom_note': '{Custom Note Placeholder}',
            'report_summary': '{Report Summary Placeholder}',
            # Add other common placeholders your templates might use
        }
        rendered_body = self.template_manager.render_template(selected_template, mock_context)
        if rendered_body:
            self.email_body_text.delete('1.0', tk.END)
            self.email_body_text.insert('1.0', rendered_body)
            # Placeholder for subject - ideally, subject could also be part of template or a mapping
            self.email_subject_var.set(f"Preview: {selected_template.replace('.html', '')} for {{Domain}}")
            self.update_status(f"Previewing template: {selected_template}")
        else:
            self.email_body_text.delete('1.0', tk.END)
            self.email_subject_var.set("")
            self.update_status(f"Failed to render template: {selected_template}")


    def load_recipients_csv(self):
        filepath = filedialog.askopenfilename(
            title="Import Campaign CSV",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not filepath:
            self.update_status("CSV import cancelled.")
            return

        self.campaign_recipients.clear()
        self.recipients_tree.delete(*self.recipients_tree.get_children()) # Clear treeview
        self._clear_preview_fields() # Clear preview when loading new CSV

        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f: # utf-8-sig handles BOM
                reader = csv.DictReader(f)
                if not reader.fieldnames or not all(col in reader.fieldnames for col in ['email']):
                    messagebox.showerror("CSV Error", "CSV must contain at least an 'email' column header.")
                    self.update_status("CSV import failed: Missing 'email' header.")
                    return

                for row_idx, row in enumerate(reader):
                    email = row.get('email', '').strip()
                    if not email: # Skip rows with no email
                        self.update_status(f"Skipped row {row_idx+1} in CSV: email is missing.")
                        continue

                    # template_key from CSV or default selected in UI
                    template_key = row.get('template', self.template_var.get()).strip()
                    if not template_key.endswith('.html'): # Ensure .html suffix if not present
                        template_key += '.html'

                    # Check if this template actually exists
                    if template_key not in self.template_manager.list_templates():
                        self.update_status(f"Warning: Template '{template_key}' for {email} not found. Using default/selected.")
                        template_key = self.template_var.get() # Fallback to currently selected

                    recipient_data = {
                        'email': email,
                        'template_key': template_key,
                        'custom_note': row.get('custom_note', ''),
                        'client_name': row.get('name', row.get('client_name', '')),
                        'domain': row.get('domain', ''),
                        # PDF related fields from CSV
                        'pdf_attachment_path': row.get('pdf_attachment_path', '').strip(), # Pre-existing PDF
                        'pdf_generate_data': { # Data for on-the-fly PDF generation
                            'Domain': row.get('pdf_domain', row.get('domain', '')), # Fallback to main domain
                            'Risk': row.get('pdf_risk_summary', ''), # Specific field for risk summary in PDF
                            'Details': row.get('pdf_details', ''),     # Specific field for other details in PDF
                            # Add more fields here that pdf_generator.py might use
                            # For example, if pdf_generator expects "SSL", "Open Ports" etc.,
                            # they could be read as row.get('pdf_ssl_info', '')
                        }
                    }
                    # Add all other row data to recipient_data for template context, excluding specific keys already handled
                    # to avoid them being duplicated in context if they are also in pdf_generate_data
                    excluded_keys_for_context = ['email', 'template', 'custom_note', 'name', 'client_name', 'domain',
                                                 'pdf_attachment_path', 'pdf_domain', 'pdf_risk_summary', 'pdf_details']
                    for key, value in row.items():
                        if key not in excluded_keys_for_context and key not in recipient_data : # Check if not already set by specific logic
                            recipient_data[key] = value
                        elif key not in excluded_keys_for_context and key not in recipient_data['pdf_generate_data']: # Add to pdf_generate_data if its a pdf_ field
                             if key.startswith('pdf_'):
                                 recipient_data['pdf_generate_data'][key.replace('pdf_','',1).capitalize()] = value


                    self.campaign_recipients.append(recipient_data)
                    self.recipients_tree.insert("", tk.END, values=(
                        recipient_data['email'],
                        recipient_data['template_key'],
                        recipient_data['custom_note']
                    ))
            self.update_status(f"Loaded {len(self.campaign_recipients)} recipients from {os.path.basename(filepath)}.")
            if self.campaign_recipients:
                 self.recipients_tree.selection_set(self.recipients_tree.get_children()[0]) # Select first
                 self.on_recipient_selected() # Trigger preview for the first loaded recipient
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {filepath}")
            self.update_status("CSV import failed: File not found.")
        except Exception as e:
            messagebox.showerror("CSV Read Error", f"Error reading CSV file: {e}")
            self.update_status(f"CSV import error: {e}")
        self.toggle_send_buttons_state()

    def _clear_preview_fields(self):
        self.email_subject_var.set("")
        self.email_body_text.delete('1.0', tk.END)
        self.pdf_path_label.config(text="No PDF selected/generated.")
        self.current_pdf_report_path = None
        # self.on_template_selected() # Optionally, reload generic preview of current template

    def on_recipient_selected(self, event=None):
        selected_items = self.recipients_tree.selection()
        if not selected_items:
            # If selection is cleared, could also clear preview fields
            # self._clear_preview_fields()
            # However, on_template_selected might provide a generic template preview which is fine
            return

        item_id = selected_items[0] # Get the first selected item
        # Find the corresponding recipient data from self.campaign_recipients
        # This is a bit inefficient if list is huge, but ok for moderate numbers
        # A dict mapping tree_id to index or using item values directly would be better.
        # For now, let's assume order in tree matches order in list for simplicity,
        # or iterate to find by email (if emails are unique in the list view).

        # A more robust way: store index in treeview item or use email as key
        # For this example, let's find by index, assuming tree items are added in order
        try:
            item_index = self.recipients_tree.index(item_id)
            recipient_data = self.campaign_recipients[item_index]
        except (ValueError, IndexError):
            self.update_status("Error selecting recipient from list.")
            return

        template_to_render = recipient_data.get('template_key', self.template_var.get())

        # Prepare context for rendering this specific recipient's email
        # Base context from recipient_data (which includes all CSV columns)
        context = recipient_data.copy()

        # Add/override sender_name if needed by template, though signature handles it mostly
        context['sender_name'] = self.sender_name_entry.get().strip() or "Muhammad Talha"

        rendered_body = self.template_manager.render_template(template_to_render, context)

        if rendered_body:
            self.email_body_text.delete('1.0', tk.END)
            self.email_body_text.insert('1.0', rendered_body)
            # Update subject based on recipient data or template convention
            # Example: "Report for {domain}" or "Special Offer for {client_name}"
            # This needs a more robust way to determine subject, maybe from template too.
            subject_prefix = template_to_render.replace('.html','').replace('_', ' ').title()
            domain_in_context = recipient_data.get('domain', '')
            client_name_in_context = recipient_data.get('client_name', '')

            if domain_in_context:
                self.email_subject_var.set(f"{subject_prefix} - Regarding {domain_in_context}")
            elif client_name_in_context:
                 self.email_subject_var.set(f"{subject_prefix} - For {client_name_in_context}")
            else:
                self.email_subject_var.set(f"{subject_prefix} - Information")

            self.update_status(f"Previewing email for: {recipient_data['email']} using {template_to_render}")
        else:
            self.email_body_text.delete('1.0', tk.END)
            self.email_subject_var.set("")
            self.update_status(f"Failed to render template for {recipient_data['email']}.")

        # PDF attachment logic update
        self._handle_pdf_for_recipient(recipient_data, is_preview=True)

    def _generate_pdf_for_recipient(self, recipient_data):
        """
        Generates a PDF if pdf_generate_data is present and valid.
        Returns the path to the generated PDF or None.
        """
        pdf_gen_data = recipient_data.get('pdf_generate_data', {})
        # Check if there's meaningful data to generate a PDF, beyond just a domain name.
        # For example, require 'Risk' or 'Details' to be non-empty.
        if pdf_gen_data.get('Domain') and (pdf_gen_data.get('Risk') or pdf_gen_data.get('Details')):
            # Sanitize domain for filename
            domain_filename_part = "".join(c if c.isalnum() else "_" for c in pdf_gen_data['Domain'])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            reports_dir = "generated_reports"
            if not os.path.exists(reports_dir):
                try:
                    os.makedirs(reports_dir)
                except OSError as e:
                    self.update_status(f"Error creating reports directory: {e}")
                    return None

            # Use recipient's email (sanitized) or domain for unique filename part
            email_prefix = "".join(c if c.isalnum() else "_" for c in recipient_data.get('email', 'unknown_email').split('@')[0])
            pdf_filename = f"Report_{email_prefix}_{domain_filename_part}_{timestamp}.pdf"
            output_filepath = os.path.join(reports_dir, pdf_filename)

            # Call the actual PDF generator (ensure data matches what pdf_generator expects)
            # pdf_generator.py expects a flat dict.
            # We've structured pdf_generate_data, so pass that.
            # Ensure all expected keys by gr_generate_report are in pdf_gen_data or handled by pdf_generator defaults.
            pdf_data_for_generator = pdf_gen_data.copy() # Use the specific pdf_generate_data
            # Example: if pdf_generator.py also uses 'CustomNote' or other top-level fields from recipient_data
            # for the PDF, they would need to be added to pdf_data_for_generator here.

            success, message = gr_generate_report(pdf_data_for_generator, output_filepath)
            if success:
                self.update_status(f"Generated PDF: {output_filepath}")
                return output_filepath
            else:
                self.update_status(f"PDF Gen Failed for {recipient_data['email']}: {message}")
                messagebox.showwarning("PDF Generation Failed", f"Could not generate PDF for {recipient_data['email']}:\n{message}")
                return None
        return None # No data to generate PDF

    def _handle_pdf_for_recipient(self, recipient_data, is_preview=False):
        """
        Determines the PDF path for a recipient.
        Prioritizes existing path, then tries to generate one.
        Updates self.current_pdf_report_path and UI label.
        If is_preview is False, it means we are in the sending logic.
        Returns the path of the PDF to be used, or None.
        """
        # 1. Check for pre-existing PDF path from CSV
        existing_pdf_path = recipient_data.get('pdf_attachment_path')
        if existing_pdf_path and os.path.exists(existing_pdf_path):
            if is_preview:
                self.current_pdf_report_path = existing_pdf_path
                self.pdf_path_label.config(text=f"Attached (CSV): {os.path.basename(existing_pdf_path)}")
            return existing_pdf_path

        # 2. If no pre-existing path, try to generate a new PDF
        generated_pdf_path = self._generate_pdf_for_recipient(recipient_data)
        if generated_pdf_path:
            if is_preview:
                self.current_pdf_report_path = generated_pdf_path
                self.pdf_path_label.config(text=f"Attached (Generated): {os.path.basename(generated_pdf_path)}")
            return generated_pdf_path

        # 3. No PDF available or generated
        if is_preview:
            self.current_pdf_report_path = None
            self.pdf_path_label.config(text="No PDF for this email.")
        return None


    def send_previewed_email(self):
        # Placeholder: Get data for the currently selected/previewed recipient
        # and send only that one email.
        selected_items = self.recipients_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No recipient selected to send email.")
            return

        item_id = selected_items[0]
        try:
            item_index = self.recipients_tree.index(item_id)
            recipient_data = self.campaign_recipients[item_index]
        except (ValueError, IndexError):
            self.update_status("Error identifying selected recipient for sending.")
            return

        self._send_single_email_logic(recipient_data, is_part_of_campaign=False)


    def send_full_campaign(self):
        if not self.campaign_recipients:
            messagebox.showinfo("No Recipients", "No recipients loaded for the campaign.")
            return

        if messagebox.askyesno("Confirm Campaign Send", f"Are you sure you want to send this campaign to {len(self.campaign_recipients)} recipient(s)?"):
            self.update_status(f"Starting campaign for {len(self.campaign_recipients)} recipients...")
            sent_count = 0
            failed_count = 0
            for i, recipient_data in enumerate(self.campaign_recipients):
                self.update_status(f"Sending to {recipient_data['email']} ({i+1}/{len(self.campaign_recipients)})...")
                # Update preview for this recipient before sending (optional, but good for visual feedback if slow)
                # self.recipients_tree.selection_set(self.recipients_tree.get_children()[i])
                # self.on_recipient_selected()
                # self.root.update_idletasks() # Refresh UI

                success = self._send_single_email_logic(recipient_data, is_part_of_campaign=True)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1

                # Small delay to avoid being rate-limited too quickly, GUI update
                self.root.after(200) # 200ms, adjust as needed
                self.root.update_idletasks()


            summary_message = f"Campaign finished. Sent: {sent_count}, Failed: {failed_count}."
            self.update_status(summary_message)
            messagebox.showinfo("Campaign Complete", summary_message)

    def _send_single_email_logic(self, recipient_data, is_part_of_campaign=True):
        """
        Handles logic for sending one email.
        recipient_data is a dict from self.campaign_recipients or current preview.
        """
        user_gmail = self.user_gmail_entry.get().strip()
        app_password = self.app_password_entry.get().strip()
        sender_name = self.sender_name_entry.get().strip()

        if not all([user_gmail, app_password, sender_name]):
            messagebox.showerror("Configuration Error", "Your Gmail, App Password, and Sender Name must be set.")
            if not is_part_of_campaign: self.update_status("Email send failed: Missing sender configuration.")
            return False

        recipient_email = recipient_data.get('email')
        template_key = recipient_data.get('template_key', self.template_var.get()) # Fallback to UI selected

        # For sending current previewed email, use the content from UI fields
        # For campaign, re-render to ensure latest context (though it should be same as preview)
        final_subject = ""
        final_body = ""

        if not is_part_of_campaign and self.recipients_tree.selection(): # Sending previewed
            final_subject = self.email_subject_entry.get()
            final_body = self.email_body_text.get("1.0", tk.END)
        else: # Rendering for campaign or if no specific preview selection active
            context = recipient_data.copy()
            context['sender_name'] = sender_name

            # Regenerate subject (consistent with on_recipient_selected logic)
            subject_prefix = template_key.replace('.html','').replace('_', ' ').title()
            domain_in_context = recipient_data.get('domain', '')
            client_name_in_context = recipient_data.get('client_name', '')
            if domain_in_context: final_subject = f"{subject_prefix} - Regarding {domain_in_context}"
            elif client_name_in_context: final_subject = f"{subject_prefix} - For {client_name_in_context}"
            else: final_subject = f"{subject_prefix} - Information"

            final_body = self.template_manager.render_template(template_key, context)

        if not final_body:
            message = f"Failed to render template '{template_key}' for {recipient_email}."
            if not is_part_of_campaign:
                messagebox.showerror("Template Error", message)
                self.update_status(message)
            else:
                print(message) # Log for campaign, don't stop for each
            return False

        # PDF Attachment for this specific email
        # Determine PDF path: uses pre-existing from CSV, or generates on-the-fly
        attachment_to_send = self._handle_pdf_for_recipient(recipient_data, is_preview=False)

        if recipient_data.get('pdf_attachment_path') and attachment_to_send is None:
            # This means a pre-existing PDF was specified but not found/usable, and generation also failed or wasn't applicable.
            # _handle_pdf_for_recipient would have logged/warned during generation attempt if that was the case.
            # If only pre-existing was specified and failed, we need a clear warning here before sending.
            warning_msg = f"Specified PDF '{recipient_data.get('pdf_attachment_path')}' for {recipient_email} not found or failed to generate. Sending without attachment."
            if not is_part_of_campaign:
                messagebox.showwarning("Attachment Issue", warning_msg)
            else:
                print(f"Campaign Info: {warning_msg}")
        elif attachment_to_send is None:
             # No PDF was specified, and no PDF was generated. This is fine, just proceed without.
             pass
        # The commented out block below is now entirely handled by _handle_pdf_for_recipient
        # and the warning logic just above this. Removing it.

        # Actual sending
        success, send_message = send_gmail(
            sender_email=user_gmail,
            app_password=app_password,
            recipient_email=recipient_email,
            subject=final_subject,
            body=final_body,
            attachment_filepath=attachment_to_send
        )

        if success:
            if not is_part_of_campaign:
                messagebox.showinfo("Email Sent", f"Email successfully sent to {recipient_email}!")
                self.update_status(f"Email sent to {recipient_email}.")
            # Log to CRM
            with self.crm_manager as crm: # Use context manager for connection
                crm.add_or_update_client(
                    email=recipient_email,
                    name=recipient_data.get('client_name'),
                    status="Contacted", # Or derive from template
                    tags=recipient_data.get('tags', 'outreach'), # Add default tag
                    interaction_log={
                        'type': 'Email Sent',
                        'template': template_key,
                        'subject': final_subject,
                        'notes': f"Sent via campaign. Custom note: {recipient_data.get('custom_note', 'N/A')}"
                    }
                )
            return True
        else: # This else corresponds to "if success:"
            if not is_part_of_campaign: # Indented correctly under the parent else
                messagebox.showerror("Email Error", f"Failed to send email to {recipient_email}: {send_message}")
                self.update_status(f"Failed to send to {recipient_email}: {send_message}")
            else: # This else corresponds to "if not is_part_of_campaign:" and must align with it
                print(f"Failed to send to {recipient_email}: {send_message}") # Log for campaign
            return False # This return belongs to the outer "if success: ... else: ..."


    def toggle_send_buttons_state(self, event=None):
        # Enable send buttons if agree_var is true AND recipients are loaded for campaign send
        # AND gmail config is present
        gmail_configured = self.user_gmail_entry.get() and self.app_password_entry.get()

        if self.agree_var.get() and gmail_configured:
            if self.recipients_tree.selection(): # If a recipient is selected for individual send
                 self.send_current_email_button.config(state=tk.NORMAL)
            else:
                 self.send_current_email_button.config(state=tk.DISABLED)

            if self.campaign_recipients: # If there's a campaign list
                self.send_campaign_button.config(state=tk.NORMAL)
            else:
                self.send_campaign_button.config(state=tk.DISABLED)
        else:
            self.send_current_email_button.config(state=tk.DISABLED)
            self.send_campaign_button.config(state=tk.DISABLED)

    def update_status(self, message):
        self.status_bar.config(text=message)
        print(f"Status: {message}") # Also print to console for debugging

    # Placeholder for PDF management - to be expanded
    # def manage_pdf_for_email(self):
    #     # This function would handle generating a PDF based on some input (e.g. findings for a client)
    #     # or selecting an existing PDF. For now, we assume PDF path might come from CSV or a single campaign PDF.
    #     messagebox.showinfo("PDF Management", "PDF generation/selection per email to be implemented.\nFor now, ensure 'pdf_attachment_path' is in CSV or use a general campaign PDF.")
    #     # Example: if some data is available to generate PDF:
    #     # findings_data = {"Domain": "example.com", "Risk": "High"} # Get this from somewhere
    #     # filepath = filedialog.asksaveasfilename(defaultextension=".pdf", title="Save Report As")
    #     # if filepath:
    #     #     success, msg = gr_generate_report(findings_data, filepath)
    #     #     if success:
    #     #         self.current_pdf_report_path = filepath
    #     #         self.pdf_path_label.config(text=f"PDF: {os.path.basename(filepath)}")
    #     #         messagebox.showinfo("PDF Generated", msg)
    #     #     else:
    #     #         messagebox.showerror("PDF Error", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = OutreachApp(root)
    # Set initial state for send buttons based on agreement (which is initially False)
    app.toggle_send_buttons_state()
    root.mainloop()

    # Ensure CRM connection is closed if app exits unexpectedly (though 'with' handles it for explicit calls)
    if hasattr(app, 'crm_manager') and app.crm_manager._conn is not None:
        app.crm_manager._close()
        print("Closed CRM DB connection on exit.")
