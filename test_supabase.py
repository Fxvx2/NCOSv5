from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://example.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-or-service-key")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client created successfully!")
except Exception as e:
    print(f"Error creating Supabase client: {e}") 