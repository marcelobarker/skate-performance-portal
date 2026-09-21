-- SKATE PERFORMANCE PORTAL V3.11
-- Permite upload de vídeos por atleta e por toda a equipe técnica autorizada.
-- Execute uma única vez no SQL Editor do Supabase.

drop policy if exists "video own upload" on storage.objects;
drop policy if exists "video own or staff upload" on storage.objects;

create policy "video own or staff upload"
on storage.objects for insert to authenticated
with check (
  bucket_id = 'trick-videos'
  and (
    (storage.foldername(name))[1] = auth.uid()::text
    or exists (
      select 1 from public.profiles p
      where p.id = auth.uid()
        and p.status::text = 'ativo'
        and p.role::text in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica')
    )
  )
);
