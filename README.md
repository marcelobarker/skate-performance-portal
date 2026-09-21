Skate Performance Portal V3.14

# Skate Performance Portal V3.11

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

## V2.2
- Data de nascimento exibida/editada em DD/MM/AAAA.
- Tema escuro reforçado para botões, menus e popovers.
- Foto dos membros do time ampliada em modal interno pelo botão 👁.
- Novos cargos: Presidente, Vice-presidente, Chefe de Equipe, Comissão Técnica e Familiar.
- Admin pode alterar cargos em Cadastros.
- Familiar escolhe um atleta no cadastro e acessa somente o histórico/treinos desse atleta; admin pode corrigir o vínculo depois.
- Staff técnico continua limitado aos atletas dos times aos quais pertence; Admin mantém controle total.

Execute somente `supabase_v2_2_migration.sql` ao atualizar da V2.1.

## V2.5 — Premium Design System
- Design system global dark navy/electric blue/cyan aplicado em todas as páginas.
- Home reconstruída com hero esportivo, KPIs premium, acesso rápido, atletas, próximos eventos e últimos treinos.
- Botões, inputs, uploads, calendários, dialogs, tabs e sidebar padronizados; nenhum botão branco.
- Responsividade reforçada para mobile/tablet mantendo a mesma linguagem visual.
- Sem migration nova: usa a estrutura do banco da V2.4.

## V2.9
- Calendário com data inicial e data final de evento (executar `supabase_v2_9_migration.sql` uma vez).
- Sessão persistente revisada para o modo "Me manter conectado".
- Cards neon da Home e cards de Acesso rápido navegáveis; botões duplicados removidos.
- Menu rápido expansível no topo para mobile e botão Início azul no mobile.
- Dashboard interativo responsivo no mobile (gráficos empilhados, sem pizzas cortadas).
- Fontes ampliadas no relatório PDF e no Dashboard Visual PDF; histórico regenera PDFs com o motor atual.
- Administrador identificado também como membro do Staff e incluído na contagem de Técnicos/Staff.


## V3.0
Correções verificáveis: cards Home navegáveis, menu mobile global, data final de evento, dashboard mobile responsivo e PDFs com fontes maiores. A Home exibe “Portal V3.0” para confirmar o deploy.

## V3.2
- Calendário redesenhado com período inicial/final e tema dark consistente.
- Perfil/feed do atleta com vídeos, curtidas e comentários.
- Livro de Manobras por categorias.
- Envio de manobras em vídeo pelo atleta.
- Requer executar `supabase_v3_2_migration.sql` uma vez.

## V3.4
- Restaura o visual aprovado dos cards neon e Acesso rápido da Home; navegação passa a usar st.switch_page por overlay transparente, sem links HTML.
- Atalho explícito Perfil/Feed para atletas na Home e em Times.
- Calendário refeito sem expander/select mensal: Data inicial + Data final sempre visíveis e navegação mensal por setas.


V3.5: corrige RLS do Livro de Manobras e impede erros de banco de derrubarem a página. Execute supabase_v3_5_migration.sql uma vez.

## V3.8 — sessões longas de vídeo
- Upload de sessão completa ou tentativa isolada.
- Limite do portal/bucket configurado para até 2 GB por vídeo (sujeito ao limite global do plano Supabase).
- Codificação de várias tentativas dentro do mesmo vídeo com timestamp, manobra, Acerto/Erro, avaliação, dificuldade, risco, velocidade, direção e base.
- Resultados das marcações alimentam a página de Análise do atleta.

## V3.12 — vídeos no Google Drive CBSk
- Upload de vídeos grandes diretamente do navegador para a pasta configurada em `GOOGLE_DRIVE_FOLDER_ID`.
- Google Drive usa conta de serviço guardada apenas nos Secrets do Streamlit.
- Supabase continua guardando metadados, feed e codificação; novos `video_path` usam `gdrive:<file_id>`.
- Feed e tela de codificação reconhecem vídeos antigos do Supabase e novos do Google Drive.
- Não há migration SQL nova nesta versão.
- Secrets necessários: `GOOGLE_DRIVE_FOLDER_ID` e `[gcp_service_account]`.


## V3.18
- Excluir vídeo: atleta proprietário ou Admin; remove também o arquivo do Drive.
- Confirmação antes da exclusão.
- Botão para reabrir sidebar permanece visível após recolher.
- Execute supabase_v3_18_migration.sql uma vez.

## V3.19
- Corrige ImportError de `drive_player_geometry` com fallback compatível.
- Remove a navegação automática do Streamlit e usa um menu lateral explícito.
- Menu principal: Home, Times, Feed, Calendário, Meu Perfil, Enviar Vídeo e Central de Performance conforme o cargo.
- Análise, Histórico, Perfil do Atleta, Livro de Manobras e Codificação não aparecem mais no menu.
- Cadastros também não aparece no menu principal; Admin usa apenas `Cargos e cadastros` na seção Administração.

## V3.20
- Remove a navegação móvel duplicada que estava aparecendo no desktop.
- Menu lateral controlado: sem Análise, Codificação ou Cadastros redundantes no menu principal.
- Codificação usa o player oficial do Google Drive para evitar o vídeo travado em 0:00.
- Player de codificação compacto (máx. 560 px).
- Sem migration nova.

## V3.21
- Exclusão de vídeo disponível somente para Admin.
- Interface reduzida para um único botão `Excluir vídeo`.
- Removidos expander, checkbox e textos extras de exclusão.
- Execute `supabase_v3_21_migration.sql` para restringir também a permissão no banco.


## V3.22
- Codificação: remove definitivamente o player HTML5 antigo em 0:00 para vídeos do Drive e usa o player oficial do Google Drive.
- Timestamp manual temporário (Minuto/Segundo), sem promessa de captura automática incorreta.
- Home: marca atualizada para Skate Performance Brasil.
- Sem migration nova.

## V3.22 FIXED
- Corrige o botão de reabrir a sidebar após recolher.
- Compatível com seletores novos (`collapsedControl` / `Open sidebar`) e antigos do Streamlit.
- Mantém o botão de expansão fixo e clicável no canto superior esquerdo.
- Preserva as demais correções da V3.22 (player da codificação + Skate Performance Brasil).
- Sem migration nova.

## V3.23
- Sidebar fixada aberta no desktop para eliminar definitivamente o estado em que o menu desaparecia.
- Botão de recolher removido; o menu não pode mais ficar preso fechado.
- `initial_sidebar_state="expanded"` aplicado às páginas que configuram a página.
- Mantém V3.22: Skate Performance Brasil e player do Drive na Codificação.
- Sem migration nova.

## V3.24
- Sidebar: removidos Codificar Sessão, Análise de Treino, Cadastros e Perfil do Atleta.
- Essas páginas continuam disponíveis pelos fluxos internos/administrativos apropriados.
- Codificação: player responsivo para vertical/horizontal.
- Adicionado relógio visual automático de sessão; por limitação cross-origin do Google Drive, o iframe oficial não fornece currentTime ao Streamlit.
- Mantido ajuste manual de timestamp recolhido como fallback para gravação confiável.
- Sem migration nova.

## V3.25 — correção urgente de navegação
- Desativa definitivamente a navegação automática multipage do Streamlit (`showSidebarNavigation=false`).
- Remove do menu principal: Cadastros, Análise de Treino, Histórico de Treinos, Perfil do Atleta, Livro de Manobras e Codificar Sessão.
- Menu principal fica: Home, Times, Feed, Calendário, Meu Perfil, Enviar Vídeo e Central de Performance (conforme cargo).
- Admin mantém `Cargos e cadastros` somente em Administração, no final, junto de `Gerenciar times`.
- Oculta restos de navegação mobile/legada duplicada no web.
- Sem migration nova.

## V3.26 — correção da Codificação
- Remove o relógio paralelo de codificação, que não correspondia à timeline real do vídeo.
- Restaura os botões grandes ACERTO e ERRO.
- Timestamp volta a representar somente o tempo real da timeline do vídeo.
- Enquanto o player for o iframe oficial do Google Drive, Minuto/Segundo ficam disponíveis para registrar a posição real pausada.
- Player continua responsivo para vertical/horizontal.
- Sem migration nova.
