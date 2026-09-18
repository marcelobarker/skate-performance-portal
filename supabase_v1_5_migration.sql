-- SKATE PERFORMANCE PORTAL V1.5
-- Execute UMA VEZ no SQL Editor do Supabase.
-- Habilita a gestão completa de Times e seus membros.
-- Não apaga times, perfis ou cadastros existentes.

-- Usuários ativos podem visualizar a composição dos times.
drop policy if exists "active users read team members" on public.team_members;
create policy "active users read team members" on public.team_members
for select to authenticated using (
  exists(select 1 from public.profiles p where p.id = auth.uid() and p.status = 'ativo')
);

-- Apenas administrador ativo pode adicionar/remover membros.
drop policy if exists "admin insert team members" on public.team_members;
create policy "admin insert team members" on public.team_members
for insert to authenticated with check (public.is_active_admin());

drop policy if exists "admin delete team members" on public.team_members;
create policy "admin delete team members" on public.team_members
for delete to authenticated using (public.is_active_admin());

-- Usuários ativos precisam conseguir ler os perfis ativos para exibir nomes nos times.
drop policy if exists "active users read active profiles" on public.profiles;
create policy "active users read active profiles" on public.profiles
for select to authenticated using (
  status = 'ativo' and exists(
    select 1 from public.profiles me where me.id = auth.uid() and me.status = 'ativo'
  )
);
