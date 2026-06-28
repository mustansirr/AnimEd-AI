import asyncio
from app.services.supabase_client import get_supabase_client

client = get_supabase_client()
scenes = client.table("scenes").select("*").eq("video_id", "e3447516-f30f-4f64-8ac2-4a5a2cf31146").execute().data

for s in scenes:
    print(f"Scene {s['scene_order']}:")
    print(f"Code:\n{s.get('code')}")
    print(f"JSON:\n{s.get('scene_json')}")
    print("-" * 40)
