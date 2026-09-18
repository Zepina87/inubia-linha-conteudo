#!/usr/bin/env python3
"""O Eco - Modo 7 VIGIA mensal e Modo 8 ALVOS: inventario de metadados por pagina.
Uso:  python3 inventaria_paginas.py <lista.txt|url> [...] [--json saida.json] [--csv saida.csv]
Por pagina: status, title (e comprimento), description (e comprimento), canonical, H1, tipos JSON-LD,
hreflang, palavras visiveis, data (article:published_time / dateModified / lastmod), robots.
Estados: LIDA / NAO VERIFICADO. Zero escrita.
"""
import csv, re, sys
from _vigia_comum import ler_lista, fetch, texto_visivel, title, meta, canonical, h1s, jsonld_tipos, guardar_json, arg_json

def main(argv):
    rest, saida = arg_json(argv)
    csv_out = None
    if "--csv" in rest:
        i = rest.index("--csv"); csv_out = rest[i + 1]; rest = rest[:i] + rest[i + 2:]
    if not rest: print(__doc__); return 2
    urls = []
    for a in rest: urls += ler_lista(a) if not a.startswith("http") else [a]
    res = []
    for u in urls:
        r = fetch(u)
        if r["status"] is None or not r["body"]:
            res.append({"url": u, "estado": "NAO VERIFICADO", "status": r["status"], "erro": r["erro"]}); print(f"NAO VERIFICADO {u}"); continue
        b = r["body"]; t = title(b); d = meta(b, "description")
        hl = sorted(set(re.findall(r'hreflang=["\']([^"\']+)["\']', b, re.I)))
        data = meta(b, "article:published_time") or meta(b, "article:modified_time")
        m = re.search(r'"date(?:Modified|Published)"\s*:\s*"([^"]+)"', b)
        if not data and m: data = m.group(1)
        vis = texto_visivel(b)
        res.append({"url": u, "estado": "LIDA", "status": r["status"], "final_url": r["final_url"], "title": t, "title_len": len(t) if t else 0,
                    "description": d, "description_len": len(d) if d else 0, "canonical": canonical(b), "h1": h1s(b), "jsonld": jsonld_tipos(b),
                    "hreflang": hl, "robots": meta(b, "robots"), "palavras": len(vis.split()), "data": data,
                    "ccao_errado": len([w for w in re.findall(r"\b\w*cç(?:ão|ões)\w*\b", vis, re.I) if not re.match(r"(acç|protecç|detecç|interacç|direcç|fricç|prospecç|projecç|selecç|reacç|redacç|correcç|secç|inspecç)", w, re.I)])})
        print(f"{r['status']} {u}  title={len(t) if t else 0}c desc={len(d) if d else 0}c h1={len(h1s(b))} jsonld={','.join(jsonld_tipos(b)) or '-'} palavras={len(vis.split())}")
    lidas = sum(1 for x in res if x["estado"] == "LIDA")
    print(f"\ninventario: {len(urls)} URL, {lidas} lidas · sem title {sum(1 for x in res if x['estado']=='LIDA' and not x['title'])} · sem description {sum(1 for x in res if x['estado']=='LIDA' and not x['description'])} · sem canonical {sum(1 for x in res if x['estado']=='LIDA' and not x['canonical'])} · sem JSON-LD {sum(1 for x in res if x['estado']=='LIDA' and not x['jsonld'])} · sem hreflang {sum(1 for x in res if x['estado']=='LIDA' and not x['hreflang'])}")
    if saida: guardar_json(saida, {"script": "inventaria_paginas", "resultados": res})
    if csv_out:
        with open(csv_out, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f); w.writerow(["url", "status", "title", "title_len", "description_len", "canonical", "h1", "jsonld", "hreflang", "palavras", "data", "ccao_errado"])
            for x in res:
                if x["estado"] == "LIDA": w.writerow([x["url"], x["status"], x["title"], x["title_len"], x["description_len"], x["canonical"], " | ".join(x["h1"]), ",".join(x["jsonld"]), ",".join(x["hreflang"]), x["palavras"], x["data"], x["ccao_errado"]])
        print(f"csv: {csv_out}")
    return 0 if lidas else 2

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
