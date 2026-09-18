#!/usr/bin/env python3
"""O Eco - Modo 7 VIGIA: ligacoes de saida (redes sociais e externas) de cada pagina, com o codigo HTTP.
Uso:  python3 verifica_ligacoes.py <lista.txt> [--so-sociais] [--json saida.json]
Regra: o LinkedIn devolve 999 a robots e o Instagram/Facebook redireccionam para login. Isso e
NAO VERIFICADO, nunca OK. Um 404 lido e FALHA. Sai 1 se houver FALHA, 2 se nada foi lido.
Nascido da tarefa 1243w4q56ay do Fabio: o LinkedIn do rodape de inubia.pt deu 404 durante meses.
"""
import re, sys
from urllib.parse import urlparse
from _vigia_comum import ler_lista, fetch, guardar_json, arg_json

SOCIAIS = ("linkedin.com", "instagram.com", "facebook.com", "youtube.com", "youtu.be", "x.com", "twitter.com", "tiktok.com")
BLOQUEIAM_ROBOTS = ("linkedin.com", "instagram.com", "facebook.com")

def main(argv):
    rest, saida = arg_json(argv)
    so_sociais = "--so-sociais" in rest; rest = [a for a in rest if a != "--so-sociais"]
    if not rest: print(__doc__); return 2
    urls = [u for l in rest for u in ler_lista(l)]
    ligacoes = {}; res_pag = []; nv_pag = 0
    for u in urls:
        r = fetch(u)
        if r["status"] is None or r["status"] >= 400 or not r["body"]:
            res_pag.append({"url": u, "estado": "NAO VERIFICADO", "status": r["status"]}); nv_pag += 1; continue
        dom = urlparse(u).netloc.replace("www.", "")
        hrefs = set(re.findall(r'href=["\']([^"\'#]+)["\']', r["body"], re.I))
        ext = sorted(h for h in hrefs if h.startswith("http") and dom not in urlparse(h).netloc)
        if so_sociais: ext = [h for h in ext if any(s in h for s in SOCIAIS)]
        res_pag.append({"url": u, "estado": "LIDA", "externas": ext})
        for h in ext: ligacoes.setdefault(h, set()).add(u)
    resultados = []; falhas = 0
    for h, paginas in sorted(ligacoes.items()):
        host = urlparse(h).netloc
        if any(b in host for b in BLOQUEIAM_ROBOTS):
            rr = fetch(h)
            estado = "NAO VERIFICADO (a plataforma bloqueia robots; confirmar dentro da conta)"
            # o LinkedIn devolve 404 mesmo a robots quando o slug nao existe: isso ja e sinal
            if rr["status"] == 404: estado = "FALHA 404 (lido mesmo com bloqueio: o slug nao existe)"; falhas += 1
            resultados.append({"ligacao": h, "estado": estado, "status": rr["status"], "em_paginas": len(paginas), "exemplo": sorted(paginas)[0]})
        else:
            rr = fetch(h)
            if rr["status"] is None: estado = "NAO VERIFICADO"
            elif rr["status"] < 400: estado = "OK"
            else: estado = f"FALHA {rr['status']}"; falhas += 1
            resultados.append({"ligacao": h, "estado": estado, "status": rr["status"], "final_url": rr["final_url"], "em_paginas": len(paginas), "exemplo": sorted(paginas)[0]})
        print(f"{resultados[-1]['estado'][:40]:40} {h}  ({len(paginas)} pag.)")
    print(f"\nligacoes: {len(urls)} paginas, {len(urls)-nv_pag} lidas, {len(ligacoes)} ligacoes externas distintas, {falhas} FALHA")
    if saida: guardar_json(saida, {"script": "verifica_ligacoes", "paginas": res_pag, "ligacoes": resultados})
    if len(urls) - nv_pag == 0: return 2
    return 1 if falhas else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
