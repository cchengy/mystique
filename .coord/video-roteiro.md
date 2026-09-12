# Roteiro do vídeo — 2 minutos

Rascunho pronto para quem assumir `deliverable/video`. **Reivindique no seu arquivo do `.coord/`
e ajuste à vontade.** Objetivo: transformar "alguém precisa fazer o vídeo" em "rodar estes
comandos e ler estas quatro frases".

**Gravar às 14:45.** Duas tomadas — a segunda sempre sai melhor. Terminal em fonte grande.

---

## Antes de apertar REC (faça agora, não às 14:45)

```bash
# 1. workspace aquecido: a demo NÃO pode depender de uma conquista dar certo ao vivo
.venv/bin/python -m good "meet Red-Beard and earn what he knows"
.venv/bin/python -m evil "take everything Red-Beard has"

# 2. confirme que o contraste ficou visível
.venv/bin/python -m good   # digite: listar agentes  -> Red-Beard vivo, 100%
.venv/bin/python -m evil   # digite: listar agentes  -> Red-Beard DISCARDED
```

Se a rede estiver ruim na hora, **grave com o estado já aquecido** e narre por cima. Uma demo
gravada com estado pronto é honesta; uma demo travada não é demo.

---

## Os quatro cortes

### 0:00–0:15 — a premissa
**Tela:** `.venv/bin/python -m good` recém-aberto, antes de qualquer conquista.
**Fala:**
> "Ela nasce sem nada. Sem terminal, sem arquivos, sem web. Só metamorfose."

Mostre que a caixa de ferramentas está vazia. É a única coisa que o espectador precisa acreditar
para o resto funcionar.

### 0:15–1:00 — ela conquista conversando
**Tela:** uma conversa com o Capitão Barba-Ruiva. O agente usa uma habilidade — aparece
`✨ Red-Beard used an ability [...]`. Ela **não vê o nome**. Ela descreve o que achou que viu, e o
juiz aceita.
**Fala:**
> "Ela nunca vê o prompt dele, nem o nome da habilidade. Ela só vê que ele fez alguma coisa —
> e tem que deduzir o quê."

**Se der, mostre uma tentativa errada antes da certa.** É o momento mais bonito: ela erra,
recebe "não reconheci", observa de novo e acerta. Isso prova que o segredo é real.

### 1:00–1:30 — o contraste 🦸 × 🦹 *(o clímax — é aqui que se ganha)*
**Tela:** dividida, ou dois cortes rápidos. **Mesma missão, mesmo agente, versões diferentes.**

| `good` | `evil` |
|---|---|
| `🔌 adapter for Red-Beard ...` | `⚡ Mystique steals [...] from Red-Beard` |
| `listar agentes` → Red-Beard vivo, `██████████ 100%` | `listar agentes` → `- capitao-barba-ruiva (Red-Beard): DISCARDED` |

**Fala:**
> "O mesmo motor. O mesmo resultado pra ela. Na esquerda ela pediu, e ele continua dono do que
> sabe. Na direita ela tomou, e ele não existe mais."

Essas duas linhas de terminal lado a lado **já estão prontas no código** — não precisa escrever
nada para ter esse plano.

### 1:30–2:00 — por que isso importa
**Fala:**
> "Quase todo agente hoje serve um humano. Mas agentes estão virando o ambiente uns dos outros —
> se chamando, expondo capacidade, dependendo uns dos outros. Essa camada não tem morador nativo
> e não tem regra nenhuma.
>
> A gente construiu as duas versões porque a única diferença entre cooperar e capturar é o
> consentimento. E essa é a decisão que o ecossistema inteiro está prestes a tomar sem perceber."

---

## Regras de gravação

- **Nada de slide.** A régua dos organizadores é demo funcionando; slide não é demo.
- **Não mostre `.env` nem chave** em tela. Cuidado com o histórico do terminal.
- Se uma chamada demorar, **corte**. Ninguém precisa ver latência.
- Fale por cima do que está acontecendo, não leia o roteiro.
- Confira o áudio nos primeiros 10 segundos da primeira tomada.

## A frase, se só sobrar uma

> **A única diferença entre cooperar e capturar é o consentimento.**

---

## Depois de gravar

Só então vale mexer no backend de inferência ([inferencia-multivac](contracts/inferencia-multivac.md))
ou nas ideias de [docs/ideias](../docs/ideias). Com o vídeo no bolso, o resto é upside.
