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

## V1.5 — Times completos
- Criar, editar e excluir times.
- Adicionar/remover skatistas e técnicos ativos.
- Visualizar composição do time.
- Execute `supabase_v1_5_migration.sql` uma vez no Supabase após o deploy.


## V1.6 — Atleta + Análise de Treino
- A Análise de Treino agora seleciona skatistas ativos cadastrados no Portal.
- Nome, foto, modalidade, categoria e base são carregados automaticamente do perfil.
- O upload manual de foto/nome na análise foi removido para evitar divergência de cadastro.
- Os CSVs e todos os cálculos/relatórios do dashboard foram preservados.
- Esta versão não grava histórico de CSVs ainda; isso fica para a V1.7.
- Não exige nova migration SQL.

## V1.7 — Histórico de Treinos
- Salva CSVs em bucket privado `training-csvs`.
- Registra cada sessão em `training_sessions` com atleta, data, título e caminho do CSV.
- Nova página `Histórico de Treinos` para consultar, baixar e excluir sessões (admin).
- Execute `supabase_v1_7_migration.sql` uma vez antes de usar o salvamento.


## V1.8 — Perfis e Permissões
- Admin: gestão completa de cadastros, times, atletas e históricos.
- Técnico: visualiza somente times e skatistas aos quais está vinculado; pode consultar análises/histórico desses atletas.
- Skatista: visualiza o próprio perfil/análise/histórico.
- Segurança aplicada no Supabase via RLS, não apenas na interface.
- Execute `supabase_v1_8_migration.sql` uma vez após instalar esta versão.

## V1.9 — Relatórios integrados ao histórico
- Ao salvar um treino novo, o portal arquiva o CSV e também os dois PDFs da análise.
- Histórico permite baixar CSV, relatório PDF e dashboard visual por sessão.
- Filtro por período: todos, 30 dias, 90 dias, ano atual ou personalizado.
- PDFs ficam em bucket privado e seguem as permissões Admin / Técnico / Skatista.
- Sessões salvas antes da V1.9 continuam válidas; elas apenas não possuem PDFs arquivados retroativamente.
- Execute `supabase_v1_9_migration.sql` uma única vez após a V1.8.

## V2.0 — revisão final
- Dashboard visual PDF volta a exibir percentuais diretamente nas pizzas.
- Foto opcional restaurada na Análise de Treino, sem substituir a foto do cadastro.
- Skatistas ficam restritos ao Histórico; Análise/CSV é área de Admin/Técnico.
- Técnicos podem salvar treino somente para skatistas dos próprios times (RLS).
- Controles e botões recebem tema escuro global.
- Home/Central da equipe mostra contagens reais de atletas, técnicos, times, treinos e pendentes (admin).
- Execute `supabase_v2_0_migration.sql` uma vez após atualizar o GitHub.
