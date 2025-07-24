from hushh_mcp.consent.token import generate_consent_token, verify_consent_token

def request_consent(user_id, action):
    """
    Generate a consent token for a user and action.
    """
    return generate_consent_token(user_id, action)

def check_consent(consent_token):
    """
    Verify if a consent token is valid.
    """
    return verify_consent_token(consent_token)