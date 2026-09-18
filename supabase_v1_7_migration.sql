-- SKATE PERFORMANCE PORTAL V1.7
-- Execute UMA VEZ no SQL Editor do Supabase.
-- Histórico de treinos + armazenamento privado dos CSVs.
-- Não apaga cadastros, times ou análises existentes.

insert into storage.buckets (id, name, public)
values ('training-csvs', 'training-csvs', false)
on conflict (id) do update set public = false;

-- Sessões: admin ativo gerencia tudo; skatista pode ler o próprio histórico.
drop policy if exists "admin read training sessions" on public.training_sessions;
create policy "admin read training sessions" on public.training_sessions
for select to authenticated using (public.is_active_admin());

drop policy if exists "athlete read own training sessions" on public.training_sessions;
create policy "athlete read own training sessions" on public.training_sessions
for select to authenticated using (athlete_id = auth.uid());

drop policy if exists "admin insert training sessions" on public.training_sessions;
create policy "admin insert training sessions" on public.training_sessions
for insert to authenticated with check (public.is_active_admin());

drop policy if exists "admin update training sessions" on public.training_sessions;
create policy "admin update training sessions" on public.training_sessions
for update to authenticated using (public.is_active_admin()) with check (public.is_active_admin());

drop policy if exists "admin delete training sessions" on public.training_sessions;
create policy "admin delete training sessions" on public.training_sessions
for delete to authenticated using (public.is_active_admin());

-- Bucket privado: nesta fase somente o admin manipula os CSVs.
drop policy if exists "admin read training csvs" on storage.objects;
create policy "admin read training csvs" on storage.objects
for select to authenticated
using (bucket_id = 'training-csvs' and public.is_active_admin());

drop policy if exists "admin upload training csvs" on storage.objects;
create policy "admin upload training csvs" on storage.objects
for insert to authenticated
with check (bucket_id = 'training-csvs' and public.is_active_admin());

drop policy if exists "admin update training csvs" on storage.objects;
create policy "admin update training csvs" on storage.objects
for update to authenticated
using (bucket_id = 'training-csvs' and public.is_active_admin())
with check (bucket_id = 'training-csvs' and public.is_active_admin());

drop policy if exists "admin delete training csvs" on storage.objects;
create policy "admin delete training csvs" on storage.objects
for delete to authenticated
using (bucket_id = 'training-csvs' and public.is_active_admin());
