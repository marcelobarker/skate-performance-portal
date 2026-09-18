-- SKATE PERFORMANCE PORTAL V1.8
-- Execute UMA VEZ no SQL Editor do Supabase, depois da V1.7.
-- Permissões por perfil: Admin / Técnico / Skatista.
-- Não apaga usuários, times, membros, treinos ou arquivos.

-- Helpers SECURITY DEFINER evitam recursão das policies RLS.
create or replace function public.is_active_user()
returns boolean language sql stable security definer set search_path = public as $$
  select exists(select 1 from public.profiles where id=auth.uid() and status='ativo');
$$;

create or replace function public.is_active_technician()
returns boolean language sql stable security definer set search_path = public as $$
  select exists(select 1 from public.profiles where id=auth.uid() and role='tecnico' and status='ativo');
$$;

create or replace function public.shares_team_with(target_profile uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists(
    select 1 from public.team_members mine
    join public.team_members theirs on theirs.team_id=mine.team_id
    where mine.profile_id=auth.uid() and theirs.profile_id=target_profile
  );
$$;

create or replace function public.is_member_of_team(target_team bigint)
returns boolean language sql stable security definer set search_path = public as $$
  select exists(select 1 from public.team_members where team_id=target_team and profile_id=auth.uid());
$$;

create or replace function public.can_access_athlete(target_athlete uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select public.is_active_admin()
      or (auth.uid()=target_athlete and public.is_active_user())
      or (public.is_active_technician() and public.shares_team_with(target_athlete));
$$;

revoke all on function public.is_active_user() from public;
revoke all on function public.is_active_technician() from public;
revoke all on function public.shares_team_with(uuid) from public;
revoke all on function public.is_member_of_team(bigint) from public;
revoke all on function public.can_access_athlete(uuid) from public;
grant execute on function public.is_active_user() to authenticated;
grant execute on function public.is_active_technician() to authenticated;
grant execute on function public.shares_team_with(uuid) to authenticated;
grant execute on function public.is_member_of_team(bigint) to authenticated;
grant execute on function public.can_access_athlete(uuid) to authenticated;

-- PROFILES: remove leitura ampla da V1.5.1. Admin continua com a policy própria;
-- cada usuário lê a si mesmo; técnico lê somente atletas/staff que compartilham time.
drop policy if exists "active users read active profiles" on public.profiles;
drop policy if exists "technician read team profiles" on public.profiles;
create policy "technician read team profiles" on public.profiles
for select to authenticated using (
  status='ativo' and public.is_active_technician() and public.shares_team_with(id)
);

-- TIMES: admin lê tudo; demais usuários ativos só veem times dos quais participam.
drop policy if exists "active users read teams" on public.teams;
drop policy if exists "members read own teams" on public.teams;
create policy "members read own teams" on public.teams
for select to authenticated using (
  public.is_active_admin() or (public.is_active_user() and public.is_member_of_team(id))
);

-- TEAM MEMBERS: admin lê tudo; membros veem somente a composição dos próprios times.
drop policy if exists "active users read team members" on public.team_members;
drop policy if exists "members read own team members" on public.team_members;
create policy "members read own team members" on public.team_members
for select to authenticated using (
  public.is_active_admin() or (public.is_active_user() and public.is_member_of_team(team_id))
);

-- TREINOS: técnico pode ler sessões dos skatistas que compartilham time.
drop policy if exists "technician read assigned training sessions" on public.training_sessions;
create policy "technician read assigned training sessions" on public.training_sessions
for select to authenticated using (
  public.is_active_technician() and public.shares_team_with(athlete_id)
);

-- CSVs privados: atleta acessa os próprios arquivos; técnico, os atletas do seu time.
-- O primeiro diretório do caminho é sempre o UUID do atleta (criado pela V1.7).
drop policy if exists "athlete read own training csvs" on storage.objects;
create policy "athlete read own training csvs" on storage.objects
for select to authenticated using (
  bucket_id='training-csvs' and (storage.foldername(name))[1]=auth.uid()::text
);

drop policy if exists "technician read assigned training csvs" on storage.objects;
create policy "technician read assigned training csvs" on storage.objects
for select to authenticated using (
  bucket_id='training-csvs'
  and public.is_active_technician()
  and public.shares_team_with(((storage.foldername(name))[1])::uuid)
);
