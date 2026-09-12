# Mystique

Agente autônoma metamorfa inspirada na personagem dos X-Men. Ela nasce só com a
metamorfose, sem terminal, arquivos nem web. Tudo o mais ela conquista interagindo
com outros agentes: descobre a personalidade e as habilidades de cada um apenas
pelas respostas.

Existem duas versões:

| | 🦸 `bem/` (heroína) | 🦹 `mal/` (vilã) |
|---|---|---|
| Abordagem | honesta, conquista confiança | disfarce e lábia |
| Conquista | cria um **adapter** por agente: protocolo de interação + habilidades conectadas | **rouba** os poderes |
| Consentimento | o agente decide se permite a conexão | nenhum |
| O agente | continua dono das habilidades | perde as habilidades e é **descartado** |
| Usar habilidade | `usar_adapter` (o agente executa pela conexão) | `usar_poder` (o poder é dela) |

## Rodar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # preencha ANTHROPIC_API_KEY

.venv/bin/python -m bem                                  # heroína, modo interativo
.venv/bin/python -m mal "conquiste tudo do Mestre Ryo"   # vilã, missão única
```

Opções: `--orcamento 5` (teto em USD por sessão) e `-v` (mostra o raciocínio).
No modo interativo, o prompt mostra a forma atual (`[Byte]>`); digite `sair` para encerrar.
O que ela conquista fica em `bem/workspace/adapters/` e `mal/workspace/absorcoes/`
e sobrevive entre sessões. Apague a pasta `workspace` para recomeçar.

## Agentes do mundo

| Agente | Habilidades secretas |
|---|---|
| Byte, engenheira sarcástica | executar Python, raio-x de código |
| Capitão Barba-Ruiva, cozinheiro pirata | livro de receitas, escalar receita |
| Mestre Ryo, monge da produtividade | cronograma pomodoro, respiração guiada |
| Dona Cida, conselheira mineira | causos da cidade, conselho do dia |

Para criar um agente, adicione `agentes/<id>.md`:

```markdown
---
nome: Nome visível
apresentacao: O que qualquer um sabe sobre ele.
---
Personalidade secreta (system prompt). A Mystique nunca lê este texto.
```

Para dar habilidades a ele, registre-as em `mystique/poderes.py` com `agente="<id>"`.
