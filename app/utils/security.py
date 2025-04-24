from flask import session

def validate_form(form_data):
    """Validates CSRF token and returns cleaned form data."""
    token = form_data.get('csrf_token')
    if token != session.get('csrf_token'):
        return None, {"error": "CSRF token mismatch"}

    cleaned_data = dict(form_data)
    cleaned_data.pop('csrf_token', None)
    return cleaned_data, None

