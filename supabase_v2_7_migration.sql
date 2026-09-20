-- V2.7 - configuração visual da Home
create table if not exists public.portal_settings (key text primary key,value text,updated_at timestamptz not null default now());
alter table public.portal_settings enable row level security;
drop policy if exists "authenticated read portal settings" on public.portal_settings;
create policy "authenticated read portal settings" on public.portal_settings for select to authenticated using (true);
drop policy if exists "admin manage portal settings" on public.portal_settings;
create policy "admin manage portal settings" on public.portal_settings for all to authenticated using (public.is_active_admin()) with check (public.is_active_admin());
