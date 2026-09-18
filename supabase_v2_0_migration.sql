-- SKATE PERFORMANCE PORTAL V2.0
-- Execute UMA VEZ depois da V1.9.
-- Permite que técnicos salvem treinos/CSVs/PDFs SOMENTE para skatistas dos seus próprios times.
-- Não remove dados existentes.

-- Sessões: técnico pode inserir apenas para atleta com quem compartilha time.
drop policy if exists "technician insert assigned training sessions" on public.training_sessions;
create policy "technician insert assigned training sessions" on public.training_sessions
for insert to authenticated
with check (
  public.is_active_technician()
  and public.shares_team_with(athlete_id)
);

-- CSV privado: técnico pode enviar somente para pasta UUID de atleta do próprio time.
drop policy if exists "technician upload assigned training csvs" on storage.objects;
create policy "technician upload assigned training csvs" on storage.objects
for insert to authenticated
with check (
  bucket_id='training-csvs'
  and public.is_active_technician()
  and public.shares_team_with(((storage.foldername(name))[1])::uuid)
);

-- PDFs privados: mesma regra do CSV.
drop policy if exists "technician upload assigned training reports" on storage.objects;
create policy "technician upload assigned training reports" on storage.objects
for insert to authenticated
with check (
  bucket_id='training-reports'
  and public.is_active_technician()
  and public.shares_team_with(((storage.foldername(name))[1])::uuid)
);
