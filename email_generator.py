def compose_email_subject(data):
    """
    Composes a professional email subject line.
    """
    domain = data.get("Domain", None)
    if domain:
        return f"Vulnerability Assessment Report for {domain}"
    return "Vulnerability Assessment Report"

def compose_email_body(data, sender_name_input):
    """
    Composes a professional email body.
    - Greets the client.
    - Briefly summarizes findings.
    - Mentions attached report.
    - Signs off with sender’s name.
    """
    domain = data.get("Domain", "your domain/asset")

    # Try to create a concise summary of findings
    # This can be expanded based on common keys expected in `data`
    findings_summary_parts = []
    if "Risk" in data:
        findings_summary_parts.append(f"identified risk: {data['Risk']}")
    if "SSL" in data:
        findings_summary_parts.append(f"SSL status: {data['SSL']}")
    if "Email Found" in data and data["Email Found"]: # Check if not empty
        findings_summary_parts.append(f"exposed email(s): {data['Email Found']}")

    if not findings_summary_parts: # Default if no specific known keys are found
        findings_summary_parts.append("various aspects were assessed")

    findings_str = "; ".join(findings_summary_parts)

    sender_name = sender_name_input.strip()
    if not sender_name:
        sender_name = "[Your Name]" # Default if not provided

    body = f"Dear Client,\n\n" \
           f"Please find attached the vulnerability assessment report for {domain}.\n\n" \
           f"The assessment covered several areas, and key observations include: {findings_str}.\n\n" \
           f"The attached PDF report provides a more detailed overview of all findings and includes actionable recommendations " \
           f"to help enhance your security posture.\n\n" \
           f"We encourage you to review the report at your earliest convenience. Please let us know if you have any questions " \
           f"or would like to discuss the findings further.\n\n" \
           f"Best regards,\n\n" \
           f"{sender_name}"

    return body

if __name__ == '__main__':
    sample_data_1 = {
        "Domain": "securecorp.com",
        "SSL": "Valid, Grade A+",
        "Risk": "Outdated server software on host xyz",
        "Open Ports": "22, 80, 443",
    }
    sender_1 = "Muhammad Talha"

    subject_1 = compose_email_subject(sample_data_1)
    body_1 = compose_email_body(sample_data_1, sender_1)

    print("--- Example 1 ---")
    print(f"Subject: {subject_1}")
    print(f"Body:\n{body_1}\n")

    sample_data_2 = {
        "Domain": "vulnerableapp.net",
        "SSL": "Expired Certificate",
        "Risk": "Critical SQL Injection vulnerability found; SSL Certificate Expired",
        "Email Found": "admin@vulnerableapp.net",
        "Details": "A high severity SQL injection was identified on the login page."
    }
    sender_2 = "Security Team Alpha"

    subject_2 = compose_email_subject(sample_data_2)
    body_2 = compose_email_body(sample_data_2, sender_2)

    print("--- Example 2 ---")
    print(f"Subject: {subject_2}")
    print(f"Body:\n{body_2}\n")

    sample_data_3 = {
        "Target IP": "192.168.1.100", # No "Domain" key
        "Open Services": "FTP (Anonymous login enabled), Telnet (Weak credentials)"
    }
    sender_3 = "Analyst Jane"
    subject_3 = compose_email_subject(sample_data_3)
    body_3 = compose_email_body(sample_data_3, sender_3)
    print("--- Example 3 (No Domain) ---")
    print(f"Subject: {subject_3}")
    print(f"Body:\n{body_3}\n")
