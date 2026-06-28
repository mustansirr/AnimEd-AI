import asyncio
from app.services.supabase_client import get_supabase_client

client = get_supabase_client()
videos = client.table("videos").select("*").execute().data

for v in videos:
    print(f"Video: {v['prompt']} (ID: {v['id']})")
    scenes = client.table("scenes").select("*").eq("video_id", v["id"]).execute().data
    for s in scenes:
        print(f"  Scene {s['scene_order']}:")
        print(f"    Code: {s.get('code', '')[:100]}...")
        if 'scene_json' in s:
            print(f"    JSON: {s['scene_json']}")
