-- SKATE PERFORMANCE PORTAL V3.9
-- Reativa manobras previamente excluídas/inativadas em vez de criar duplicatas.
-- Execute somente esta migration depois da V3.8.

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
    -- Se já existe (inclusive inativa), reaproveita o mesmo ID e reativa.
    select id into v_id
      from public.tricks
     where category_id = p_category_id
       and lower(trim(name)) = lower(trim(p_name))
     limit 1;

    if v_id is not null then
      update public.tricks
         set name = trim(p_name),
             description = nullif(trim(coalesce(p_description,'')),''),
             active = true
       where id = v_id;
    else
      insert into public.tricks(category_id,name,description,created_by,active)
      values(p_category_id,trim(p_name),nullif(trim(coalesce(p_description,'')),''),auth.uid(),true)
      returning id into v_id;
    end if;

  elsif p_action = 'update' then
    update public.tricks
       set category_id=p_category_id,
           name=trim(p_name),
           description=nullif(trim(coalesce(p_description,'')),'')
     where id=p_trick_id returning id into v_id;

  elsif p_action = 'delete' then
    -- Soft delete preserva análises históricas que apontam para esta manobra.
    update public.tricks set active=false where id=p_trick_id returning id into v_id;
  else
    raise exception 'Ação inválida';
  end if;
  return v_id;
end;
$$;

revoke all on function public.manage_trick(text,uuid,uuid,text,text) from public;
grant execute on function public.manage_trick(text,uuid,uuid,text,text) to authenticated;
