
import asyncio
import httpx
import sys
import os

# Configuration
API_URL = "http://localhost:8000"
VIDEO_ID = "00000000-0000-0000-0000-000000000000" # Dummy UUID for testing if validation is loose, else we need a real one.
# Note: The API validates video_uuid exists in DB. This script assumes the user has a video or we might face 404.
# Let's handle 404 gracefully or create a dummy video if possible (but that requires supabase client).
# For simplicity, we'll ask the user to provide a video ID or just try a dummy and expect a specific error if DB is empty.

async def verify_rag_pipeline(pdf_path: str, video_id: str):
    print(f"Testing RAG Pipeline with:")
    print(f"  PDF: {pdf_path}")
    print(f"  Video ID: {video_id}")
    print("=" * 50)

    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Upload PDF
        print("\n[1] Uploading PDF...")
        try:
            with open(pdf_path, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                data = {"video_id": video_id}
                response = await client.post(f"{API_URL}/api/upload", data=data, files=files)
                
                if response.status_code == 404:
                    print(f"❌ Error 404: {response.text}")
                    print(f"   (Check if video ID {video_id} exists OR if API path is correct)")
                    return
                
                if response.status_code != 201:
                    print(f"❌ Upload failed: {response.status_code} - {response.text}")
                    return
                
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Chunks stored: {result.get('chunks_stored')}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return

        # 2. Test Context Retrieval
        query = "What is the main topic?"
        print(f"\n[2] Testing Context Retrieval (Query: '{query}')...")
        try:
            response = await client.get(
                f"{API_URL}/api/upload/{video_id}/context",
                params={"query": query}
            )
            
            if response.status_code != 200:
                print(f"❌ Retrieval failed: {response.status_code} - {response.text}")
                return

            data = response.json()
            if data['has_context']:
                print("✅ Context retrieved successfully!")
                print(f"   Context snippet: {data['context'][:100]}...")
            else:
                print("⚠️ No context found (might be expected if query is irrelevant).")
                
        except Exception as e:
             print(f"❌ Context retrieval error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/verify_rag.py <path_to_pdf> <valid_video_id>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    video_id = sys.argv[2]
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    asyncio.run(verify_rag_pipeline(pdf_path, video_id))
