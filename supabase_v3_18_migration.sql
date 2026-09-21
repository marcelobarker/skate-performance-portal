-- V3.18 — exclusão de vídeos/posts
-- Execute uma vez no Supabase SQL Editor.
drop policy if exists "posts owner admin delete" on public.athlete_posts;
create policy "posts owner admin delete"
on public.athlete_posts
for delete to authenticated
using (
  athlete_id = auth.uid()
  or exists (
    select 1 from public.profiles p
    where p.id = auth.uid() and p.role = 'admin'
  )
);
