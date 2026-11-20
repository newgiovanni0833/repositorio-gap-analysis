"""Análise de gap entre um sistema de origem e o repositório de dados.

Uso:
    python src/gap_analysis.py [pasta_dados] [pasta_saida]   # padrão: dados_exemplo/ e saida/

Para cada campo exibido nas consultas do sistema de origem, classifica:
- Presente                    já existe na tabela correspondente do repositório
- Ausente em tabela existente a tabela existe, falta a coluna
- Sem tabela                  a consulta não tem tabela no repositório (criar)

A comparação ignora acentos, maiúsculas e pontuação: "Data de Início" casa com
"data_inicio".

Saídas: gap_campos.csv, resumo.md e diagrama.html (grafo interativo em D3.js).
Só usa a biblioteca padrão do Python.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

PRESENTE, AUSENTE, SEM_TABELA = "Presente", "Ausente em tabela existente", "Sem tabela"


def chave(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


def ler(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def analisar(origem, mapa, repositorio) -> list[dict[str, str]]:
    tabela_de = {m["consulta"]: m["tabela"].strip() for m in mapa}
    colunas = defaultdict(set)
    for r in repositorio:
        colunas[r["tabela"]].add(chave(r["coluna"]))

    linhas = []
    for o in origem:
        tabela = tabela_de.get(o["consulta"], "")
        if not tabela:
            status, sugestao = SEM_TABELA, "tb_" + chave(o["consulta"])
        elif chave(o["campo"]) in colunas[tabela]:
            status, sugestao = PRESENTE, tabela
        else:
            status, sugestao = AUSENTE, tabela
        linhas.append({
            "dominio": o["dominio"], "consulta": o["consulta"], "campo": o["campo"],
            "coluna_sugerida": chave(o["campo"]), "tabela_destino": sugestao, "status": status,
        })
    return linhas


def resumo_md(linhas) -> str:
    total = len(linhas)
    por_status = Counter(l["status"] for l in linhas)
    por_consulta: dict[str, Counter] = defaultdict(Counter)
    dominio = {}
    for l in linhas:
        por_consulta[l["consulta"]][l["status"]] += 1
        dominio[l["consulta"]] = l["dominio"]

    out = ["# Resumo da análise de gap", "",
           f"- Consultas analisadas: **{len(por_consulta)}**",
           f"- Campos analisados: **{total}**",
           f"- Presentes no repositório: **{por_status[PRESENTE]}** ({por_status[PRESENTE] / total:.0%})",
           f"- Ausentes em tabelas existentes: **{por_status[AUSENTE]}** ({por_status[AUSENTE] / total:.0%})",
           f"- Sem tabela correspondente: **{por_status[SEM_TABELA]}** ({por_status[SEM_TABELA] / total:.0%})",
           "", "## Cobertura por consulta", "",
           "| Domínio | Consulta | Campos | Presentes | Ausentes | Sem tabela | Cobertura |",
           "|---|---|---:|---:|---:|---:|---:|"]
    ordem = sorted(por_consulta, key=lambda c: por_consulta[c][PRESENTE] / sum(por_consulta[c].values()))
    for c in ordem:
        n = por_consulta[c]
        t = sum(n.values())
        out.append(f"| {dominio[c]} | {c} | {t} | {n[PRESENTE]} | {n[AUSENTE]} | {n[SEM_TABELA]} | {n[PRESENTE] / t:.0%} |")

    criar = [c for c in ordem if por_consulta[c][SEM_TABELA]]
    out += ["", "## Backlog de modelagem", "",
            "**1. Tabelas a criar**", ""]
    out += [f"- `tb_{chave(c)}` ({por_consulta[c][SEM_TABELA]} campos) — consulta {c}" for c in criar]
    out += ["", "**2. Colunas a incluir em tabelas existentes** (da menor para a maior cobertura)", ""]
    out += [f"- `tb_{chave(c)}`: {por_consulta[c][AUSENTE]} coluna(s)" for c in ordem if por_consulta[c][AUSENTE]]
    return "\n".join(out) + "\n"


def dados_do_grafo(linhas, relacionamentos=()) -> dict:
    """Nós: consultas e tabelas. Arestas: consulta -> tabela de destino e consulta -> consulta."""
    por_consulta: dict[str, Counter] = defaultdict(Counter)
    info = {}
    for l in linhas:
        por_consulta[l["consulta"]][l["status"]] += 1
        info[l["consulta"]] = (l["dominio"], l["tabela_destino"], l["status"] == SEM_TABELA)

    nos, arestas = [], []
    for c, n in por_consulta.items():
        dominio, tabela, criar = info[c]
        total = sum(n.values())
        nos.append({"id": c, "tipo": "consulta", "dominio": dominio, "campos": total,
                    "presentes": n[PRESENTE], "ausentes": n[AUSENTE], "sem_tabela": n[SEM_TABELA]})
        nos.append({"id": tabela, "tipo": "tabela", "dominio": dominio, "campos": total,
                    "presentes": n[PRESENTE], "ausentes": n[AUSENTE], "sem_tabela": n[SEM_TABELA], "criar": criar})
        arestas.append({"source": c, "target": tabela, "tipo": "tabela", "cobertura": n[PRESENTE] / total, "criar": criar})
    for r in relacionamentos:
        if r["consulta_origem"] in por_consulta and r["consulta_destino"] in por_consulta:
            arestas.append({"source": r["consulta_origem"], "target": r["consulta_destino"], "tipo": "relacao",
                            "campo": r["campo"], "cobertura": 0, "criar": False})
    return {"nos": nos, "arestas": arestas}


def main(dados: Path, saida: Path) -> list[dict[str, str]]:
    linhas = analisar(ler(dados / "campos_origem.csv"), ler(dados / "mapa_consulta_tabela.csv"),
                      ler(dados / "campos_repositorio.csv"))
    saida.mkdir(parents=True, exist_ok=True)

    with (saida / "gap_campos.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]), delimiter=";")
        w.writeheader()
        w.writerows(linhas)

    (saida / "resumo.md").write_text(resumo_md(linhas), encoding="utf-8")

    modelo = (Path(__file__).parent / "diagrama_modelo.html").read_text(encoding="utf-8")
    arq_rel = dados / "relacionamentos.csv"
    relacionamentos = ler(arq_rel) if arq_rel.exists() else []
    grafo = json.dumps(dados_do_grafo(linhas, relacionamentos), ensure_ascii=False)
    (saida / "diagrama.html").write_text(modelo.replace("/*__DADOS__*/null", grafo), encoding="utf-8")

    n = Counter(l["status"] for l in linhas)
    print(f"Campos: {len(linhas)} | presentes: {n[PRESENTE]} | ausentes: {n[AUSENTE]} | sem tabela: {n[SEM_TABELA]}")
    print(f"Saídas gravadas em {saida}/")
    return linhas


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dados_exemplo"),
         Path(sys.argv[2]) if len(sys.argv) > 2 else Path("saida"))
