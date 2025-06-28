import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("POSTGRES_PASSWORD")
db_url = os.getenv("DATABASE_URL")

print("=== Password Analysis ===")
print(f"Password: {password}")
print(f"Length: {len(password)}")
print(f"Repr: {repr(password)}")
print(f"Hex: {password.encode().hex()}")

print("\n=== Extracted from DATABASE_URL ===")
# Extract password from DATABASE_URL
if db_url:
    parts = db_url.split('@')[0].split(':')
    if len(parts) >= 3:
        url_password = parts[2].replace('//cognitive', '')
        print(f"URL Password: {url_password}")
        print(f"Matches POSTGRES_PASSWORD: {url_password == password}")
        print(f"URL Password Hex: {url_password.encode().hex()}")

print("\n=== Check for hidden characters ===")
for i, char in enumerate(password):
    if ord(char) < 32 or ord(char) > 126:
        print(f"Non-printable character at position {i}: {ord(char)}")
