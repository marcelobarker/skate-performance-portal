-- SKATE PERFORMANCE PORTAL V2.0.1
-- Execute UMA VEZ depois da migration V2.0.
-- Permite que uma única sessão de treino mantenha vários CSVs originais.

alter table public.training_sessions
  add column if not exists csv_paths text[];

-- Compatibilidade: sessões antigas continuam funcionando e passam a ter
-- o CSV antigo também representado na nova lista.
update public.training_sessions
set csv_paths = array[csv_path]
where csv_path is not null
  and (csv_paths is null or cardinality(csv_paths) = 0);
