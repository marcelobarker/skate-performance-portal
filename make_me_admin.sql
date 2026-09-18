
-- DEPOIS de criar sua própria conta pelo Portal, troque o e-mail abaixo pelo SEU e-mail
-- e execute no SQL Editor para transformar somente essa conta em administrador.
update public.profiles
set role = 'admin', status = 'ativo'
where email = 'SEU_EMAIL_AQUI';
