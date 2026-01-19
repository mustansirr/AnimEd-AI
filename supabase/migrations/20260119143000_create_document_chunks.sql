-- Migration: Create document_chunks table for RAG (Retrieval Augmented Generation)
-- This table stores PDF text chunks with vector embeddings for semantic search.
-- Uses gte-small model which produces 384-dimension embeddings.

-- ============================================================================
-- DOCUMENT CHUNKS TABLE
-- Stores text chunks from uploaded PDFs with their embeddings
-- ============================================================================
create table if not exists public.document_chunks (
    id uuid primary key default uuid_generate_v4(),
    video_id uuid references public.videos(id) on delete cascade not null,
    chunk_index int not null,
    content text not null,
    embedding vector(384),  -- gte-small produces 384 dimensions
    created_at timestamp with time zone default now(),
    
    -- Ensure unique chunk index per video
    unique(video_id, chunk_index)
);

-- Add RLS (Row Level Security) policies for document_chunks
alter table public.document_chunks enable row level security;

-- Users can view chunks of their own videos
create policy "Users can view chunks of own videos"
    on public.document_chunks for select
    using (
        exists (
            select 1 from public.videos
            where videos.id = document_chunks.video_id
            and videos.user_id = auth.uid()
        )
    );

-- Users can create chunks for their own videos
create policy "Users can create chunks for own videos"
    on public.document_chunks for insert
    with check (
        exists (
            select 1 from public.videos
            where videos.id = document_chunks.video_id
            and videos.user_id = auth.uid()
        )
    );

-- Users can delete chunks of their own videos
create policy "Users can delete chunks of own videos"
    on public.document_chunks for delete
    using (
        exists (
            select 1 from public.videos
            where videos.id = document_chunks.video_id
            and videos.user_id = auth.uid()
        )
    );

-- ============================================================================
-- INDEXES
-- ============================================================================
-- Index for fast lookup by video_id
create index if not exists idx_document_chunks_video_id 
    on public.document_chunks(video_id);

-- Index for ordering chunks
create index if not exists idx_document_chunks_order 
    on public.document_chunks(video_id, chunk_index);

-- HNSW index for fast vector similarity search
-- Using cosine distance (vector_cosine_ops) for normalized embeddings
create index if not exists idx_document_chunks_embedding 
    on public.document_chunks 
    using hnsw (embedding vector_cosine_ops)
    with (m = 16, ef_construction = 64);

-- ============================================================================
-- MATCH DOCUMENT CHUNKS RPC FUNCTION
-- Performs semantic similarity search for RAG context retrieval
-- ============================================================================
create or replace function public.match_document_chunks(
    query_embedding vector(384),
    target_video_id uuid,
    match_threshold float default 0.5,
    match_count int default 5
)
returns table (
    id uuid,
    video_id uuid,
    chunk_index int,
    content text,
    similarity float
)
language sql stable
as $$
    select
        document_chunks.id,
        document_chunks.video_id,
        document_chunks.chunk_index,
        document_chunks.content,
        1 - (document_chunks.embedding <=> query_embedding) as similarity
    from public.document_chunks
    where document_chunks.video_id = target_video_id
    and 1 - (document_chunks.embedding <=> query_embedding) > match_threshold
    order by (document_chunks.embedding <=> query_embedding) asc
    limit match_count;
$$;

-- Grant execute permission to authenticated users
grant execute on function public.match_document_chunks to authenticated;
