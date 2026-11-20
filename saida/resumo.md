# Resumo da análise de gap

- Consultas analisadas: **12**
- Campos analisados: **205**
- Presentes no repositório: **76** (37%)
- Ausentes em tabelas existentes: **83** (40%)
- Sem tabela correspondente: **46** (22%)

## Cobertura por consulta

| Domínio | Consulta | Campos | Presentes | Ausentes | Sem tabela | Cobertura |
|---|---|---:|---:|---:|---:|---:|
| Planejamento | CALENDARIO | 15 | 0 | 0 | 15 | 0% |
| Suporte | ALTERACAO_CANCELAMENTO | 17 | 0 | 0 | 17 | 0% |
| Suporte | CERTIFICADOS | 14 | 0 | 0 | 14 | 0% |
| Financeiro | DESPESAS | 17 | 5 | 12 | 0 | 29% |
| Execução | EVENTOS | 24 | 8 | 16 | 0 | 33% |
| Cadastros | PARCEIROS | 17 | 7 | 10 | 0 | 41% |
| Execução | PARTICIPANTES | 19 | 8 | 11 | 0 | 42% |
| Planejamento | PLANO_ACAO | 17 | 8 | 9 | 0 | 47% |
| Financeiro | FATURAS | 17 | 8 | 9 | 0 | 47% |
| Execução | TURMAS | 16 | 9 | 7 | 0 | 56% |
| Cadastros | INSTRUTORES | 18 | 12 | 6 | 0 | 67% |
| Execução | PRESENCA | 14 | 11 | 3 | 0 | 79% |

## Backlog de modelagem

**1. Tabelas a criar**

- `tb_calendario` (15 campos) — consulta CALENDARIO
- `tb_alteracao_cancelamento` (17 campos) — consulta ALTERACAO_CANCELAMENTO
- `tb_certificados` (14 campos) — consulta CERTIFICADOS

**2. Colunas a incluir em tabelas existentes** (da menor para a maior cobertura)

- `tb_despesas`: 12 coluna(s)
- `tb_eventos`: 16 coluna(s)
- `tb_parceiros`: 10 coluna(s)
- `tb_participantes`: 11 coluna(s)
- `tb_plano_acao`: 9 coluna(s)
- `tb_faturas`: 9 coluna(s)
- `tb_turmas`: 7 coluna(s)
- `tb_instrutores`: 6 coluna(s)
- `tb_presenca`: 3 coluna(s)
