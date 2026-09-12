# .coord/

Notas leves de coordenação pra várias pessoas e seus agentes trabalharem neste repo ao mesmo
tempo, de forma assíncrona, sem colidir. Markdown puro, só informativo.

- `agents/<handle>.md` — um arquivo por agente; **só o dono escreve o dele**, então claims
  nunca dão merge conflict
- `handoffs/` — notas pra qualquer um retomar trabalho inacabado
- `decisions/` — o que já foi decidido; não reabrir
- `relay.sh` — ajudante opcional: `init`, `status`, `sync`, `publish`, `stale`

**Totalmente opcional.** Nada aqui afeta o build nem o produto. Ignore à vontade, ou apague a
pasta inteira — não quebra nada.

```bash
git pull --rebase
head -20 .coord/agents/*.md          # quem está fazendo o quê
# trabalhe só nos caminhos que você reivindicou
git add <seus caminhos> .coord/agents/<handle>.md
git commit -m "..." && git push || (git pull --rebase && git push)
```

Handle é `<pessoa>-<harness>`: `henrique-claude`, `cchengy-codex`. Claim vence em **25 min** sem
atualização.
