# Skate Performance Portal V1.4

V1.4 adiciona gestão completa de perfis sem alterar a página de Análise de Treino.

## Novidades
- edição de nome, modalidade, base e categoria;
- upload de foto de perfil pelo administrador;
- visualização da foto no painel de Cadastros;
- separação por pendentes, ativos e bloqueados;
- aprovação, bloqueio e reativação;
- administrador não pode bloquear a própria conta;
- e-mail de login fica protegido contra edição pelo painel.

## Antes de testar fotos
Execute **uma vez** `supabase_v1_4_migration.sql` no SQL Editor do Supabase.

## Deploy
Suba os arquivos no mesmo repositório do Portal e faça commit. O Streamlit Community Cloud fará o redeploy automaticamente.
