"""Gera o cenário fictício da análise de gap.

Uso:
    python scripts/gerar_dados_exemplo.py [pasta]      # padrão: dados_exemplo/

Cria quatro arquivos:
- campos_origem.csv       dominio;consulta;campo     (como o sistema de origem exibe)
- mapa_consulta_tabela.csv consulta;tabela           (vazio quando não há tabela no repositório)
- campos_repositorio.csv  tabela;coluna              (o que já existe no repositório)
- relacionamentos.csv     consulta_origem;campo;consulta_destino  (campos que apontam para outra consulta)

O sistema de origem usa rótulos "humanos" ("Data de Início") e o repositório usa
snake_case ("data_inicio"), como acontece na prática.
"""
from __future__ import annotations

import csv
import random
import re
import sys
import unicodedata
from pathlib import Path

COMUNS = ["ID interno", "Status", "Data de Criação", "Data de Atualização", "Usuário Responsável",
          "Observações", "Código Externo", "Município", "Regional"]

CONSULTAS = {
    "Planejamento": {
        "PLANO_ACAO": ["Ano de Referência", "Meta de Eventos", "Meta de Participantes", "Orçamento Previsto",
                       "Área Temática", "Não Planejado", "Data de Aprovação", "Versão do Plano"],
        "CALENDARIO": ["Data", "Dia Útil", "Feriado", "Descrição do Feriado", "Semana do Ano", "Período Letivo"],
    },
    "Execução": {
        "EVENTOS": ["Título do Evento", "Data de Início", "Data de Término", "Carga Horária", "Local do Evento",
                    "Zona", "Modalidade", "Vagas Ofertadas", "Hora de Conclusão", "Estrutura Própria", "Modular",
                    "Curso Vinculado", "Instrutor Principal", "Parceiro Local", "Plano de Ação"],
        "TURMAS": ["Evento", "Número da Turma", "Turno", "Vagas", "Data de Início", "Data de Término", "Sala"],
        "PARTICIPANTES": ["Evento", "Nome", "Data de Nascimento", "Sexo", "Escolaridade", "Situação Final",
                          "Nota Final", "Frequência", "Data da Inscrição", "Telefone"],
        "PRESENCA": ["Participante", "Turma", "Data da Aula", "Presente", "Justificativa"],
    },
    "Financeiro": {
        "FATURAS": ["Evento", "Número da Fatura", "Valor Bruto", "Valor Líquido", "Data de Emissão",
                    "Data de Pagamento", "Retenção de Impostos", "Centro de Custo"],
        "DESPESAS": ["Evento", "Tipo de Despesa", "Valor", "Data da Despesa", "Fornecedor", "Quantidade de Diárias",
                     "Quilometragem", "Comprovante Anexado"],
    },
    "Cadastros": {
        "INSTRUTORES": ["Nome", "Categoria", "Escolaridade", "Data de Credenciamento", "Situação do Cadastro",
                        "Área de Atuação", "Telefone", "E-mail", "Treinamento Metodológico"],
        "PARCEIROS": ["Nome", "Categoria do Parceiro", "Nome do Presidente", "Telefone", "E-mail",
                      "Máximo de Eventos por Mês", "Necessita de Mobilização", "Homologado"],
    },
    "Suporte": {
        "ALTERACAO_CANCELAMENTO": ["Evento", "Tipo de Solicitação", "Motivo", "Data da Solicitação",
                                   "Solicitante", "Aprovador", "Data da Decisão", "Nova Data de Início"],
        "CERTIFICADOS": ["Participante", "Evento", "Número do Certificado", "Data de Emissão", "Código de Validação"],
    },
}

# campo de uma consulta que referencia outra consulta
RELACIONAMENTOS = [
    ("TURMAS", "Evento", "EVENTOS"), ("PARTICIPANTES", "Evento", "EVENTOS"),
    ("PRESENCA", "Participante", "PARTICIPANTES"), ("PRESENCA", "Turma", "TURMAS"),
    ("FATURAS", "Evento", "EVENTOS"), ("DESPESAS", "Evento", "EVENTOS"),
    ("ALTERACAO_CANCELAMENTO", "Evento", "EVENTOS"),
    ("CERTIFICADOS", "Evento", "EVENTOS"), ("CERTIFICADOS", "Participante", "PARTICIPANTES"),
    ("EVENTOS", "Instrutor Principal", "INSTRUTORES"), ("EVENTOS", "Parceiro Local", "PARCEIROS"),
    ("EVENTOS", "Plano de Ação", "PLANO_ACAO"), ("EVENTOS", "Data de Início", "CALENDARIO"),
]

SEM_TABELA = {"CALENDARIO", "ALTERACAO_CANCELAMENTO", "CERTIFICADOS"}
# fração dos campos de cada consulta que já está no repositório
COBERTURA = {"EVENTOS": 0.30, "PLANO_ACAO": 0.45, "TURMAS": 0.55, "PARTICIPANTES": 0.40, "PRESENCA": 0.80,
             "FATURAS": 0.50, "DESPESAS": 0.25, "INSTRUTORES": 0.60, "PARCEIROS": 0.35}


def snake(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


def main(pasta: Path, semente: int = 7) -> None:
    rnd = random.Random(semente)
    pasta.mkdir(parents=True, exist_ok=True)
    origem, mapa, repo = [], [], []

    for dominio, consultas in CONSULTAS.items():
        for consulta, especificos in consultas.items():
            campos = COMUNS + especificos
            origem += [[dominio, consulta, c] for c in campos]
            if consulta in SEM_TABELA:
                mapa.append([consulta, ""])
                continue
            tabela = "tb_" + consulta.lower()
            mapa.append([consulta, tabela])
            presentes = rnd.sample(campos, round(len(campos) * COBERTURA[consulta]))
            if "ID interno" not in presentes:
                presentes.append("ID interno")
            repo += [[tabela, snake(c)] for c in campos if c in presentes]
            repo.append([tabela, "dt_carga"])            # coluna técnica que só existe no repositório

    for nome, cab, linhas in [("campos_origem.csv", ["dominio", "consulta", "campo"], origem),
                              ("mapa_consulta_tabela.csv", ["consulta", "tabela"], mapa),
                              ("campos_repositorio.csv", ["tabela", "coluna"], repo),
                              ("relacionamentos.csv", ["consulta_origem", "campo", "consulta_destino"],
                               [list(r) for r in RELACIONAMENTOS])]:
        with (pasta / nome).open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(cab)
            w.writerows(linhas)
        print(f"{nome}: {len(linhas)} linha(s)")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dados_exemplo"))
