SIGNATURE_HTML = """
<br>
<hr style="border: none; border-top: 1px solid #ccc;">
<p style="font-family: Arial, sans-serif; font-size: 10pt; color: #555555;">
    <strong>Muhammad Talha</strong><br>
    Cybersecurity Analyst | Vulnerability Assessment Specialist<br>
    🔗 <a href="https://linkedin.com/in/muhammad-talha-cybersecurity" style="color: #0077B5; text-decoration: none;">LinkedIn</a> |
    🌐 <a href="https://github.com/infosectalha" style="color: #333; text-decoration: none;">GitHub</a> |
    📁 <a href="https://sites.google.com/view/muhammadtalha-portfolio/home" style="color: #0077B5; text-decoration: none;">Portfolio</a><br>
    ✉️ infosectalha@gmail.com<br>
    📱 +92-307-1955559
</p>
"""

def get_html_signature():
    """
    Returns the predefined HTML email signature.
    """
    return SIGNATURE_HTML

def append_signature_to_html(html_body_content, signature_html=None):
    """
    Appends the HTML signature to an HTML email body.
    Tries to insert before </body> if present, otherwise appends.

    Args:
        html_body_content (str): The main HTML content of the email body.
        signature_html (str, optional): The HTML signature. Defaults to global SIGNATURE_HTML.

    Returns:
        str: The HTML body content with the signature appended.
    """
    if signature_html is None:
        signature_html = get_html_signature()

    # Ensure there's some content to append to
    if not html_body_content:
        return signature_html # Or perhaps just the body if it's only a signature

    body_lower = html_body_content.lower()
    body_tag_index = body_lower.rfind("</body>")

    if body_tag_index != -1:
        # Insert before the closing </body> tag
        return html_body_content[:body_tag_index] + signature_html + html_body_content[body_tag_index:]
    else:
        # If no </body> tag, just append. This assumes html_body_content is a fragment.
        return html_body_content + signature_html

if __name__ == '__main__':
    # Example Usages
    print("--- Raw Signature ---")
    print(get_html_signature())

    print("\n--- Appending to HTML with </body> tag ---")
    sample_body_with_tag = """
    <html>
        <head><title>Test Email</title></head>
        <body>
            <p>Hello Client,</p>
            <p>This is the main content of the email.</p>
            <p>We hope you find this information useful.</p>
        </body>
    </html>
    """
    print(append_signature_to_html(sample_body_with_tag))

    print("\n--- Appending to HTML fragment (no </body> tag) ---")
    sample_body_fragment = """
    <p>Dear User,</p>
    <p>Here is an update on your account.</p>
    """
    print(append_signature_to_html(sample_body_fragment))

    print("\n--- Appending to an empty body ---")
    empty_body = ""
    print(append_signature_to_html(empty_body))

    print("\n--- Appending to a body that is just whitespace ---")
    whitespace_body = "   \n\t   "
    # The current logic would append after whitespace. This is generally fine.
    # If stricter handling for "empty" (whitespace-only) is needed, html_body_content.strip() check could be added.
    print(append_signature_to_html(whitespace_body))

    # Example of how it might be used with a template that already has a placeholder
    # (though the current append_signature_to_html doesn't use placeholders, it appends)
    # template_with_placeholder = "<p>Email content here.</p>{{ SIGNATURE }}"
    # rendered_template = template_with_placeholder.replace("{{ SIGNATURE }}", get_html_signature())
    # print("\n--- Signature via placeholder replacement (conceptual) ---")
    # print(rendered_template)
    # The current append_signature_to_html is designed to be added to the *output* of a template engine,
    # or to a manually crafted HTML string.
    # If Jinja2 templates are used, the signature can also be included directly in the base template
    # or as a variable/macro in Jinja2, which might be cleaner.
    # For now, this provides a programmatic way to append it.

    # A more robust append_signature_to_html might ensure the main content ends with a newline
    # or that the signature starts with one if not already present, for better visual spacing if concatenated raw.
    # The current SIGNATURE_HTML starts with <br><hr> which helps.

    # Consider if the signature should always be wrapped in its own div or section for styling isolation.
    # The current one uses <p> and inline styles, which is generally good for email client compatibility.
    # Added a <br> and <hr> to the signature itself for better separation.

    styled_body = """
    <html>
        <body>
            <p style="color: blue;">This is some styled content.</p>
        </body>
    </html>
    """
    print("\n--- Appending to styled body ---")
    print(append_signature_to_html(styled_body))
