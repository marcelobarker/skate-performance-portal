-- SKATE PERFORMANCE PORTAL V3.8
-- Sessões longas de vídeo + codificação de várias tentativas por vídeo.
-- Não apaga dados existentes.

alter table public.athlete_posts add column if not exists upload_kind text not null default 'single';
alter table public.athlete_posts add column if not exists session_title text;

-- Aumenta o limite do bucket de 150 MB para 2 GB.
-- O limite global do projeto Supabase ainda pode depender do plano/configuração do projeto.
update storage.buckets
set file_size_limit = 2147483648,
    allowed_mime_types = array['video/mp4','video/quicktime','video/webm','video/x-m4v']
where id = 'trick-videos';

create table if not exists public.trick_video_events (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.athlete_posts(id) on delete cascade,
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  trick_id uuid not null references public.tricks(id) on delete restrict,
  timestamp_seconds integer not null default 0 check (timestamp_seconds >= 0),
  result text not null check (result in ('Acerto','Erro')),
  evaluation text check (evaluation in ('Excelente','Bom','Ruim')),
  difficulty text check (difficulty in ('Baixa','Média','Alta')),
  risk text check (risk in ('Baixo','Médio','Alto')),
  speed text check (speed in ('Lento','Médio','Rápido')),
  direction text check (direction is null or direction in ('Frontside','Backside')),
  base text check (base is null or base in ('Regular','Goofy','Switch','Nollie')),
  notes text,
  analyzed_by uuid not null references public.profiles(id),
  created_at timestamptz not null default now()
);
create index if not exists trick_video_events_post_idx on public.trick_video_events(post_id,timestamp_seconds);
create index if not exists trick_video_events_athlete_idx on public.trick_video_events(athlete_id,created_at desc);
create index if not exists trick_video_events_trick_idx on public.trick_video_events(trick_id);
alter table public.trick_video_events enable row level security;

drop policy if exists "video events read" on public.trick_video_events;
create policy "video events read" on public.trick_video_events for select to authenticated using(true);

create or replace function public.save_trick_video_event(
  p_post_id uuid, p_athlete_id uuid, p_trick_id uuid, p_timestamp_seconds integer,
  p_result text, p_evaluation text default null, p_difficulty text default null,
  p_risk text default null, p_speed text default null, p_direction text default null,
  p_base text default null, p_notes text default null
) returns uuid
language plpgsql security definer set search_path=public
as $$
declare v_id uuid; v_allowed boolean;
begin
  select exists(select 1 from public.profiles where id=auth.uid() and status::text='ativo' and role::text in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica')) into v_allowed;
  if not v_allowed then raise exception 'Sem permissão para analisar vídeos'; end if;
  if not exists(select 1 from public.athlete_posts where id=p_post_id and athlete_id=p_athlete_id) then raise exception 'Vídeo/atleta inválido'; end if;
  insert into public.trick_video_events(post_id,athlete_id,trick_id,timestamp_seconds,result,evaluation,difficulty,risk,speed,direction,base,notes,analyzed_by)
  values(p_post_id,p_athlete_id,p_trick_id,greatest(p_timestamp_seconds,0),p_result,p_evaluation,p_difficulty,p_risk,p_speed,p_direction,p_base,nullif(trim(coalesce(p_notes,'')),''),auth.uid())
  returning id into v_id;
  return v_id;
end; $$;
revoke all on function public.save_trick_video_event(uuid,uuid,uuid,integer,text,text,text,text,text,text,text,text) from public;
grant execute on function public.save_trick_video_event(uuid,uuid,uuid,integer,text,text,text,text,text,text,text,text) to authenticated;

create or replace function public.delete_trick_video_event(p_event_id uuid) returns boolean
language plpgsql security definer set search_path=public
as $$
declare v_allowed boolean;
begin
  select exists(select 1 from public.profiles where id=auth.uid() and status::text='ativo' and role::text in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica')) into v_allowed;
  if not v_allowed then raise exception 'Sem permissão para excluir marcações'; end if;
  delete from public.trick_video_events where id=p_event_id;
  return true;
end; $$;
revoke all on function public.delete_trick_video_event(uuid) from public;
grant execute on function public.delete_trick_video_event(uuid) to authenticated;
