-- Skate Performance Portal V3.6 — análise técnica dos vídeos enviados
create table if not exists public.trick_video_analyses (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null unique references public.athlete_posts(id) on delete cascade,
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  trick_id uuid references public.tricks(id) on delete set null,
  result text not null check (result in ('Acerto','Erro')),
  evaluation text check (evaluation in ('Excelente','Bom','Ruim')),
  difficulty text check (difficulty in ('Baixa','Média','Alta')),
  risk text check (risk in ('Baixo','Médio','Alto')),
  speed text check (speed in ('Lento','Médio','Rápido')),
  direction text check (direction is null or direction in ('Frontside','Backside')),
  base text check (base is null or base in ('Regular','Goofy','Switch','Nollie')),
  notes text,
  analyzed_by uuid references public.profiles(id),
  analyzed_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.trick_video_analyses enable row level security;
drop policy if exists "video analyses read" on public.trick_video_analyses;
create policy "video analyses read" on public.trick_video_analyses for select to authenticated using (true);
drop policy if exists "video analyses staff insert" on public.trick_video_analyses;
create policy "video analyses staff insert" on public.trick_video_analyses for insert to authenticated
with check (public.can_manage_trick_library() and analyzed_by=auth.uid());
drop policy if exists "video analyses staff update" on public.trick_video_analyses;
create policy "video analyses staff update" on public.trick_video_analyses for update to authenticated
using (public.can_manage_trick_library()) with check (public.can_manage_trick_library() and analyzed_by=auth.uid());
create index if not exists trick_video_analyses_athlete_idx on public.trick_video_analyses(athlete_id, analyzed_at desc);
create index if not exists trick_video_analyses_trick_idx on public.trick_video_analyses(trick_id);
