-- Skate Performance Portal V2.9
-- Adiciona data final opcional aos eventos do calendário.
alter table public.calendar_events
  add column if not exists event_end_date date;

-- Eventos antigos continuam como eventos de um único dia.
update public.calendar_events
set event_end_date = event_date
where event_end_date is null;
