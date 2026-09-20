-- V3.3 — permite Admin/Técnico enviar vídeo em nome de atleta
drop policy if exists "video own upload" on storage.objects;
create policy "video own or staff upload" on storage.objects for insert to authenticated
with check (bucket_id='trick-videos' and (
  (storage.foldername(name))[1]=auth.uid()::text
  or exists(select 1 from public.profiles p where p.id=auth.uid() and p.role in ('admin','tecnico'))
));
