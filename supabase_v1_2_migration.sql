
-- SKATE PERFORMANCE PORTAL V1.2
-- Execute UMA VEZ no SQL Editor do Supabase, depois do schema inicial.

-- Cria automaticamente public.profiles quando alguém se cadastra no Auth.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
declare
  requested_role public.user_role;
begin
  requested_role :=
    case
      when new.raw_user_meta_data->>'role' = 'tecnico' then 'tecnico'::public.user_role
      else 'skatista'::public.user_role
    end;

  insert into public.profiles (id, full_name, email, role, status, modality)
  values (
    new.id,
    coalesce(nullif(new.raw_user_meta_data->>'full_name',''), split_part(new.email,'@',1)),
    new.email,
    requested_role,
    'pendente',
    new.raw_user_meta_data->>'modality'
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();

-- Usuário autenticado pode consultar o próprio perfil.
drop policy if exists "read own profile" on public.profiles;
create policy "read own profile" on public.profiles
for select to authenticated using (auth.uid() = id);

-- Função segura para identificar administradores ativos.
create or replace function public.is_active_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.profiles
    where id = auth.uid() and role = 'admin' and status = 'ativo'
  );
$$;

revoke all on function public.is_active_admin() from public;
grant execute on function public.is_active_admin() to authenticated;

-- Admin pode visualizar e atualizar todos os perfis.
drop policy if exists "admin read profiles" on public.profiles;
create policy "admin read profiles" on public.profiles
for select to authenticated using (public.is_active_admin());

drop policy if exists "admin update profiles" on public.profiles;
create policy "admin update profiles" on public.profiles
for update to authenticated using (public.is_active_admin()) with check (public.is_active_admin());

-- Times: usuários ativos podem ler; admin pode criar/alterar/apagar.
drop policy if exists "active users read teams" on public.teams;
create policy "active users read teams" on public.teams
for select to authenticated using (
  exists(select 1 from public.profiles p where p.id=auth.uid() and p.status='ativo')
);

drop policy if exists "admin insert teams" on public.teams;
create policy "admin insert teams" on public.teams
for insert to authenticated with check (public.is_active_admin());

drop policy if exists "admin update teams" on public.teams;
create policy "admin update teams" on public.teams
for update to authenticated using (public.is_active_admin()) with check (public.is_active_admin());

drop policy if exists "admin delete teams" on public.teams;
create policy "admin delete teams" on public.teams
for delete to authenticated using (public.is_active_admin());
