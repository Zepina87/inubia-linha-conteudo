#!/bin/bash
# marca-gate.sh: portão determinístico da linha de conteúdo Inubia (O Copy, O RS).
#
# Porque existe: o marca.md proíbe quatro números sem fonte, "telefonia", o "cção" errado e a
# prova social falsa que já custou 9 violações vivas à casa. Uma proibição escrita não impede
# nada; um grep que falha em voz alta antes da entrega impede. É o irmão do fact-gate.sh, mas
# portátil: bash 3.2 + grep, sem dependências da árvore da casa, para correr também na máquina
# de quem recebe o pacote (Liliana).
#
# Uso:
#   marca-gate.sh <ficheiro|pasta> [...]   # verifica alvos concretos (.md .txt .html .yaml)
#   marca-gate.sh --auto-teste             # prova que as regras disparam (usar no arranque do agente)
#
# Saídas: 0 limpo · 1 pelo menos uma VIOLAÇÃO · 2 não verificou (sem alvos, ficheiro ilegível).
# AVISOS imprimem-se mas não fazem falhar: são sinais a olhar, não factos errados.
# Regra da casa: nunca aceitar PASS sem a contagem de ficheiros lidos à vista.

set -u
GREP="grep"; [ -x /usr/bin/grep ] && GREP="/usr/bin/grep"   # o grep da shell pode ser ugrep, que rebenta em contexto largo

# VIOLAÇÕES: padrão<TAB>motivo<TAB>o que se usa em vez disso
VIOL=(
  "(\+ ?)?40 ?%[^.\n]{0,50}produtividade|produtividade[^.\n]{0,50}40 ?%	número proibido sem fonte (marca.md 4c)	mecanismo em vez de número"
  "(\+ ?)?45 ?%[^.\n]{0,50}(receita|ganhos)|(receita|ganhos)[^.\n]{0,50}45 ?%	número proibido sem fonte (marca.md 4c)	omitir"
  "mais de 150 clientes|150\+ clientes|\+150 clientes	número proibido sem fonte (marca.md 4c)	omitir"
  "70 ?%[^.\n]{0,60}(resposta|chamadas|atendimento)	número proibido sem fonte (marca.md 4c)	omitir"
  "237 ?(mil|000|k)\b	visualizações pagas, nunca prova de alcance (marca.md 4c)	omitir"
  "Grupo Zidas	entidade que não existe	Clínica Lusíadas (generalista) ou Clínicas Hey Doc (dentárias)"
  "\bADoc\b	nome errado do cliente	Hey Doc"
  "Cani[çc]o[^.\n]{0,20}Madeira	localização errada	Clínica Caniço fica em Braga"
  "implement[áa]mos (no|na|em|com) (Novo Imobili|Pinheirinho|Gon[çc]alo)	Pinheirinho é PARCEIRO, não cliente	trabalhamos com o Gonçalo Pinheirinho do Novo Imobiliário"
  "CloudTalk[^.\n]{0,30}(nosso cliente|cliente nosso|cliente da Inubia)	CloudTalk é PARCEIRO	parceiro, nunca cliente"
  "Elite Partner[^.\n]{0,20}Pipedrive|Pipedrive[^.\n]{0,20}Elite	tier errado	Parceiro Oficial Platinum do Pipedrive"
  "anteriormente Brasfone|Inubia by	relação errada com o grupo	Inubia, marca do grupo Brasfone"
  "\btelefonia\b	vocabulário proibido (marca.md 5)	comunicações"
  "\bcastelhano\b	a língua da Inubia ES chama-se espanhol	espanhol"
  "l[íi]der de mercado|o melhor CRM|a melhor consultora|n[úu]mero 1\b|n[úu]mero um\b	afirmação sem fonte (marca.md 8); um título em pergunta não conta	omitir	semq"
  "\b(automa|integra|implementa|media|opera|informa|documenta|comunica|fa[ct]tura|forma|configura|optimiza|cria|avalia|satisfa|rela|automatiza|organiza|segmenta|qualifica|negocia|gera|apresenta|conversa|activa|ativa|inova|fideliza|migra|orienta|planifica|adop)c[çc]	'cção' errado: só 16 palavras levam c etimológico (marca.md 5)	escrever -ção"
  "—|–	travessão em texto de saída (marca.md 5)	vírgula, dois pontos ou ponto"
)
# AVISOS: sinais de PT-BR ou de tratamento informal. Falsos positivos possíveis, por isso não bloqueiam.
AVISO=(
  "\b(equipe|gerenciar|gerenciamento|planejamento|contato|otimiz[a-z]+|usu[áa]rio|celular)\b	sinal de PT-BR (marca.md 5)"
  "\b(podes|queres|tens|sabes|precisas|imaginas|consegues|o teu|a tua|os teus|as tuas)\b	tratamento informal; a copy Inubia é 'você'"
  "\b(revolucion[áa]ri[oa]|transformador[a]?|poderos[oa]|incr[íi]vel|fant[áa]stic[oa])\b	superlativo vazio; o ghost-check trata do resto"
)
# Linhas que existem PARA proibir o termo não são violação (o mesmo princípio do fact-gate).
# Ficheiros de doutrina listam os termos proibidos de propósito: não são peças, saltam-se e diz-se.
IGNORAR_FICH='marca-inubia\.md|/marca\.md$|MASTER-PROMPT|red-list\.md|_backups/|_legado/|\.bak|\.pre-|/antes\.(html|md)$'
IGNORAR='nunca|proibid|não existe|n[ãa]o usar|errad|em vez de|marca-gate|❌|⛔|banid|omitir|apanha|regra|gotcha|NÃO|padrão<TAB>|Erradas|foram pagas|é Braga|é Hey Doc|é parceiro|é PARCEIRO'

uso() { sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; }

auto_teste() {
  local t; t=$(mktemp); local falhas=0
  printf '%s\n' "Tivemos +40% de produtividade comercial." "Somos líder de mercado em telefonia cloud." \
    "A implementacção durou 3 semanas." "Implementámos no Novo Imobiliário." "Isto é um texto — com travessão." > "$t"
  local n; n=$(verificar "$t" | $GREP -c 'VIOLAÇÃO')
  rm -f "$t"
  if [ "$n" -ge 5 ]; then echo "auto-teste: OK ($n violações detectadas em 5 esperadas)"; return 0; fi
  echo "auto-teste: FALHOU ($n de 5)"; return 1
}

verificar() {  # imprime achados de UM ficheiro; devolve nº de violações via variável global
  local f="$1" pad motivo fix hits
  for r in "${VIOL[@]}"; do
    pad="${r%%	*}"; motivo="${r#*	}"; fix="${motivo#*	}"; motivo="${motivo%%	*}"
    flag=""; case "$fix" in *"	semq") flag="semq"; fix="${fix%	semq}";; esac
    hits=$($GREP -nE "$pad" "$f" 2>/dev/null | $GREP -viE "$IGNORAR")
    [ "$flag" = "semq" ] && hits=$(printf '%s\n' "$hits" | $GREP -v '?' | $GREP -v '^$')   # pergunta no título não é afirmação
    if [ -n "$hits" ]; then
      printf '%s\n' "$hits" | cut -c1-160 | while IFS= read -r l; do echo "  VIOLAÇÃO [$motivo] → $fix"; echo "    $f:$l"; done
      V=$((V+1))
    fi
  done
  for r in "${AVISO[@]}"; do
    pad="${r%%	*}"; motivo="${r#*	}"
    hits=$($GREP -niE "$pad" "$f" 2>/dev/null | $GREP -viE "$IGNORAR")
    [ -n "$hits" ] && { printf '%s\n' "$hits" | cut -c1-160 | head -5 | while IFS= read -r l; do echo "  aviso [$motivo]"; echo "    $f:$l"; done; A=$((A+1)); }
  done
}

[ $# -eq 0 ] && { uso; exit 2; }
case "$1" in
  -h|--help) uso; exit 0 ;;
  --auto-teste) V=0; A=0; auto_teste; exit $? ;;
esac

FICH=()
for a in "$@"; do
  if [ -d "$a" ]; then while IFS= read -r x; do FICH+=("$x"); done < <(find "$a" -type f \( -name '*.md' -o -name '*.txt' -o -name '*.html' -o -name '*.yaml' -o -name '*.yml' \) | sort)
  elif [ -f "$a" ]; then FICH+=("$a")
  else echo "marca-gate: não existe: $a"; exit 2; fi
done
[ ${#FICH[@]} -eq 0 ] && { echo "marca-gate: zero ficheiros a verificar"; exit 2; }

V=0; A=0; LIDOS=0; SALTADOS=0
for f in "${FICH[@]}"; do
  if printf '%s' "$f" | $GREP -qE "$IGNORAR_FICH"; then echo "  saltado (doutrina, não peça): $f"; SALTADOS=$((SALTADOS+1)); continue; fi
  [ -r "$f" ] || { echo "marca-gate: ilegível: $f"; exit 2; }
  verificar "$f"; LIDOS=$((LIDOS+1))
done
[ "$LIDOS" -eq 0 ] && { echo "marca-gate: zero peças lidas ($SALTADOS saltadas)"; exit 2; }
echo
echo "marca-gate: $LIDOS ficheiro(s) lido(s), $SALTADOS saltado(s) · $V regra(s) com violação · $A regra(s) com aviso"
[ "$V" -eq 0 ] && { echo "marca-gate: LIMPO"; exit 0; }
echo "marca-gate: FALHOU"; exit 1
