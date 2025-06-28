import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from signature_handler import get_html_signature # To make signature available to templates

# Define the path to the templates directory
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

class TemplateManager:
    def __init__(self, template_dir=TEMPLATE_DIR):
        if not os.path.exists(template_dir):
            # Fallback if running from a different CWD, though TEMPLATE_DIR should be robust
            alt_template_dir = 'templates'
            if os.path.exists(alt_template_dir):
                self.template_dir = alt_template_dir
            else:
                # In a critical scenario, we might raise an error or log this.
                # For now, assume TEMPLATE_DIR works or 'templates' relative to CWD.
                # If 'templates' dir is missing, FileSystemLoader will raise TemplateNotFound.
                self.template_dir = template_dir
        else:
            self.template_dir = template_dir

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        # Add signature to global context for all templates
        self.env.globals['SIGNATURE_HTML'] = get_html_signature()

    def list_templates(self):
        """
        Lists available HTML templates in the template directory.
        """
        try:
            return [f for f in os.listdir(self.template_dir) if f.endswith('.html') and not f.startswith('.')]
        except FileNotFoundError:
            print(f"Error: Template directory not found at {self.template_dir}")
            return []

    def render_template(self, template_name, context=None):
        """
        Renders a Jinja2 template with the given context.

        Args:
            template_name (str): The filename of the template (e.g., 'cold_outreach.html').
            context (dict, optional): A dictionary of variables to pass to the template.

        Returns:
            str: The rendered HTML content.
            None: If the template is not found or an error occurs.
        """
        if context is None:
            context = {}

        try:
            template = self.env.get_template(template_name)
            # The signature is already in env.globals, so it's available directly in templates.
            # No need to explicitly add it to 'context' here unless overriding per-render.
            return template.render(context)
        except Exception as e: # Catches jinja2.exceptions.TemplateNotFound and other render errors
            print(f"Error rendering template '{template_name}': {e}")
            return None

if __name__ == '__main__':
    # Create dummy templates for testing
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)

    with open(os.path.join(TEMPLATE_DIR, "test_template1.html"), "w") as f:
        f.write("""
        <html>
            <head><title>{{ title }}</title></head>
            <body>
                <h1>Hello, {{ name }}!</h1>
                <p>{{ custom_note }}</p>
                <p>This is a test template.</p>
                {{ SIGNATURE_HTML | safe }}
            </body>
        </html>
        """)

    with open(os.path.join(TEMPLATE_DIR, "test_template2.html"), "w") as f:
        f.write("""
        <p>Dear {{ contact_person | default('Valued Client') }},</p>
        <p>This is another template with a special offer: {{ offer_details }}</p>
        <p>Regards</p>
        {{ SIGNATURE_HTML | safe }}
        """)

    # Test TemplateManager
    manager = TemplateManager()

    print("Available Templates:")
    templates = manager.list_templates()
    if templates:
        for tpl in templates:
            print(f"- {tpl}")
    else:
        print("No templates found (or directory issue). Check TEMPLATE_DIR.")

    print("\n--- Rendering test_template1.html ---")
    context1 = {
        "title": "My First Email",
        "name": "John Doe",
        "custom_note": "We noticed your SSL certificate is about to expire."
    }
    rendered1 = manager.render_template("test_template1.html", context1)
    if rendered1:
        print(rendered1)
    else:
        print("Failed to render test_template1.html")

    print("\n--- Rendering test_template2.html ---")
    context2 = {
        "contact_person": "Jane Smith",
        "offer_details": "Get 20% off on your next scan!"
    }
    rendered2 = manager.render_template("test_template2.html", context2)
    if rendered2:
        print(rendered2)
    else:
        print("Failed to render test_template2.html")

    print("\n--- Rendering test_template2.html (with default contact_person) ---")
    context3 = {
        "offer_details": "A free consultation."
    }
    rendered3 = manager.render_template("test_template2.html", context3)
    if rendered3:
        print(rendered3)
    else:
        print("Failed to render test_template2.html with default.")

    print("\n--- Rendering non-existent template ---")
    rendered_non_existent = manager.render_template("non_existent_template.html", {})
    if rendered_non_existent is None:
        print("Correctly handled non-existent template.")

    # Clean up dummy templates (optional)
    # try:
    #     os.remove(os.path.join(TEMPLATE_DIR, "test_template1.html"))
    #     os.remove(os.path.join(TEMPLATE_DIR, "test_template2.html"))
    #     # If TEMPLATE_DIR was created by this script and is empty, consider removing it
    #     if not os.listdir(TEMPLATE_DIR) and TEMPLATE_DIR == os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'):
    #         # Be cautious with rmdir, ensure it's the one we might have created
    #         # os.rmdir(TEMPLATE_DIR) # Only if it's empty
    #         pass
    # except OSError as e:
    #     print(f"Error cleaning up dummy templates: {e}")
