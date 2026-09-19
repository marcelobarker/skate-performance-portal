-- SKATE PERFORMANCE PORTAL V2.0.3
-- Execute UMA VEZ depois da V2.0.1.
-- Permite que cada usuário ativo atualize SOMENTE o próprio perfil e gerencie a própria foto.
-- Não altera role/status e não remove dados.

drop policy if exists "active user update own profile" on public.profiles;
create policy "active user update own profile" on public.profiles
for update to authenticated
using (id=auth.uid() and public.is_active_user())
with check (id=auth.uid() and public.is_active_user());

drop policy if exists "user upload own profile photos" on storage.objects;
create policy "user upload own profile photos" on storage.objects
for insert to authenticated
with check (bucket_id='profile-photos' and (storage.foldername(name))[1]=auth.uid()::text and public.is_active_user());

drop policy if exists "user update own profile photos" on storage.objects;
create policy "user update own profile photos" on storage.objects
for update to authenticated
using (bucket_id='profile-photos' and (storage.foldername(name))[1]=auth.uid()::text and public.is_active_user())
with check (bucket_id='profile-photos' and (storage.foldername(name))[1]=auth.uid()::text and public.is_active_user());
