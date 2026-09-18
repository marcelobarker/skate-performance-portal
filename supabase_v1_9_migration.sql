-- SKATE PERFORMANCE PORTAL V1.9
-- Execute UMA VEZ depois da migration V1.8.
-- Arquiva os PDFs de cada sessão e mantém o bucket privado.

alter table public.training_sessions
  add column if not exists report_pdf_path text,
  add column if not exists visual_pdf_path text;

insert into storage.buckets (id, name, public)
values ('training-reports', 'training-reports', false)
on conflict (id) do update set public = false;

-- Admin gerencia todos os relatórios.
drop policy if exists "admin read training reports" on storage.objects;
create policy "admin read training reports" on storage.objects
for select to authenticated using (bucket_id='training-reports' and public.is_active_admin());

drop policy if exists "admin upload training reports" on storage.objects;
create policy "admin upload training reports" on storage.objects
for insert to authenticated with check (bucket_id='training-reports' and public.is_active_admin());

drop policy if exists "admin update training reports" on storage.objects;
create policy "admin update training reports" on storage.objects
for update to authenticated
using (bucket_id='training-reports' and public.is_active_admin())
with check (bucket_id='training-reports' and public.is_active_admin());

drop policy if exists "admin delete training reports" on storage.objects;
create policy "admin delete training reports" on storage.objects
for delete to authenticated using (bucket_id='training-reports' and public.is_active_admin());

-- Skatista lê apenas os próprios PDFs.
drop policy if exists "athlete read own training reports" on storage.objects;
create policy "athlete read own training reports" on storage.objects
for select to authenticated using (
  bucket_id='training-reports' and (storage.foldername(name))[1]=auth.uid()::text
);

-- Técnico lê somente relatórios de atletas com quem compartilha time.
drop policy if exists "technician read assigned training reports" on storage.objects;
create policy "technician read assigned training reports" on storage.objects
for select to authenticated using (
  bucket_id='training-reports'
  and public.is_active_technician()
  and public.shares_team_with(((storage.foldername(name))[1])::uuid)
);
