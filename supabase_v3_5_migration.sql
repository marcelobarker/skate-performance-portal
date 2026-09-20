-- SKATE PERFORMANCE PORTAL V3.5
-- Correção das permissões (RLS) do Livro de Manobras.
-- Execute UMA VEZ depois das migrations V3.2/V3.3.
-- Não apaga manobras, categorias, vídeos, usuários ou treinos.

-- Usa os helpers SECURITY DEFINER já existentes no portal para consultar o cargo
-- sem depender das policies de leitura da própria tabela profiles.
create or replace function public.can_manage_trick_library()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(public.is_active_admin(), false)
      or coalesce(public.is_technical_staff(), false);
$$;

revoke all on function public.can_manage_trick_library() from public;
grant execute on function public.can_manage_trick_library() to authenticated;

-- Categorias
DROP POLICY IF EXISTS "categories staff write" ON public.trick_categories;
DROP POLICY IF EXISTS "categories staff insert" ON public.trick_categories;
DROP POLICY IF EXISTS "categories staff update" ON public.trick_categories;
DROP POLICY IF EXISTS "categories staff delete" ON public.trick_categories;

CREATE POLICY "categories staff insert" ON public.trick_categories
FOR INSERT TO authenticated
WITH CHECK (public.can_manage_trick_library());

CREATE POLICY "categories staff update" ON public.trick_categories
FOR UPDATE TO authenticated
USING (public.can_manage_trick_library())
WITH CHECK (public.can_manage_trick_library());

CREATE POLICY "categories staff delete" ON public.trick_categories
FOR DELETE TO authenticated
USING (public.can_manage_trick_library());

-- Manobras
DROP POLICY IF EXISTS "tricks staff write" ON public.tricks;
DROP POLICY IF EXISTS "tricks staff insert" ON public.tricks;
DROP POLICY IF EXISTS "tricks staff update" ON public.tricks;
DROP POLICY IF EXISTS "tricks staff delete" ON public.tricks;

CREATE POLICY "tricks staff insert" ON public.tricks
FOR INSERT TO authenticated
WITH CHECK (public.can_manage_trick_library());

CREATE POLICY "tricks staff update" ON public.tricks
FOR UPDATE TO authenticated
USING (public.can_manage_trick_library())
WITH CHECK (public.can_manage_trick_library());

CREATE POLICY "tricks staff delete" ON public.tricks
FOR DELETE TO authenticated
USING (public.can_manage_trick_library());
