#!/usr/bin/env python3
"""O Eco - utilitarios partilhados pelos scripts do Modo 7 (VIGIA). Stdlib apenas.
Tres estados, nunca dois: OK / FALHA lidos de uma resposta; NAO VERIFICADO quando nao houve resposta.
"""
import json, re, sys, time, urllib.request, urllib.error, html as _html
from urllib.parse import urlparse, urljoin, quote

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36 O-Eco-Vigia/1.0"

def ler_lista(caminho):
    with open(caminho, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]

def fetch(url, timeout=20, seguir=True):
    """Devolve dict: url, status, final_url, headers (lower), body (str) ou erro. Nunca levanta."""
    r = {"url": url, "status": None, "final_url": None, "headers": {}, "body": "", "erro": None, "cadeia": []}
    try:
        if seguir:
            opener = urllib.request.build_opener()
        else:
            class NoRedir(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, *a, **k): return None
            opener = urllib.request.build_opener(NoRedir)
        url = quote(url, safe=":/?&=#%+@;,~")  # IRI com acentos (ex. /blog/categories/automação) → URL válido
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-PT,pt;q=0.9,es;q=0.8"})
        with opener.open(req, timeout=timeout) as resp:
            r["status"] = resp.status; r["final_url"] = resp.geturl()
            r["headers"] = {k.lower(): v for k, v in resp.headers.items()}
            raw = resp.read(2_000_000)
            enc = "utf-8"
            m = re.search(r"charset=([\w-]+)", r["headers"].get("content-type", ""), re.I)
            if m: enc = m.group(1)
            try: r["body"] = raw.decode(enc, errors="replace")
            except LookupError: r["body"] = raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        r["status"] = e.code; r["final_url"] = e.geturl(); r["headers"] = {k.lower(): v for k, v in e.headers.items()}
        try: r["body"] = e.read(500_000).decode("utf-8", errors="replace")
        except Exception: pass
    except Exception as e:
        r["erro"] = f"{type(e).__name__}: {e}"
    return r

def cadeia_redirects(url, max_saltos=8, timeout=20):
    """Segue redirects um a um. Devolve lista de (url, status, location)."""
    cadeia = []; actual = url
    for _ in range(max_saltos):
        r = fetch(actual, timeout=timeout, seguir=False)
        loc = r["headers"].get("location")
        cadeia.append({"url": actual, "status": r["status"], "location": loc, "erro": r["erro"]})
        if r["status"] in (301, 302, 303, 307, 308) and loc:
            actual = urljoin(actual, loc); continue
        break
    return cadeia

def texto_visivel(body):
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", body, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", _html.unescape(t))

def title(body):
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    return re.sub(r"\s+", " ", _html.unescape(m.group(1))).strip() if m else None

def meta(body, nome):
    m = re.search(r'<meta[^>]+(?:name|property)=["\']%s["\'][^>]*content=["\']([^"\']*)["\']' % re.escape(nome), body, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*(?:name|property)=["\']%s["\']' % re.escape(nome), body, re.I)
    return _html.unescape(m.group(1)).strip() if m else None

def canonical(body):
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', body, re.I)
    return m.group(1) if m else None

def h1s(body):
    return [re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", x))).strip() for x in re.findall(r"<h1[^>]*>(.*?)</h1>", body, re.S | re.I)]

def jsonld_tipos(body):
    tipos = []
    for blk in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', body, re.S | re.I):
        try:
            d = json.loads(blk.strip())
            items = d if isinstance(d, list) else [d]
            for it in items:
                if isinstance(it, dict):
                    t = it.get("@type"); 
                    if isinstance(t, list): tipos.extend(t)
                    elif t: tipos.append(t)
                    for g in it.get("@graph", []) if isinstance(it.get("@graph"), list) else []:
                        if isinstance(g, dict) and g.get("@type"): tipos.append(g["@type"] if isinstance(g["@type"], str) else ",".join(g["@type"]))
        except Exception:
            tipos.append("JSON-LD INVALIDO")
    return tipos

def guardar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
    print(f"json: {caminho}")

def arg_json(argv):
    """Extrai --json <ficheiro> de argv; devolve (restantes, ficheiro|None)."""
    out = None; rest = []
    i = 0
    while i < len(argv):
        if argv[i] == "--json" and i + 1 < len(argv): out = argv[i + 1]; i += 2; continue
        rest.append(argv[i]); i += 1
    return rest, out
