#!/usr/bin/env python3
"""O Eco - Modo 7 VIGIA: conta o "ccao" errado por pagina e por palavra. SO LE; nunca escreve no site.
Uso:  python3 verifica_ortografia.py <lista.txt|url> [--json saida.json] [--substituicoes]
As 16 grafias legitimas com c etimologico (marca-inubia.md, seccao 5) NAO contam:
accao accoes proteccao deteccao interaccao interaccoes direccao friccao prospeccao projeccao seleccao
reaccao redaccao correccao seccao inspeccao (e os plurais/derivados directos).
Sai 1 se houver ocorrencias erradas, 0 se zero, 2 se nada foi lido. O --aplicar nao existe de proposito:
corrigir e trabalho no WordPress, de quem tem acesso, com backup.
"""
import re, sys, unicodedata
from collections import Counter
from _vigia_comum import ler_lista, fetch, texto_visivel, guardar_json, arg_json

LEGITIMAS = {"acção", "acções", "protecção", "protecções", "detecção", "detecções", "interacção", "interacções", "direcção", "direcções",
             "fricção", "fricções", "prospecção", "prospecções", "projecção", "projecções", "selecção", "selecções", "reacção", "reacções",
             "redacção", "redacções", "correcção", "correcções", "secção", "secções", "inspecção", "inspecções",
             "acçao", "convicção", "convicções", "ficção", "dicção", "jurisdicção", "restricção", "transacção", "transacções", "infecção", "infecções",
             "objecção", "objecções", "colecção", "colecções", "confecção", "afecção", "predilecção", "intersecção", "coacção", "abstracção", "extracção", "extracções", "refracção", "distracção"}
PADRAO = re.compile(r"\b(\w*cç(?:ão|ões|oes|ao)\w*)\b", re.I | re.U)

def norm(p): return unicodedata.normalize("NFC", p.lower())

def main(argv):
    rest, saida = arg_json(argv)
    subs = "--substituicoes" in rest; rest = [a for a in rest if a != "--substituicoes"]
    if not rest: print(__doc__); return 2
    urls = []
    for a in rest: urls += ler_lista(a) if not a.startswith("http") else [a]
    total = Counter(); por_pag = []; nv = 0
    for u in urls:
        r = fetch(u)
        if r["status"] is None or r["status"] >= 400 or not r["body"]:
            por_pag.append({"url": u, "estado": "NAO VERIFICADO", "status": r["status"]}); nv += 1; continue
        txt = texto_visivel(r["body"])
        c = Counter(norm(m) for m in PADRAO.findall(txt) if norm(m) not in LEGITIMAS)
        total.update(c)
        por_pag.append({"url": u, "estado": "LIDA", "ocorrencias": sum(c.values()), "palavras": dict(c.most_common())})
        print(f"{sum(c.values()):5}  {u}")
    lidas = len(urls) - nv; n = sum(total.values())
    print(f"\nortografia: {len(urls)} URL, {lidas} lidas, {nv} NAO VERIFICADO, {n} ocorrencias erradas em {sum(1 for p in por_pag if p.get('ocorrencias'))} paginas, {len(total)} palavras distintas")
    if total:
        print("palavra errada -> correcta (top 25):")
        for w, k in total.most_common(25): print(f"  {k:4}  {w}  ->  {w.replace('cç', 'ç')}")
    if saida: guardar_json(saida, {"script": "verifica_ortografia", "total": n, "palavras": dict(total.most_common()), "substituicoes": {w: w.replace('cç', 'ç') for w in total}, "paginas": por_pag})
    if lidas == 0: return 2
    return 1 if n else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
