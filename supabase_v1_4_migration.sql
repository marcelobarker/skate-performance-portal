-- SKATE PERFORMANCE PORTAL V1.4
-- Execute UMA VEZ no SQL Editor do Supabase antes de usar upload de fotos.
-- Não apaga tabelas nem cadastros existentes.

-- Bucket público somente para fotos de perfil.
insert into storage.buckets (id, name, public)
values ('profile-photos', 'profile-photos', true)
on conflict (id) do update set public = true;

-- Apenas administrador ativo pode enviar/alterar/remover fotos neste bucket.
drop policy if exists "admin upload profile photos" on storage.objects;
create policy "admin upload profile photos"
on storage.objects for insert
to authenticated
with check (bucket_id = 'profile-photos' and public.is_active_admin());

drop policy if exists "admin update profile photos" on storage.objects;
create policy "admin update profile photos"
on storage.objects for update
to authenticated
using (bucket_id = 'profile-photos' and public.is_active_admin())
with check (bucket_id = 'profile-photos' and public.is_active_admin());

drop policy if exists "admin delete profile photos" on storage.objects;
create policy "admin delete profile photos"
on storage.objects for delete
to authenticated
using (bucket_id = 'profile-photos' and public.is_active_admin());
