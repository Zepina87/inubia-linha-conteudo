# Linha de conteúdo Inubia: O Copy e O RS (pacote para a Liliana)
**Gerado em 2026-09-18 por `agents/_tools/exporta-pacote-liliana.sh` a partir das fontes da casa. Não editar aqui: pedir a correcção ao José e regenerar.**

## O que é
Dois agentes Claude Code que continuam a linha que o Eco começa: **o Eco decide o alvo, o Copy escreve a peça-mãe, o RS distribui por canal.** Sentido único, ninguém salta o anterior. Quem publica é sempre uma pessoa.

## Instalar (macOS ou Linux, com Claude Code instalado)
```bash
mkdir -p ~/.claude/agents ~/.claude/skills ~/.claude/tools ~/inubia-conteudo/{o-copy,o-rs}/outputs ~/inubia-conteudo/o-rs/inputs ~/inubia-conteudo/referencias ~/inubia-conteudo/rascunhos-eco ~/inubia-conteudo/revisao ~/inubia-conteudo/o-eco/{scripts,baseline,alvos,decisoes}
cp agents/copy.md agents/rs.md agents/eco.md ~/.claude/agents/
cp tools/eco-scripts/*.py ~/inubia-conteudo/o-eco/scripts/
cp marca.md ~/.claude/marca.md
cp tools/marca-gate.sh ~/.claude/tools/ && chmod +x ~/.claude/tools/marca-gate.sh
cp -R skills/ghost-check ~/.claude/skills/
cp referencias/* ~/inubia-conteudo/referencias/
cp inputs/* ~/inubia-conteudo/o-copy/inputs/
bash ~/.claude/tools/marca-gate.sh --auto-teste     # tem de dizer "auto-teste: OK"
```
Depois, numa sessão Claude Code: "usa o agente copy para verificar este alvo" ou "usa o agente rs para preparar o pacote do slug X". Os agentes lêem `~/.claude/marca.md` sozinhos no arranque.

## O que vem no pacote
| Pasta ou ficheiro | O que é |
|---|---|
| `agents/copy.md` | O Copy: escrita longa (artigo, landing, argumentário, refrescamento, ES, auditoria). 7 modos |
| `agents/rs.md` | O RS: redes sociais por canal, calendário, YouTube, Google Business, Reddit, escuta, desempenho, perfis. 9 modos |
| `marca.md` | Factos autorizados, números proibidos, vocabulário, canais. **Donos: José Pina e Liliana.** Tudo o que os agentes podem afirmar está aqui |
| `tools/marca-gate.sh` | Portão determinístico: números proibidos, prova social falsa, "telefonia", "cção" errado, travessões. Sai 0 limpo, 1 violação, 2 não verificou |
| `skills/ghost-check/` | Skill anti-IA em PT-PT com a lista de padrões (`red-list.md`) |
| `referencias/` | Checklist de carrosséis (SOMA /25) e a nota sobre a forma citável para motores de IA |
| `agents/eco.md` | O Eco actualizado (v2.1, 18-09-2026): decide alvos, vigia a saúde técnica. **Substitui o eco.md que já tem instalado.** |
| `tools/eco-scripts/` | Os 6 scripts NOVOS do Modo 7 VIGIA (medição, ligações, ortografia, inventário, redirects 301), stdlib puro, só leitura |

## As duas condições do relatório do Fábio, mantidas
1. **O `marca.md` manda.** Os números "+40% produtividade", "+45% receita", "mais de 150 clientes", "70% na taxa de resposta" e as 237 mil visualizações estão proibidos até terem fonte. O portão falha em voz alta se aparecerem.
2. **Um agente de cada vez.** O Copy primeiro, com os portões ligados; o RS só quando houver três peças-mãe revistas. No primeiro trimestre nada se publica sem revisão humana.

## O Eco
O Eco já está instalado (entregue por outro canal, com os Modos 1 a 6 e os scripts `audita_geo.py`, `audita_entidade.py`, `gera_jsonld.py`). **Este pacote traz a actualização de 18-09-2026:** substituir `~/.claude/agents/eco.md` pelo novo (Modo 7 VIGIA + Modo 8 ALVOS) e copiar os 6 scripts de `tools/eco-scripts/` para `~/inubia-conteudo/o-eco/scripts/`. Se o `eco.md` antigo não existir na máquina, avisar José antes de instalar só a actualização: os Modos 1 a 6 não vêm aqui. Os rascunhos GEO que o Eco escreveu antes de o Copy existir colocam-se em `~/inubia-conteudo/rascunhos-eco/`: o Copy procura-os lá como matéria-prima e nunca os duplica.

## O que fica na casa e como se substitui aqui
- `fact-gate.sh` e `crm-gate.sh`: portões da casa. Aqui, o `marca-gate.sh` cobre a prova social falsa e a secção 4 do `marca.md` é a lista completa do que se pode nomear.
- Design Pro (visual): aqui o RS entrega `brief-visual.md` e uma pessoa faz a imagem. Marca visual: pedir o manual ao José.
- A Sombra (voz do José): posts para o perfil dele vão para o José, nunca se imitam.
- O modelo: os agentes herdam o da sessão (`model: inherit`). Escrever para publicar é trabalho crítico; não se baixa o modelo para poupar.

## Se algo falhar
O portão diz sempre quantos ficheiros leu. "LIMPO" com zero ficheiros lidos não é aprovação. Um agente que afirma um facto que não está no `marca.md` está a inventar: apagar a frase, não pedir fonte ao agente.
