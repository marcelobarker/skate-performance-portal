-- Skate Performance Portal V3.2 — Livro de Manobras + Feed/Vídeos
create extension if not exists pgcrypto;

create table if not exists public.trick_categories (
  id uuid primary key default gen_random_uuid(), name text not null unique,
  sort_order integer not null default 0, created_at timestamptz not null default now()
);
create table if not exists public.tricks (
  id uuid primary key default gen_random_uuid(), category_id uuid references public.trick_categories(id) on delete set null,
  name text not null, description text, active boolean not null default true, created_by uuid references auth.users(id), created_at timestamptz not null default now(),
  unique(category_id,name)
);
create table if not exists public.athlete_posts (
  id uuid primary key default gen_random_uuid(), athlete_id uuid not null references public.profiles(id) on delete cascade,
  trick_id uuid references public.tricks(id) on delete set null, video_path text not null, caption text,
  analysis_status text not null default 'aguardando', created_at timestamptz not null default now()
);
create table if not exists public.post_likes (
  post_id uuid references public.athlete_posts(id) on delete cascade, user_id uuid references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now(), primary key(post_id,user_id)
);
create table if not exists public.post_comments (
  id uuid primary key default gen_random_uuid(), post_id uuid not null references public.athlete_posts(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade, body text not null check(char_length(body) between 1 and 800), created_at timestamptz not null default now()
);
insert into public.trick_categories(name,sort_order) values ('Grinds',10),('Slides',20),('Flips',30),('Aéreos',40),('Transição',50),('Outras',99) on conflict(name) do nothing;
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types) values ('trick-videos','trick-videos',false,157286400,array['video/mp4','video/quicktime','video/webm']) on conflict(id) do update set public=false;

alter table public.trick_categories enable row level security; alter table public.tricks enable row level security; alter table public.athlete_posts enable row level security; alter table public.post_likes enable row level security; alter table public.post_comments enable row level security;

drop policy if exists "categories read" on public.trick_categories; create policy "categories read" on public.trick_categories for select to authenticated using(true);
drop policy if exists "categories staff write" on public.trick_categories; create policy "categories staff write" on public.trick_categories for all to authenticated using(exists(select 1 from public.profiles p where p.id=auth.uid() and p.role in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica'))) with check(exists(select 1 from public.profiles p where p.id=auth.uid() and p.role in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica')));
drop policy if exists "tricks read" on public.tricks; create policy "tricks read" on public.tricks for select to authenticated using(true);
drop policy if exists "tricks staff write" on public.tricks; create policy "tricks staff write" on public.tricks for all to authenticated using(exists(select 1 from public.profiles p where p.id=auth.uid() and p.role in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica'))) with check(exists(select 1 from public.profiles p where p.id=auth.uid() and p.role in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica')));
drop policy if exists "posts team read" on public.athlete_posts; create policy "posts team read" on public.athlete_posts for select to authenticated using(true);
drop policy if exists "athlete post insert" on public.athlete_posts; create policy "athlete post insert" on public.athlete_posts for insert to authenticated with check(athlete_id=auth.uid() or exists(select 1 from public.profiles p where p.id=auth.uid() and p.role in ('admin','tecnico','chefe_equipe','comissao_tecnica')));
drop policy if exists "likes read" on public.post_likes; create policy "likes read" on public.post_likes for select to authenticated using(true);
drop policy if exists "likes own" on public.post_likes; create policy "likes own" on public.post_likes for all to authenticated using(user_id=auth.uid()) with check(user_id=auth.uid());
drop policy if exists "comments read" on public.post_comments; create policy "comments read" on public.post_comments for select to authenticated using(true);
drop policy if exists "comments own insert" on public.post_comments; create policy "comments own insert" on public.post_comments for insert to authenticated with check(user_id=auth.uid());
drop policy if exists "comments own delete" on public.post_comments; create policy "comments own delete" on public.post_comments for delete to authenticated using(user_id=auth.uid());

drop policy if exists "video authenticated read" on storage.objects; create policy "video authenticated read" on storage.objects for select to authenticated using(bucket_id='trick-videos');
drop policy if exists "video own upload" on storage.objects; create policy "video own upload" on storage.objects for insert to authenticated with check(bucket_id='trick-videos' and (storage.foldername(name))[1]=auth.uid()::text);
