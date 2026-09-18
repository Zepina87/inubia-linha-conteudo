#!/usr/bin/env python3
"""O Eco - Modo 7 VIGIA: mede se cada pagina tem analitica (deteccao ESTRITA).
Uso:  python3 verifica_medicao.py <lista.txt> [mais listas...] [--json baseline/vigia-medicao-DATA.json]
Deteccao estrita (tarefa ClickUp 1243w4q56ap do Fabio): GA4 G-XXXXXXXXXX, GTM-XXXXXX, fbq('init'.
O bi-logger interno do Wix (frog.wix.com) NAO conta como medicao.
Estados: MEDIDA / SEM MEDICAO / NAO VERIFICADO. Sai 1 se houver paginas SEM MEDICAO, 2 se nada foi lido.
"""
import re, sys
from _vigia_comum import ler_lista, fetch, guardar_json, arg_json

PADROES = {"ga4": re.compile(r"\bG-[A-Z0-9]{9,12}\b"), "gtm": re.compile(r"\bGTM-[A-Z0-9]{6,9}\b"),
           "meta_pixel": re.compile(r"fbq\(\s*['\"]init['\"]"), "ua_legado": re.compile(r"\bUA-\d{6,10}-\d\b")}

def main(argv):
    rest, saida = arg_json(argv)
    if not rest: print(__doc__); return 2
    urls = [u for l in rest for u in ler_lista(l)]
    res = []; sem = 0; nv = 0
    for u in urls:
        r = fetch(u)
        if r["status"] is None or r["status"] >= 400 or not r["body"]:
            res.append({"url": u, "estado": "NAO VERIFICADO", "status": r["status"], "erro": r["erro"]}); nv += 1; continue
        achados = {k: sorted(set(p.findall(r["body"])))[:3] if k != "meta_pixel" else bool(p.search(r["body"])) for k, p in PADROES.items()}
        wix_bi = "frog.wix.com" in r["body"]
        medida = bool(achados["ga4"] or achados["gtm"] or achados["meta_pixel"])
        estado = "MEDIDA" if medida else "SEM MEDICAO"
        if not medida: sem += 1
        res.append({"url": u, "estado": estado, "status": r["status"], "final_url": r["final_url"], "ga4": achados["ga4"], "gtm": achados["gtm"],
                    "meta_pixel": achados["meta_pixel"], "ua_legado": achados["ua_legado"], "wix_bi_logger_ignorado": wix_bi})
        print(f"{estado:14} {u}  ga4={achados['ga4'] or '-'} gtm={achados['gtm'] or '-'} pixel={achados['meta_pixel']}")
    lidas = len(urls) - nv
    print(f"\nmedicao: {len(urls)} URL, {lidas} lidas, {nv} NAO VERIFICADO, {sem} SEM MEDICAO")
    if saida: guardar_json(saida, {"script": "verifica_medicao", "padroes": {k: p.pattern for k, p in PADROES.items()}, "resultados": res})
    if lidas == 0: return 2
    return 1 if sem else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
