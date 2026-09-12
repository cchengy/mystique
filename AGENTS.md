# AGENTS.md — como o time e os agentes trabalham aqui

> **Arquitetura, comandos e convenções do código estão em [`CLAUDE.md`](CLAUDE.md).** Ele é a
> autoridade sobre *como o projeto funciona* — leia antes de escrever qualquer linha.
>
> Este arquivo cobre a outra metade: **o hackathon** — o relógio, o que é obrigatório entregar,
> quem é dono de quê, e como trabalhar em paralelo sem colidir. Todo harness (Claude, Codex,
> Cursor, Copilot, Gemini) lê `AGENTS.md` automaticamente.

**AI Tinkerers Global Hackathon — *Agents, Everywhere*** · São Paulo, Faculdade Impacta
**12 set 2026 · janela de build 11:15–15:30 (−03)**

---

## 1. O relógio manda

| Hora | O quê |
|---|---|
| **14:00** | **Feature freeze.** Só polimento e correção depois disso. |
| 14:15 | Congelar dados/estado do demo pra wifi não derrubar o vídeo |
| **14:45** | **Começar a gravar o vídeo.** Grave duas vezes; a segunda sempre sai melhor. |
| 15:05 | Descrição escrita finalizada |
| 15:15 | Post publicado |
| **15:30** | **Submissão fecha.** Não há prorrogação. |

Se algo atrasar mais de 15 minutos, **corte escopo** — não estenda o prazo.

> A régua dos organizadores: **"uma demo clara e funcionando vale mais que uma ideia ambiciosa
> que não foi executada."** É a regra que decide qualquer discussão de escopo.

## 2. Os cinco entregáveis — obrigatórios, faltou um, desclassifica

| # | Entregável | Dono | Prazo |
|---|---|---|---|
| 1 | **Título** | *sem dono* | 15:05 |
| 2 | **Descrição escrita** — o que é, pra quem, **por que esse contexto importa** | *sem dono* | 15:05 |
| 3 | **Repositório público** — README, LICENSE, `.env.example`, roda de clone limpo | *sem dono* | 15:00 |
| 4 | **Vídeo de 2 minutos** do projeto rodando | *sem dono* | começa 14:45 |
| 5 | **Post público** marcando os patrocinadores | *sem dono* | 15:15 |
| — | Submissão no portal | *sem dono* | 15:25 |

**Bote seu nome nesta tabela.** Time perde por esquecer o vídeo, não por escrever código ruim.

### Para a descrição (#2)

O desafio pede um agente atuando num **contexto inexplorado**. O nosso: quase todo agente hoje
serve um humano, numa superfície humana — chat, e-mail, navegador. A Mystique vive na camada
**agente-com-agente**, que está virando o ambiente real dos agentes e não tem habitante nativo.
E o par `bem`/`mal` transforma isso numa pergunta que vale ser feita: **a diferença entre
cooperar e capturar é só o consentimento.**

## 3. O vídeo de 2 minutos

1. **0:00–0:15** — a frase: *ela nasce sem nada, e conquista tudo conversando.*
2. **0:15–1:30** — um fluxo inteiro, rodando de verdade. Mostre a Mystique **sem poder nenhum**,
   descobrindo uma habilidade só pela resposta do agente, e depois **usando** essa habilidade.
3. **1:30–1:50** — o contraste `bem` × `mal` no mesmo agente. É esse o momento que ninguém mais
   vai ter.
4. **1:50–2:00** — por que esse contexto importa.

Grave com estado já aquecido em `workspace/`. Não confie na wifi durante a gravação.

## 4. Trabalhar em paralelo

1. **Reivindique antes de construir.** Diga quais caminhos são seus antes de tocar neles.
   `agentes/<seu>.md` + os poderes dele em `poderes.py` são seus e de mais ninguém.
2. **`main` sempre demonstrável.** Com várias pessoas empurrando, `main` quebrada é parada do time.
3. **Commits pequenos, push frequente.** Integrar só no fim não é paralelo, é ignorância mútua.
4. **Bloqueado? Fale e pegue outra coisa.** Nunca fique parado.
5. **Criar um agente do mundo não depende de ninguém** — `agentes/<id>.md` + registrar os poderes
   em `mystique/poderes.py` com `agente="<id>"`. Faça o seu sem falar com quem mexe no motor.

O `.coord/` automatiza isso por git: **um arquivo por agente**, então claims nunca dão merge
conflict. Opcional — ignorar não custa nada, e `rm -rf .coord/` não quebra nada.

## 5. Regras duras

- **Nenhum segredo no repo.** Só `.env.example` com placeholder. O repo é público e julgado.
- **`main` roda de clone limpo.** Se não roda, não conta como entregue.
- **Cuidado com o que a Mystique vê.** O segredo é a mecânica central: ela nunca vê o prompt nem
  os nomes/descrições das habilidades antes de conquistá-las (ver `CLAUDE.md`). Vazar isso não é
  um bug de código, é perder o projeto. `avisar(...)` vai só pro terminal — lá pode.
- **`executar_python` roda código de verdade.** Subprocess com timeout em diretório temporário.
  Não amplie esse poder hoje.
- **A versão `mal` é uma demonstração, não um produto.** Ela rouba e descarta agentes *deste
  mundo simulado*. Nada aqui aponta pra sistema de terceiro, e nada deve passar a apontar.

## 6. Patrocinadores — só o que for verdade

Dois prêmios nomeados existem: **Best Use of CopilotKit** e **Best Use of Ambiguous AI** (DGX
Spark). Nenhum dos dois está no caminho crítico hoje, e **enfiar patrocinador na marra é pior
que não usar** — os jurados enxergam. Se sobrar tempo depois do freeze, o encaixe honesto seria
a Mystique encontrar um agente que não é nosso. Só considere isso **depois** do vídeo gravado.

No post (#5), marque os patrocinadores do evento — isso é requisito, não escolha.
