-- V3.21 — exclusão de vídeo somente pelo Admin
-- Execute uma vez no Supabase SQL Editor.

drop policy if exists "posts owner admin delete" on public.athlete_posts;
drop policy if exists "posts admin delete" on public.athlete_posts;

create policy "posts admin delete"
on public.athlete_posts
for delete
to authenticated
using (
  exists (
    select 1
    from public.profiles p
    where p.id = auth.uid()
      and p.role = 'admin'
  )
);
