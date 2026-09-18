
-- Execute no SQL Editor do Supabase.
create type public.user_role as enum ('admin','skatista','tecnico');
create type public.account_status as enum ('pendente','ativo','bloqueado');

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  email text,
  role public.user_role not null default 'skatista',
  status public.account_status not null default 'pendente',
  modality text,
  stance text,
  category text,
  photo_url text,
  created_at timestamptz not null default now()
);

create table public.teams (
  id bigint generated always as identity primary key,
  name text not null,
  modality text,
  created_at timestamptz not null default now()
);

create table public.team_members (
  team_id bigint references public.teams(id) on delete cascade,
  profile_id uuid references public.profiles(id) on delete cascade,
  primary key(team_id, profile_id)
);

create table public.training_sessions (
  id bigint generated always as identity primary key,
  athlete_id uuid references public.profiles(id) on delete cascade,
  training_date date not null default current_date,
  title text,
  csv_path text,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.teams enable row level security;
alter table public.team_members enable row level security;
alter table public.training_sessions enable row level security;

-- Base segura: cada usuário pode ler o próprio perfil.
create policy "read own profile" on public.profiles
for select using (auth.uid() = id);

-- As políticas administrativas e por time serão adicionadas depois de definir sua conta admin.
