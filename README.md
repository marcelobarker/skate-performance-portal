# Skate Performance Portal V1

Projeto NOVO e separado do dashboard original.

## O que já está pronto
- Home do portal no mesmo visual do Skate Performance.
- Páginas: Cadastros, Times e Análise de Treino.
- O `03_Analise_de_Treino.py` é uma cópia da V5.9; o projeto original não foi alterado.
- Estrutura SQL para Supabase com usuários, funções, status, times e sessões de treino.
- Fluxo previsto: cadastro -> pendente -> aprovação do administrador -> vínculo com time.

## Próximo passo para ativar cadastros reais
1. Criar um projeto no Supabase.
2. Executar `supabase_schema.sql` no SQL Editor.
3. Configurar `SUPABASE_URL` e `SUPABASE_KEY` nos Secrets do Streamlit.
4. Implementar login/registro e as políticas administrativas.

Importante: não coloque a chave `service_role` no navegador ou no GitHub.
