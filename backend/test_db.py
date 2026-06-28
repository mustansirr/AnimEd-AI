import asyncio
from app.services.supabase_client import get_supabase_client

def get_latest_data():
    client = get_supabase_client()
    videos = client.table("videos").select("*").order("created_at", desc=True).limit(1).execute()
    if not videos.data:
        print("No videos found.")
        return
    video = videos.data[0]
    print(f"Latest video ID: {video['id']}")
    print(f"Prompt: {video.get('prompt')}")
    
    scenes = client.table("scenes").select("*").eq("video_id", video['id']).order("scene_order").execute()
    for s in scenes.data:
        print(f"\nScene {s['scene_order']}:")
        print(f"Code preview: {s.get('code')[:200] if s.get('code') else 'None'}...")
        
get_latest_data()
