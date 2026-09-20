-- SKATE PERFORMANCE PORTAL V2.1
-- Execute UMA VEZ depois da V2.0.3. Não apaga dados existentes.
alter table public.profiles add column if not exists birth_date date;
alter table public.profiles add column if not exists city text;
alter table public.profiles add column if not exists state text;

-- Membros ativos do mesmo time precisam enxergar os perfis uns dos outros
-- (inclusive skatista vendo seu técnico). shares_team_with é SECURITY DEFINER.
drop policy if exists "members read shared team profiles" on public.profiles;
create policy "members read shared team profiles" on public.profiles
for select to authenticated using (
  status='ativo' and public.is_active_user() and public.shares_team_with(id)
);
