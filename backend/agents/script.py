from agents.llm import llm

def call_script(issue):
    return llm(f"""
    Generate a polite, professional phone call script to a civic authority.
    
    Context:
    - Issue: {issue['description']}
    - Location: {issue['location']}
    - Authority: {issue.get('authority', 'Civic Authority')}
    
    Rules:
    1. Total spoken length MUST be under 60 seconds.
    2. Start with "Hello, I am calling on behalf of a resident..."
    3. Clearly state the issue and location.
    4. Ask for the procedure to register a formal complaint.
    5. Do NOT promise any specific outcome or timeline.
    6. Do NOT make up case numbers or personal details.
    
    Output:
    Just the spoken script text.
    """)

def email_script(issue):
    return llm(f"""
    Write the body of a formal complaint email.
    Do NOT include a Subject line. Start directly with the salutation.

    Issue: {issue['description']}
    Location: {issue['location']}
    Authority: {issue['authority']}
    """)
