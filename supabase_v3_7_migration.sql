-- SKATE PERFORMANCE PORTAL V3.7
-- Operações seguras do Livro de Manobras via RPC SECURITY DEFINER.
-- Não apaga dados existentes.

create or replace function public.manage_trick(
  p_action text,
  p_trick_id uuid default null,
  p_category_id uuid default null,
  p_name text default null,
  p_description text default null
) returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  v_id uuid;
  v_allowed boolean;
begin
  select exists(
    select 1 from public.profiles
    where id = auth.uid()
      and status::text = 'ativo'
      and role::text in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica')
  ) into v_allowed;
  if not v_allowed then raise exception 'Sem permissão para gerenciar o Livro de Manobras'; end if;

  if p_action = 'insert' then
    insert into public.tricks(category_id,name,description,created_by)
    values(p_category_id,trim(p_name),nullif(trim(coalesce(p_description,'')),''),auth.uid())
    returning id into v_id;
  elsif p_action = 'update' then
    update public.tricks set category_id=p_category_id,name=trim(p_name),description=nullif(trim(coalesce(p_description,'')),'')
    where id=p_trick_id returning id into v_id;
  elsif p_action = 'delete' then
    delete from public.tricks where id=p_trick_id returning id into v_id;
  else
    raise exception 'Ação inválida';
  end if;
  return v_id;
end;
$$;

create or replace function public.add_trick_category(p_name text,p_sort_order integer default 100)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare v_id uuid; v_allowed boolean;
begin
  select exists(select 1 from public.profiles where id=auth.uid() and status::text='ativo' and role::text in ('admin','tecnico','presidente','vice_presidente','chefe_equipe','comissao_tecnica')) into v_allowed;
  if not v_allowed then raise exception 'Sem permissão para gerenciar categorias'; end if;
  insert into public.trick_categories(name,sort_order) values(trim(p_name),p_sort_order) returning id into v_id;
  return v_id;
end;
$$;

revoke all on function public.manage_trick(text,uuid,uuid,text,text) from public;
grant execute on function public.manage_trick(text,uuid,uuid,text,text) to authenticated;
revoke all on function public.add_trick_category(text,integer) from public;
grant execute on function public.add_trick_category(text,integer) to authenticated;
