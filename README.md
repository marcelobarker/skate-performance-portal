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

## V2.0.1
- Vários CSVs enviados juntos agora geram um único treino no Histórico.
- Os CSVs originais ficam vinculados à mesma sessão e podem ser baixados juntos em ZIP.
- Relatório PDF e Dashboard Visual são gerados com os dados consolidados de todos os CSVs do envio.
- Percentuais nas pizzas do Dashboard Visual PDF receberam fonte maior.
- Execute somente `supabase_v2_0_1_migration.sql` ao atualizar da V2.0.

## V2.0.2
- Histórico ganhou **VER ANÁLISE INTERATIVA**: reabre os CSVs arquivados na mesma tela interativa usada no upload original, com seleção de sessão e gráficos clicáveis.
- Skatista continua sem acesso ao upload/análise nova, mas pode abrir a análise de um treino do próprio Histórico.
- Download dos CSVs originais aparece somente para Admin.
- Dashboard Visual PDF: tabela de manobras da primeira página ampliada para a largura do documento e tipografia geral aumentada para melhorar leitura.
- Nenhuma migration nova é necessária nesta versão.


## V2.0.3
- Quadros de manobras das páginas de continuação do Dashboard Visual com as mesmas dimensões e fontes da página 1.
- Download visual do Histórico é regenerado com o motor atual usando os CSVs arquivados.
- Nova página Meu Perfil para atualização dos próprios dados e foto.
- Times de atleta/técnico carregados a partir dos próprios vínculos.
- Central da Equipe virou navegação funcional/clicável.
- Execute `supabase_v2_0_3_migration.sql` uma vez.

## V2.1
- Perfil: data de nascimento, cidade/UF e foto; campo Categoria removido da interface.
- Times: membros em lista visual com foto, função, idade, base e cidade; skatistas enxergam técnicos do próprio time.
- Login: opção “Me manter conectado” usando refresh token de sessão (30 dias; pode expirar/revogar antes).
- Análise: atleta convidado/sem cadastro, data com tema escuro, seletor de sessão visível no conteúdo/mobile e correção do bloco vazio sobre a foto.
- Navegação: Cadastros oculto para Técnico/Skatista e atalho Início em todas as páginas autenticadas.
- Execute `supabase_v2_1_migration.sql` uma vez após subir esta versão.
