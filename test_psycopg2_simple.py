import psycopg2
import sys

# Test connection with psycopg2 (synchronous)
password = '7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH'

print("Testing PostgreSQL connection with psycopg2...")
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="cognitive",
        password=password,
        database="cognitive"
    )
    print("✅ SUCCESS! Connected to PostgreSQL")
    
    cur = conn.cursor()
    cur.execute("SELECT version()")
    version = cur.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    # Check if user exists
    cur.execute("SELECT current_user")
    user = cur.fetchone()
    print(f"Connected as: {user[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)
