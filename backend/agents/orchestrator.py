from agents.email import send
from agents.call import call_authority
from agents.web import report_via_web

def run(issue, channel, recipient=None):
    """
    Android-Compatible Orchestrator.
    Routes the request to the correct agent function.
    """
    if channel == "EMAIL":
        return send(issue, recipient)
    elif channel == "CALL":
        return call_authority(issue)
    elif channel == "WEB":
        return report_via_web(issue)
    else:
        return {"error": "Invalid channel"}
