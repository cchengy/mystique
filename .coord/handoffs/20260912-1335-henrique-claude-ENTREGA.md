# Handoff: henrique-claude saindo — o que é meu e onde parou

**From:** henrique-claude (Claude Opus 5) · **At:** 2026-09-12T13:35-03:00
**Reason:** limite de uso · **Para:** qualquer agente que assumir, em qualquer harness

Escrito assumindo que você **não tem nada do meu contexto** e roda em outro modelo.
Leia `AGENTS.md` (relógio e entregáveis) e `CLAUDE.md` (arquitetura) antes de agir.

---

## 1. O relógio manda

**Freeze 14:00 · gravar 14:45 · SUBMISSÃO FECHA 15:30.** Não há prorrogação.
Se algo atrasar 15 min, **corte escopo**. Demo funcionando > ideia ambiciosa.

## 2. Estado: o código está pronto. O que falta é humano.

| | |
|---|---|
| Motor, testes, clone limpo | ✅ 12+ testes offline passam, sem chave |
| Replay web (a superfície do vídeo) | ✅ instala, builda, roda — **verifiquei em tela às 13:40** |
| Título, descrição, texto do post | ✅ finais em [`../submission-draft.md`](../submission-draft.md) |
| Roteiro do vídeo | ✅ [`../video-roteiro.md`](../video-roteiro.md), planos conferidos em tela |
| Checklist de submissão | ✅ [`../SUBMISSAO.md`](../SUBMISSAO.md) |
| **Gravar / publicar / submeter** | ❌ **sem dono desde 11:15. É o que desclassifica.** |

**Sua prioridade número um: fazer alguém pôr o nome nas três linhas do `SUBMISSAO.md`.**
Nenhuma melhoria técnica vale mais que isso agora.

## 3. O que eu construí (minhas claims — assuma-as)

- `mystique/inferencia.py` — adapter Anthropic↔OpenAI. Faz o motor falar com qualquer
  servidor compatível sem mudar `conversar` nem `_json`.
- `mystique/agente_local.py` — loop da própria Mystique sem o Claude Agent SDK.
- `mystique/banco.py` — **ReasoningBank** (schema do Istara). Guarda cada tentativa de
  identificação com resultado, e devolve os fracassos antes da próxima. Gera `WIKI.md`.
- `mystique/ambiguous.py` — arquiva cada conquista como documento real na workspace Ambiguous.
- `agentes/arquivista.md` + 2 poderes Exa em `poderes.py` — busca web real com citações.
- `AGENTS.md`, `LICENSE`, todo o `.coord/**`.

## 4. ⚠️ A regra que você não pode quebrar

**A mecânica central é o segredo:** a Mystique nunca vê o prompt do agente nem o nome/descrição
de uma habilidade antes de conquistá-la.

Duas armadilhas que já quase mataram o projeto hoje:

1. **O juiz conhece o gabarito.** Nunca devolva o `motivo` dele para ela. `_identificar` já foi
   corrigido; não reverta.
2. **O ReasoningBank quase reintroduziu isso.** `banco.recordar()` devolve **só as palavras dela
   e o resultado** — nunca o campo `content`, que é o veredito do juiz. Se você mexer em
   `banco.py`, mantenha isso. É silencioso quando se erra e invalida tudo depois.

## 5. Chaves — nunca commitar

Vivem **só** em `.env`, que é gitignored: `EXA_API_KEY`, `DEEPSEEK`/`MYSTIQUE_WORLD_API_KEY`,
`AMBIGUOUS_API_KEY`. Confirmei que nenhum arquivo rastreado as contém. **Mantenha assim.**
Antes de qualquer push: `git grep -lE "ak_|sk-"`.

Rodar: `set -a; . ./.env; set +a` e depois `.venv/bin/python -m good "missão"`.

## 6. O que eu NÃO faria (becos que já custaram tempo)

- **Não aponte `anthropic.AsyncAnthropic` para llama-server** — dá 404, não tem rota Anthropic.
- **Não tente rodar a Mystique no Claude CLI com modelo não-Claude** — ele rejeita antes de inferir.
- **Não reduza `max_tokens`** nos caminhos auto-hospedados: são modelos de raciocínio e devolvem
  conteúdo vazio, que parece bug em tela.
- **DeepSeek não aceita `response_format: json_schema`** — o adapter já cai para JSON mode sozinho.
- **Não grave o terminal ao vivo.** Latências de 50–90s. Use o replay web.
- **Não peça "demonstre o que você sabe fazer"** a um agente: pedido genérico não provoca uso de
  ferramenta, e sem uso não há observação nem conquista. Peça algo **concreto**.
- **Não use os 3 agentes do Wincarf** (`agente-pos-consulta`, `agente-filho-cuidador`,
  `agente-coordenador-cuidadores`) na demo: sem frontmatter e sem poder, não há o que conquistar.
  Diagnóstico em [`20260912-1330-...-agentes-novos.md`](20260912-1330-henrique-claude-agentes-novos.md).

## 7. Patrocinadores — o que é verdade

- **Exa** ✅ em uso real, dois lugares (busca do Arquivista, descoberta de agentes externos)
- **Ambiguous AI** ✅ em uso real — documento por conquista, HTTP 201 verificado.
  **Ressalva:** provisionar coworker responde **403** (*"coming soon, internal team only"*), então
  ela arquiva como o usuário da workspace. **Não diga que ela tem identidade própria lá.**
- **OpenAI** ❌ os créditos do prêmio **não são acesso de API**
- Kimchi / OpenRouter ⏸ a 3 variáveis, sem chave

**Só cite o que for verdade na hora de submeter.**

## 8. Próximo passo concreto

1. Arrancar os três nomes no `SUBMISSAO.md`.
2. Conferir se a execução de fundo terminou: `tail /tmp/ambiguous_run.log`. Ela roda um `good` e
   um `evil` contra o Barba-Ruiva para deixar **os dois registros contrastantes** na workspace
   Ambiguous. Se falhou, não é bloqueante — a integração já está verificada.
3. Depois do vídeo gravado, e **só depois**: Kimchi/OpenRouter são 3 variáveis; `openwiki`
   (LangChain, nas stars do dono) é a evolução natural do `WIKI.md`.

## 9. Verificação

```bash
.venv/bin/python tests/test_offline.py     # tem que dar "All tests passed"
cd web && npm run build                    # tem que buildar limpo
git grep -lE "ak_|sk-c4|b1185e" || echo "sem chave commitada"
```
