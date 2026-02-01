import os
from dotenv import load_dotenv, find_dotenv

print(f"Loading env from: {find_dotenv()}")
load_dotenv(find_dotenv(), override=True)

user = os.getenv("SMTP_USERNAME")
pwd = os.getenv("SMTP_PASSWORD")

print(f"SMTP_USERNAME: {'[SET]' if user else '[MISSING]'}")
print(f"SMTP_PASSWORD: {'[SET]' if pwd else '[MISSING]'}")

if pwd and pwd == "your_app_password":
    print("SMTP_PASSWORD is still the default placeholder!")
elif pwd:
    print(f"Password length: {len(pwd)}")
    print(f"First 2 chars: {pwd[:2]}***")
