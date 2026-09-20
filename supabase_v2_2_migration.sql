-- SKATE PERFORMANCE PORTAL V2.2
-- Execute UMA VEZ depois da V2.1. Não apaga dados existentes.
-- Novos cargos + vínculo Familiar -> Atleta + permissões.

alter type public.user_role add value if not exists 'presidente';
alter type public.user_role add value if not exists 'vice_presidente';
alter type public.user_role add value if not exists 'chefe_equipe';
alter type public.user_role add value if not exists 'comissao_tecnica';
alter type public.user_role add value if not exists 'familiar';

create table if not exists public.family_athletes (
  family_id uuid not null references public.profiles(id) on delete cascade,
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (family_id, athlete_id),
  check (family_id <> athlete_id)
);
alter table public.family_athletes enable row level security;

create or replace function public.is_technical_staff()
returns boolean language sql stable security definer set search_path=public as $$
 select exists(select 1 from public.profiles where id=auth.uid() and status='ativo'
   and role::text in ('tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica'));
$$;

create or replace function public.is_family_of(target_athlete uuid)
returns boolean language sql stable security definer set search_path=public as $$
 select exists(select 1 from public.family_athletes fa join public.profiles p on p.id=fa.family_id
   where fa.family_id=auth.uid() and fa.athlete_id=target_athlete and p.status='ativo' and p.role::text='familiar');
$$;

create or replace function public.can_access_athlete(target_athlete uuid)
returns boolean language sql stable security definer set search_path=public as $$
 select public.is_active_admin()
   or (auth.uid()=target_athlete and public.is_active_user())
   or (public.is_technical_staff() and public.shares_team_with(target_athlete))
   or public.is_family_of(target_athlete);
$$;

revoke all on function public.is_technical_staff() from public;
revoke all on function public.is_family_of(uuid) from public;
grant execute on function public.is_technical_staff() to authenticated;
grant execute on function public.is_family_of(uuid) to authenticated;

-- Admin gerencia vínculos; familiar pode enxergar somente seus próprios vínculos.
drop policy if exists "admin manage family links" on public.family_athletes;
create policy "admin manage family links" on public.family_athletes for all to authenticated
using (public.is_active_admin()) with check (public.is_active_admin());
drop policy if exists "family read own links" on public.family_athletes;
create policy "family read own links" on public.family_athletes for select to authenticated
using (family_id=auth.uid());

-- Familiar precisa conseguir ler o perfil do atleta vinculado.
drop policy if exists "family read linked athlete profile" on public.profiles;
create policy "family read linked athlete profile" on public.profiles for select to authenticated
using (status='ativo' and public.is_family_of(id));

-- Histórico: staff técnico do mesmo time e familiar vinculado.
drop policy if exists "technical staff read assigned training sessions" on public.training_sessions;
create policy "technical staff read assigned training sessions" on public.training_sessions for select to authenticated
using (public.is_technical_staff() and public.shares_team_with(athlete_id));
drop policy if exists "family read linked training sessions" on public.training_sessions;
create policy "family read linked training sessions" on public.training_sessions for select to authenticated
using (public.is_family_of(athlete_id));

-- Arquivos privados dos treinos seguem a mesma regra.
drop policy if exists "technical staff read assigned training csvs" on storage.objects;
create policy "technical staff read assigned training csvs" on storage.objects for select to authenticated
using (bucket_id='training-csvs' and public.is_technical_staff() and public.shares_team_with(((storage.foldername(name))[1])::uuid));
drop policy if exists "family read linked training csvs" on storage.objects;
create policy "family read linked training csvs" on storage.objects for select to authenticated
using (bucket_id='training-csvs' and public.is_family_of(((storage.foldername(name))[1])::uuid));

drop policy if exists "technical staff read assigned reports" on storage.objects;
create policy "technical staff read assigned reports" on storage.objects for select to authenticated
using (bucket_id='training-reports' and public.is_technical_staff() and public.shares_team_with(((storage.foldername(name))[1])::uuid));
drop policy if exists "family read linked reports" on storage.objects;
create policy "family read linked reports" on storage.objects for select to authenticated
using (bucket_id='training-reports' and public.is_family_of(((storage.foldername(name))[1])::uuid));

-- Cadastro: permite escolher um atleta ao criar conta Familiar sem expor e-mails/dados privados.
create or replace function public.signup_athletes()
returns table(id uuid, full_name text)
language sql stable security definer set search_path=public as $$
  select p.id,p.full_name from public.profiles p
  where p.role::text='skatista' and p.status='ativo' order by p.full_name;
$$;
grant execute on function public.signup_athletes() to anon, authenticated;

-- Atualiza o trigger de criação para aceitar os novos cargos e criar o vínculo do Familiar.
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path=public as $$
declare requested_role public.user_role; linked uuid; requested_text text;
begin
  requested_text := coalesce(new.raw_user_meta_data->>'role','skatista');
  if requested_text not in ('skatista','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica','familiar') then requested_text := 'skatista'; end if;
  requested_role := requested_text::public.user_role;
  insert into public.profiles(id,full_name,email,role,status,modality)
  values(new.id,coalesce(nullif(new.raw_user_meta_data->>'full_name',''),split_part(new.email,'@',1)),new.email,requested_role,'pendente',new.raw_user_meta_data->>'modality')
  on conflict(id) do nothing;
  if requested_text='familiar' and coalesce(new.raw_user_meta_data->>'linked_athlete_id','')<>'' then
    begin
      linked := (new.raw_user_meta_data->>'linked_athlete_id')::uuid;
      if exists(select 1 from public.profiles where id=linked and role::text='skatista' and status='ativo') then
        insert into public.family_athletes(family_id,athlete_id) values(new.id,linked) on conflict do nothing;
      end if;
    exception when others then null;
    end;
  end if;
  return new;
end; $$;

-- Impede um usuário comum de promover a própria conta alterando role/status diretamente pela API.
create or replace function public.protect_profile_privileges()
returns trigger language plpgsql security definer set search_path=public as $$
begin
  if auth.uid()=old.id and not public.is_active_admin() then
    new.role := old.role;
    new.status := old.status;
    new.email := old.email;
  end if;
  return new;
end; $$;
drop trigger if exists protect_profile_privileges_trigger on public.profiles;
create trigger protect_profile_privileges_trigger before update on public.profiles
for each row execute procedure public.protect_profile_privileges();
