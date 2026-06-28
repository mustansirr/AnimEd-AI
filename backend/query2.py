import asyncio
from app.services.supabase_client import get_supabase_client

client = get_supabase_client()
scenes = client.table("scenes").select("*").eq("video_id", "d0fa3f18-4dc2-40cf-b34e-368c78417cf4").execute().data

for s in scenes:
    print(f"Scene {s['scene_order']}:")
    print(f"Code:\n{s.get('code')}")
    print(f"JSON:\n{s.get('scene_json')}")
    print("-" * 40)
