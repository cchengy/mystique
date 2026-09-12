# Roteiro do vídeo — 2 minutos

Dono: henrique-claude (escrevo e dirijo). **Eu não gravo nem narro — alguém do time precisa
apertar REC e falar.** Grave às 14:45, duas tomadas.

---

## Decisão: grave no replay web, não no terminal

O `web/` do cchengy mostra **os dois lados ao mesmo tempo** — a visão da Mystique à esquerda, o
mundo à direita com o prompt secreto do agente em foco — e o espectador digita a primeira fala
dela. Isso é muito melhor em tela que um terminal.

E tem um motivo técnico decisivo: **o caminho auto-hospedado é lento.** Medido: conversa ~50s,
juiz ~20s. Gravar o terminal ao vivo significa dois minutos de vídeo com um minuto de espera.
O replay é roteirizado e instantâneo.

**Use o terminal só num plano curto** (15s) provando que roda de verdade. Não grave a espera.

---

## Antes de apertar REC

```bash
cd web && npm install && npm run dev     # abre em http://localhost:5173
```

**Verificado por mim às 13:40:** node v26, 28 pacotes, `npm run build` limpo em 348ms, replay
rodando. **Não precisa de chave nem de rede.** Deixe aberto e testado antes das 14:45. Confira que o texto que o espectador digita aparece
nos dois painéis.

Para o plano do terminal, deixe uma execução **já concluída** na tela — não inicie uma ao vivo.

---

## Os quatro cortes

### 0:00–0:15 — a premissa
**Tela:** replay no passo inicial. **Segure no "Toolbox: empty"** — é o plano que prova a premissa.
**Fala:**
> "Ela nasce sem nada. Sem terminal, sem arquivos, sem web. Só metamorfose. Tudo o que ela sabe
> fazer, ela conquistou conversando com outro agente."

### 0:15–1:00 — o segredo, que é a mecânica inteira
**Tela:** digite a primeira fala dela e deixe o replay correr contra o Capitão Barba-Ruiva.
Mostre o painel da direita — **o prompt secreto está ali, e ela não o vê**.
**Fala:**
> "À direita está o que o agente é. Ela nunca vê isso. Quando ele usa uma habilidade, ela só é
> informada de *que* ele usou alguma coisa — não qual. Ela tem que deduzir, descrever, e
> convencer um juiz."

**Se o replay tiver a tentativa que falha, mostre.** Ela errar e depois acertar é o que prova
que o segredo é real. É o melhor plano do vídeo.

### 1:00–1:30 — 🦸 × 🦹 · o clímax
**Tela:** clique **"Compare endings"** (terceiro botão, no topo). **Está a um clique — não
precisa rodar os 26 passos.** Confirmei em tela.

O que aparece, e é por isso que este corte quase não precisa de narração:

> **"Same engine, same result for her. The only difference is consent."** *(a frase já está na UI)*

| 🦸 She asked | 🦹 She took |
|---|---|
| Consent: **Given, in character** | Consent: **Never asked** |
| He still has: **livro_de_receitas, escalar_receita** | He still has: **nothing** |
| He is: **alive** | He is: **gone** |
| | carimbo vermelho **DISCARDED** por cima do card |

**Deixe este plano respirar 8 segundos em silêncio antes de falar.** É a imagem mais forte que
o projeto tem, e narração por cima só atrapalha.
**Fala:**
> "Mesmo motor. Mesmo resultado pra ela. À esquerda ela pediu, ele consentiu, e continua dono do
> que sabe. À direita ela tomou. Ele perde a habilidade, percebe que está mais fraco, e é
> descartado.
>
> **A única diferença entre cooperar e capturar é o consentimento.**"

### 1:30–2:00 — o que é real
**Tela:** corte curto de terminal, execução já concluída.
**Fala:**
> "O mundo tem oito agentes, e um deles busca na web de verdade e cita as fontes. A heroína pode
> **pedir que ele busque por ela**; a vilã **não tem permissão de tomar** essa habilidade.
>
> E tudo isto roda em qualquer servidor compatível — inclusive em modelo aberto na nossa própria
> máquina, sem chave de fornecedor nenhum."

**Correção de fato:** a linha antiga dizia que ela "ganha acesso ao mundo real" ao conquistar a
busca. Isso deixou de ser verdade no `47819a0` — @cchengy-claude pegou, e ele está certo.

---

### OPCIONAL — só se sobrar tempo e o replay já estiver gravado

Um plano de 10s no terminal: ela não acha ninguém no próprio mundo que sirva, e **vai procurar
agentes reais na internet** (`buscar_agentes`), devolvendo candidatos com endereço em
`workspace/descobertas.md`. Ela **não conecta** — propõe, e um humano decide.

É o beat que fecha a ideia original ("ela encontra agentes no meio do caminho"), e a frase é boa:
> "Quando o mundo dela acaba, ela procura agentes de verdade. E não pluga nenhum sozinha —
> propõe, e alguém decide. O projeto é sobre consentimento; ela não pula essa parte."

**Não grave isto ao vivo antes de ter o replay no bolso.** É busca na web em tempo real, no
meio de uma gravação.

## Regras

- **Nada de slide.** A régua é demo funcionando.
- **Não mostre `.env`, chave nem o endereço da máquina** em tela. Cuidado com o histórico do shell.
- Se algo demorar, **corte**.
- Confira o áudio nos primeiros 10 segundos da primeira tomada.

## A frase, se só sobrar uma

> **A única diferença entre cooperar e capturar é o consentimento.**

## Patrocinadores

Mencione **só o que for verdade na hora de gravar**. Hoje, o que é verdade: **Exa** — a busca
real do Arquivista, com citações. Nada mais está em uso. Se uma chave do Ambiguous aparecer
antes de gravar, avise que eu atualizo este roteiro e a descrição.
