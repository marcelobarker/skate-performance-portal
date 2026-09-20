-- SKATE PERFORMANCE PORTAL V2.4 — Calendário
create table if not exists public.calendar_events (
  id bigint generated always as identity primary key,
  title text not null,
  event_date date not null,
  location text,
  event_type text,
  notes text,
  created_by uuid references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now()
);
alter table public.calendar_events enable row level security;
drop policy if exists "active users read calendar" on public.calendar_events;
create policy "active users read calendar" on public.calendar_events for select to authenticated using (public.is_active_user());
drop policy if exists "active users create calendar" on public.calendar_events;
create policy "active users create calendar" on public.calendar_events for insert to authenticated with check (public.is_active_user() and created_by=auth.uid());
drop policy if exists "owners update calendar" on public.calendar_events;
create policy "owners update calendar" on public.calendar_events for update to authenticated using (created_by=auth.uid() or public.is_active_admin()) with check (created_by=auth.uid() or public.is_active_admin());
drop policy if exists "owners delete calendar" on public.calendar_events;
create policy "owners delete calendar" on public.calendar_events for delete to authenticated using (created_by=auth.uid() or public.is_active_admin());
