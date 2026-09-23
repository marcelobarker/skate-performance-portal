-- PORTAL SELEÇÃO BRASILEIRA DE SKATEBOARDING V4.80
-- Acesso global da equipe técnica a todas as modalidades.
-- Execute UMA VEZ no SQL Editor do Supabase.
-- Não apaga usuários, times, treinos ou arquivos.
--
-- Cargos considerados staff técnico:
-- tecnico, presidente, vice_presidente, chefe_equipe, comissao_tecnica.
-- Familiar continua limitado ao atleta vinculado.
-- Skatista continua limitado aos próprios dados quando aplicável.

-- 1) Helper global de acesso ao atleta.
create or replace function public.can_access_athlete(target_athlete uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select public.is_active_admin()
      or (auth.uid() = target_athlete and public.is_active_user())
      or public.is_technical_staff()
      or public.is_family_of(target_athlete);
$$;

revoke all on function public.can_access_athlete(uuid) from public;
grant execute on function public.can_access_athlete(uuid) to authenticated;

-- 2) Perfis: staff técnico enxerga todos os perfis ATIVOS, independentemente de time/modalidade.
drop policy if exists "staff read all active profiles" on public.profiles;
create policy "staff read all active profiles"
on public.profiles
for select to authenticated
using (
  status = 'ativo' and public.is_technical_staff()
);

-- 3) Times e membros: staff técnico pode consultar toda a estrutura da Seleção.
drop policy if exists "staff read all teams" on public.teams;
create policy "staff read all teams"
on public.teams
for select to authenticated
using (public.is_technical_staff());

drop policy if exists "staff read all team members" on public.team_members;
create policy "staff read all team members"
on public.team_members
for select to authenticated
using (public.is_technical_staff());

-- 4) Histórico: staff técnico lê todos os treinos de todas as modalidades.
drop policy if exists "staff read all training sessions" on public.training_sessions;
create policy "staff read all training sessions"
on public.training_sessions
for select to authenticated
using (public.is_technical_staff());

-- 5) Análise: staff técnico pode salvar treino para qualquer skatista.
drop policy if exists "staff insert all training sessions" on public.training_sessions;
create policy "staff insert all training sessions"
on public.training_sessions
for insert to authenticated
with check (public.is_technical_staff());

-- Mantemos as policies antigas por compatibilidade; esta nova policy amplia o acesso.
-- Como policies SELECT/INSERT são combinadas por OR no PostgreSQL, não é necessário
-- apagar os vínculos antigos para que o acesso global passe a funcionar.

-- 6) CSVs de treino: leitura e upload para qualquer atleta pelo staff técnico.
drop policy if exists "staff read all training csvs" on storage.objects;
create policy "staff read all training csvs"
on storage.objects
for select to authenticated
using (
  bucket_id = 'training-csvs' and public.is_technical_staff()
);

drop policy if exists "staff upload all training csvs" on storage.objects;
create policy "staff upload all training csvs"
on storage.objects
for insert to authenticated
with check (
  bucket_id = 'training-csvs' and public.is_technical_staff()
);

-- 7) PDFs/relatórios: leitura e upload para qualquer atleta pelo staff técnico.
drop policy if exists "staff read all training reports" on storage.objects;
create policy "staff read all training reports"
on storage.objects
for select to authenticated
using (
  bucket_id = 'training-reports' and public.is_technical_staff()
);

drop policy if exists "staff upload all training reports" on storage.objects;
create policy "staff upload all training reports"
on storage.objects
for insert to authenticated
with check (
  bucket_id = 'training-reports' and public.is_technical_staff()
);
