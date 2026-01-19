
import asyncio
import os
from uuid import uuid4
from supabase import create_client, Client

# Usage: python scripts/create_test_video_db.py
# Must set env vars or hardcode for testing if .env not loaded. 
# We'll try to load from .env using python-dotenv if available, or ask user.

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role to bypass RLS if needed, or Anon if policies allow insert

if not url:
    print("❌ Error: SUPABASE_URL not set in environment.")
    print("Please ensure your .env file is set up or export the variables.")
    exit(1)

# Fallback to key if service role not found, though service role is better for seeding
if not key:
    key = os.environ.get("SUPABASE_KEY")

if not key:
    print("❌ Error: SUPABASE_KEY (or SUPABASE_SERVICE_ROLE_KEY) not set.")
    exit(1)

async def create_dummy_video():
    print(f"Connecting to Supabase at {url}...")
    supabase: Client = create_client(url, key)
    
    # 1. Create a Dummy User (required for foreign key constraint)
    print("Creating dummy user in auth.users...")
    dummy_email = f"test_user_{uuid4()}@example.com"
    dummy_password = "password123"
    
    try:
        # Use admin auth to create user (requires service_role key)
        user_response = supabase.auth.admin.create_user({
            "email": dummy_email,
            "password": dummy_password,
            "email_confirm": True
        })
        user_id = user_response.user.id
        print(f"✅ Created Dummy User: {user_id} ({dummy_email})")
        
    except Exception as e:
        print(f"⚠️ Could not create new user (might duplicate or auth error): {e}")
        print("Attempting to list users to find an existing one...")
        try:
            users_response = supabase.auth.admin.list_users()
            if users_response and users_response.users:
                user_id = users_response.users[0].id
                print(f"Using existing user: {user_id}")
            else:
                print("❌ No users found and failed to create one. Cannot proceed.")
                return
        except Exception as list_err:
             print(f"❌ Failed to list users: {list_err}")
             return

    # 2. Create Video
    data = {
        "user_id": user_id,
        "prompt": "Test video for RAG verification",
        "status": "planning"
    }
    
    try:
        print("Inserting test video...")
        response = supabase.table("videos").insert(data).execute()
        if response.data:
            video_id = response.data[0]['id']
            print(f"\n✅ Created Test Video!")
            print(f"Video ID: {video_id}")
            print(f"User ID:  {user_id}")
            print("\nUse this Video ID for the verification script:")
            print(f"python scripts/verify_rag.py <path_to_pdf> {video_id}")
        else:
            print("❌ Failed to create video. No data returned.")
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        print("\nTip: Check if 'videos' table exists and RLS policies allow insertion.")

if __name__ == "__main__":
    asyncio.run(create_dummy_video())
