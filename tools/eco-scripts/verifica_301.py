#!/usr/bin/env python3
"""O Eco - Modo 7 VIGIA pos-migracao: cada linha do mapa de 301 resolve para o destino certo?
Uso:  python3 verifica_301.py <mapa.csv> [--json saida.json]
CSV com cabecalho: origem,destino[,tema,nota]. Para cada origem segue a cadeia salto a salto.
Estados: OK (1 salto 301/308 para o destino) / OK COM CADEIA (chega, mas em >1 salto) /
FALHA DESTINO (chega a outro lado) / FALHA 404 / NAO VERIFICADO (sem resposta). Sai 1 se houver FALHA.
"""
import csv, sys
from urllib.parse import urlparse
from _vigia_comum import cadeia_redirects, guardar_json, arg_json

def normaliza(u): 
    p = urlparse(u); return (p.netloc.replace("www.", "").lower(), p.path.rstrip("/") or "/")

def main(argv):
    rest, saida = arg_json(argv)
    if not rest: print(__doc__); return 2
    res = []; falhas = 0; nv = 0
    with open(rest[0], encoding="utf-8") as f:
        for row in csv.DictReader(f):
            o, d = row["origem"].strip(), row["destino"].strip()
            if not o or not d or d.upper().startswith(("A CRIAR", "MORRE", "NOINDEX")): 
                res.append({"origem": o, "destino": d, "estado": "SEM VERIFICACAO (destino nao e URL)"}); continue
            cad = cadeia_redirects(o)
            ultimo = cad[-1]
            if ultimo["status"] is None: estado = "NAO VERIFICADO"; nv += 1
            elif ultimo["status"] == 404: estado = "FALHA 404"; falhas += 1
            elif normaliza(ultimo["url"]) == normaliza(d) and ultimo["status"] < 400:
                estado = "OK" if len(cad) == 2 else ("OK SEM REDIRECT (ja e o destino)" if len(cad) == 1 else f"OK COM CADEIA ({len(cad)-1} saltos)")
            else: estado = f"FALHA DESTINO (chegou a {ultimo['url']})"; falhas += 1
            res.append({"origem": o, "destino": d, "estado": estado, "cadeia": cad})
            print(f"{estado[:34]:34} {o} -> {d}")
    print(f"\n301: {len(res)} linhas, {falhas} FALHA, {nv} NAO VERIFICADO")
    if saida: guardar_json(saida, {"script": "verifica_301", "resultados": res})
    return 1 if falhas else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
