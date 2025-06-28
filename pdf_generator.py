from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Vulnerability Assessment Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, content_dict, is_recommendations=False):
        self.set_font('Arial', '', 10)
        if is_recommendations:
            for item in content_dict: # Assuming content_dict is a list of strings for recommendations
                self.multi_cell(0, 5, f"- {item}")
                self.ln(1)
        else:
            for key, value in content_dict.items():
                self.set_font('Arial', 'B', 10)
                self.multi_cell(0, 5, f"{key}:")
                self.set_font('Arial', '', 10)
                self.multi_cell(0, 5, str(value))
                self.ln(2)
        self.ln()

    def executive_summary_content(self, data):
        self.set_font('Arial', '', 10)
        domain = data.get("Domain", "the assessed target")
        summary_text = (
            f"This report details the findings of a vulnerability assessment conducted for {domain}. "
            f"The assessment focused on several key areas including domain configuration, SSL/TLS status, "
            f"DNS records, and email security indicators. \n\n"
            f"Key findings include: {data.get('Risk', 'See detailed findings')}. "
            f"Recommendations are provided to address identified vulnerabilities and improve the overall security posture."
        )
        self.multi_cell(0, 5, summary_text)
        self.ln()

def generate_report(data, output_filepath):
    if not data:
        print("No data provided to generate_report function.")
        return False

    pdf = PDF()
    pdf.add_page()

    # Title Page (simplified)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, f"Report for: {data.get('Domain', 'N/A')}", 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(20)

    # Executive Summary
    pdf.chapter_title('Executive Summary')
    pdf.executive_summary_content(data)

    # Findings Details
    pdf.chapter_title('Findings Details')
    # Exclude some common keys that might be summarized elsewhere or too generic for this section
    detailed_findings = {k: v for k, v in data.items() if k not in ["Domain", "Executive Summary", "Recommendations"]}
    if not detailed_findings:
        detailed_findings = {"Info": "No specific itemized findings provided in the input."}
    pdf.chapter_body(detailed_findings)

    # Risk Overview (if a specific "Risk" key exists)
    if "Risk" in data:
        pdf.chapter_title('Risk Overview')
        pdf.chapter_body({"Identified Risk": data["Risk"]})

    # Recommendations
    pdf.chapter_title('Recommendations')
    # Placeholder recommendations - this should ideally be more dynamic or based on input
    recommendations = [
        "Review and implement SPF, DKIM, and DMARC records for email security.",
        "Ensure SSL/TLS certificates are valid, correctly configured, and use strong ciphers.",
        "Regularly scan for open ports and services; close any that are unnecessary.",
        "Keep all software and systems up to date with security patches.",
        "Implement robust password policies and multi-factor authentication where possible.",
        "Consult the detailed findings for specific actions related to identified issues."
    ]
    # If user provides recommendations in input, use them
    if "Recommendations" in data:
        if isinstance(data["Recommendations"], list):
            recommendations = data["Recommendations"]
        elif isinstance(data["Recommendations"], str):
            recommendations = [rec.strip() for rec in data["Recommendations"].split(';') if rec.strip()]


    pdf.chapter_body(recommendations, is_recommendations=True)

    try:
        pdf.output(output_filepath, 'F')
        return True, f"PDF report generated successfully: {output_filepath}"
    except Exception as e:
        error_message = f"Error saving PDF to '{output_filepath}': {e}"
        print(error_message) # Keep console log for detailed debugging
        return False, error_message

if __name__ == '__main__':
    # Example Usage (for testing pdf_generator.py directly)
    sample_data = {
        "Domain": "example.com",
        "SSL": "Valid, Grade A",
        "Risk": "Missing SPF record, DMARC not enforced",
        "Email Found": "contact@example.com, support@example.com",
        "Open Ports": "80, 443",
        "DNS Records": "A, MX, TXT records found.",
        "WHOIS Info": "Registrar: GoDaddy, Registered On: 2020-01-01",
        "Recommendations": "Implement SPF and DMARC; Review open ports"
    }

    # Test with list of recommendations
    # sample_data_list_reco = {
    #     "Domain": "test.com",
    #     "SSL": "Expired",
    #     "Risk": "SSL Certificate Expired",
    #     "Recommendations": [
    #         "Renew SSL Certificate immediately.",
    #         "Schedule regular certificate renewal checks."
    #     ]
    # }

    if generate_report(sample_data, "sample_report.pdf"):
        print("Sample report generated successfully: sample_report.pdf")
    else:
        print("Failed to generate sample report.")

    # if generate_report(sample_data_list_reco, "sample_report_list_reco.pdf"):
    #     print("Sample report with list recommendations generated successfully: sample_report_list_reco.pdf")
    # else:
    #     print("Failed to generate sample report with list recommendations.")
