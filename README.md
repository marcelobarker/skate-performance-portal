# Skate Performance Portal V1.2

V1.2 conecta o portal ao Supabase:
- Login e criação de conta.
- Cadastro como Skatista ou Técnico.
- Novas contas entram como PENDENTE.
- Usuário pendente não acessa áreas internas.
- Painel ADMIN aprova, bloqueia e reativa usuários.
- Times gravados no Supabase.
- Análise de Treino preservada e protegida por login.
- Projeto antigo continua separado.

## Antes de testar
1. No Supabase SQL Editor, execute `supabase_v1_2_migration.sql` UMA VEZ.
2. Atualize o GitHub com os arquivos V1.2.
3. Aguarde o Streamlit redeploy.
4. Crie a SUA conta pelo Portal.
5. Abra `make_me_admin.sql`, substitua `SEU_EMAIL_AQUI` pelo e-mail da sua conta e execute no SQL Editor.
6. Saia e entre novamente no Portal.

Os Secrets esperados no Streamlit são `SUPABASE_URL` e `SUPABASE_KEY`.
Nunca coloque Secret/Service Role Key no GitHub.
