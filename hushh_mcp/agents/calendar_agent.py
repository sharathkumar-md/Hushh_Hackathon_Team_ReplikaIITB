from .consent_utils import check_consent

def schedule_meeting(details):
    consent_token = details.get("consent_token")
    if not consent_token or not check_consent(consent_token):
        return "Consent not granted. Cannot schedule meeting."
    # ...existing code for scheduling...
    return f"Meeting scheduled with details: {details.get('meeting_info')}"

