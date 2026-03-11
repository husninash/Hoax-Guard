-- Run this in your Supabase SQL Editor

-- 1. Enable pgvector extension
create extension if not exists vector;

-- 2. Create the documents table for RAG
create table if not exists documents (
    id bigserial primary key,
    content text,
    title text,
    source text,
    url text,
    metadata jsonb,
    embedding vector(1536), -- Assuming OpenAI embeddings (text-embedding-3-small)
    created_at timestamp with time zone default now()
);

-- 3. Create a function for similarity search
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  title text,
  content text,
  source text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    documents.id,
    documents.title,
    documents.content,
    documents.source,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
end;
$$;
