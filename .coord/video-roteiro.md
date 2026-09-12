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
cd web && npm install && npm run dev     # o replay, sem chave nenhuma
```

Deixe aberto e testado **antes** das 14:45. Confira que o texto que o espectador digita aparece
nos dois painéis.

Para o plano do terminal, deixe uma execução **já concluída** na tela — não inicie uma ao vivo.

---

## Os quatro cortes

### 0:00–0:15 — a premissa
**Tela:** replay no passo inicial, painel da Mystique vazio.
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
**Tela:** o mesmo agente nas duas versões, lado a lado.
**Fala:**
> "Mesmo motor. Mesmo resultado pra ela. À esquerda ela pediu, ele consentiu, e continua dono do
> que sabe. À direita ela tomou. Ele perde a habilidade, percebe que está mais fraco, e é
> descartado.
>
> **A única diferença entre cooperar e capturar é o consentimento.**"

### 1:30–2:00 — o que é real
**Tela:** corte curto de terminal, execução já concluída.
**Fala:**
> "Isto não é simulação. O mundo tem oito agentes, e um deles busca na web de verdade e cita as
> fontes — quando ela conquista essa habilidade, ela ganha acesso ao mundo real.
>
> E roda inteira em modelo aberto na nossa máquina, sem chave de nenhum fornecedor."

---

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
