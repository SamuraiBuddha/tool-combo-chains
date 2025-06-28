import os
from dotenv import load_dotenv

print(f"Current directory: {os.getcwd()}")
print(f".env exists: {os.path.exists('.env')}")

load_dotenv()

print(f"DATABASE_URL from env: {os.getenv('DATABASE_URL')}")
print(f"POSTGRES_PASSWORD from env: {os.getenv('POSTGRES_PASSWORD')}")