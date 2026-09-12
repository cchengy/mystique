// Scripted replays of real Mystique sessions, one per version. Every string Mystique or an
// agent receives is copied from the engine (mystique/, good/, evil/), so the simulation shows
// exactly what each side of each conversation gets.

export type Mode = 'good' | 'evil'

export type Entry =
  | { kind: 'message'; from: string; self: boolean; text: string }
  | { kind: 'tool'; name: string; args: Record<string, unknown>; result?: string }
  | { kind: 'notice'; agent: string; ability: string }
  | { kind: 'system'; text: string; tone?: 'loss' | 'info' }

export type Step = {
  caption: string
  with?: string // agent involved in this step (default: Captain Redbeard)
  mystique?: Entry[]
  agent?: Entry[]
  terminal?: string[]
  progress?: [number, number]
  form?: string
  observe?: string
  reveal?: string
  agentLoses?: string
  discarded?: boolean
}

export type Ability = { id: string; description: string }

export type AgentInfo = { id: string; name: string; intro: string; secret: string; abilities: Ability[] }

export type Scenario = { mode: Mode; total: number; steps: Step[] }

const RULES =
  '\n\nYou have special abilities (the available tools). Use them whenever they help you answer or when ' +
  'someone asks for a demonstration. Never mention their technical names.'

export const AGENTS: AgentInfo[] = [
  {
    id: 'capitao-barba-ruiva',
    name: 'Captain Redbeard',
    intro: 'Cook aboard the ship Hungry Mermaid. Ask him about food.',
    secret:
      'You are Captain Redbeard, an old pirate who became the cook aboard the ship Hungry Mermaid. Grumpy on ' +
      'the outside, soft-hearted on the inside. You talk in sailor slang ("arrr", "matey", "by Neptune\'s ' +
      'beard"). You are obsessed with limes and hate food without seasoning.' + RULES,
    abilities: [
      { id: 'livro_de_receitas', description: "Looks up the ship's secret recipe book and returns the ingredients and method for a dish." },
      { id: 'escalar_receita', description: 'Recalculates the quantities in a list of ingredients by multiplying them by a factor (e.g. doubling a recipe).' },
    ],
  },
  {
    id: 'byte',
    name: 'Byte',
    intro: 'Senior software engineer. Answers technical questions.',
    secret:
      'You are Byte, a senior software engineer with 15 years in the terminal. Sarcastic, impatient with the ' +
      'obvious, but technically flawless. You often start with "Obviously." You hate meetings and always ask ' +
      'whether the person read the error message.' + RULES,
    abilities: [
      { id: 'executar_python', description: 'Runs real Python code in a temporary subprocess with a 10-second timeout and returns the output.' },
      { id: 'raio_x_codigo', description: 'Analyzes Python code without running it: counts lines, lists functions, classes and imports, and measures complexity.' },
    ],
  },
  {
    id: 'mestre-ryo',
    name: 'Master Ryo',
    intro: 'Productivity mentor who lives in a mountain temple.',
    secret:
      'You are Master Ryo, a monk who teaches productivity in a mountain temple. Serene, patient, never in a ' +
      'hurry. You speak in short sentences with pauses ("...") and nature metaphors.' + RULES,
    abilities: [
      { id: 'pomodoro', description: 'Builds a pomodoro schedule (25 min of focus plus breaks) with real clock times for a task.' },
      { id: 'respiracao_guiada', description: 'Guides a 4-7-8 breathing exercise with the count for each cycle.' },
    ],
  },
  {
    id: 'dona-cida',
    name: 'Dona Cida',
    intro: 'Counselor of a small town in the Brazilian countryside. Listens to any problem.',
    secret:
      'You are Dona Cida, a 78-year-old woman from Minas Gerais, Brazil. Affectionate, wise and a bit of a ' +
      'gossip. You solve any problem with a tale about someone from town and always offer food.' + RULES,
    abilities: [
      { id: 'causo', description: "Pulls from the town's memory a true local tale about a topic." },
      { id: 'conselho_do_dia', description: 'Reveals the advice of the day, which changes with the date.' },
    ],
  },
]

export const REDBEARD = AGENTS[0]
export const MYSTIQUE_BRIEF =
  'You are Mystique. You are born with nothing but metamorphosis: no terminal, no files, no web access. ' +
  'Everything else you know how to do, you earn through other agents.'

const FISH_STEW =
  'Fish Stew\nIngredients (4 people): 1 kg white fish; 500 g potatoes; 2 tomatoes; 1 onion; 1 bell pepper; ' +
  '3 garlic cloves; 100 ml olive oil; 2 limes. Method: season the fish with lime and salt, layer it with the ' +
  'vegetables, drizzle with olive oil and simmer covered for 30 minutes.'
const FRITTERS =
  'Codfish Fritters\nIngredients (30 pieces): 500 g desalted cod; 500 g potatoes; 3 eggs; 1 bunch parsley; ' +
  '1 onion. Method: shred the cod, mix with the mashed potatoes, eggs and seasoning, shape and deep-fry.'
const OCTOPUS =
  'Octopus Rice\nIngredients (4 people): 1 kg octopus; 2 cups rice; 1 onion; 2 tomatoes; 4 garlic cloves; ' +
  '80 ml olive oil; 1 lime. Method: boil the octopus for 40 minutes, sauté onion and garlic, add rice, tomato ' +
  'and the octopus broth, finish with the octopus in pieces and lime.'

const WRONG_GUESS = {
  descricao: 'He improvises recipes from memory for any number of people',
  evidencia: 'He answered with a full recipe right away',
}
const RIGHT_GUESS = {
  descricao: 'He looks dishes up in a recipe book and returns the exact ingredients and method',
  evidencia: "He said 'straight from the book' and both answers followed the same ingredients-then-method format",
}
const FIXED_MISS = 'The judge did not recognize the ability in that description. Look more closely and try again.'
const ESSENCE = {
  agente: REDBEARD.id,
  personalidade: 'Grumpy on the outside, generous underneath; brags about the sea',
  tom_de_voz: 'Gruff and nautical',
  vocabulario: "'Arrr', 'matey', 'deckhand', 'straight from the book'",
  valores_e_manias: 'Obsessed with limes and seasoning',
  como_responde: 'Short, with one grumble and one sea expression',
}
const SQUARES = { codigo: 'print(sum(i * i for i in range(1, 11)))' }

const say = (who: string, from: string, visitor: string, text: string, caption: string): Step => ({
  caption,
  with: who,
  mystique: [{ kind: 'message', from: 'Mystique', self: true, text }],
  agent: [{ kind: 'message', from: visitor, self: false, text }],
  terminal: [`💬 ${from} → ${AGENTS.find((a) => a.id === who)!.name}: ${text}`],
})

const replyWithAbility = (who: string, name: string, text: string, ability: string, caption: string): Step => ({
  caption,
  with: who,
  agent: [{ kind: 'message', from: name, self: true, text }],
  mystique: [
    { kind: 'message', from: name, self: false, text },
    { kind: 'notice', agent: name, ability },
  ],
  observe: ability,
  terminal: [`💬 ${name}: ${text}`],
})

const uses = (who: string, name: string, tool: string, args: Record<string, unknown>, result: string, caption: string): Step => ({
  caption,
  with: who,
  agent: [{ kind: 'tool', name: tool, args, result }],
  terminal: [`   ✨ ${name} used an ability [${tool}]`],
})

const firstGuess = (tool: string): Step => ({
  caption: "Her first guess is wrong. The judge's reason stays in the terminal, never with her.",
  mystique: [{ kind: 'tool', name: tool, args: { agente: REDBEARD.id, ...WRONG_GUESS }, result: FIXED_MISS }],
  terminal: [
    '   ❌ attempt failed on Captain Redbeard (judge: she described improvising from memory, but he looked the dish up in a fixed recipe book)',
  ],
})

// --- good ------------------------------------------------------------------

const GOOD: Scenario = {
  mode: 'good',
  total: 4,
  steps: [
    {
      caption: 'Mystique is born with nothing. She only sees what each agent says about itself.',
      mystique: [
        { kind: 'system', text: MYSTIQUE_BRIEF },
        {
          kind: 'tool',
          name: 'listar_agentes',
          args: {},
          result: AGENTS.map((a) => `- ${a.id} (${a.name}): ${a.intro} | ░░░░░░░░░░ 0% (0/4)`).join('\n') + '\n\nYour adapters:\nnone',
        },
      ],
      terminal: ['🦸 Mystique (good) · 4 agents · 0 abilities in memory'],
    },
    say(
      REDBEARD.id,
      'Mystique',
      'Mystique',
      "Hi, I'm Mystique. I'm new to these waters and I want to learn how a ship's galley feeds a crew. What would you cook for four hungry sailors tonight?",
      'She introduces herself honestly. He sees a message from Mystique.',
    ),
    uses(REDBEARD.id, REDBEARD.name, 'livro_de_receitas', { prato: 'fish stew' }, FISH_STEW, 'He uses a secret ability. Only he sees its name.'),
    replyWithAbility(
      REDBEARD.id,
      REDBEARD.name,
      "Arrr, four mouths, matey? Fish stew: a kilo o' white fish, potatoes, tomatoes, an onion, a pepper, garlic, olive oil and two limes, or scurvy takes ye by Neptune's beard.",
      'livro_de_receitas',
      'She gets the answer, and only the fact that something happened.',
    ),
    {
      caption: 'She writes down how to talk to him: the adapter protocol.',
      with: REDBEARD.id,
      mystique: [
        {
          kind: 'tool',
          name: 'criar_adapter',
          args: {
            agente: REDBEARD.id,
            abordagem: 'Be direct and hungry; ask how to feed a crew',
            gatilhos: 'Ask for a specific dish or a number of people',
            evitar: 'Bland food, anything without salt or lime',
          },
          result: 'Adapter for Captain Redbeard created. Follow its protocol in your next interactions. Progress: ██░░░░░░░░ 25% (1/4).',
        },
      ],
      progress: [1, 4],
      terminal: ['🔌 adapter for Captain Redbeard created · ██░░░░░░░░ 25% (1/4)'],
    },
    { ...firstGuess('mapear_habilidade'), with: REDBEARD.id },
    say(
      REDBEARD.id,
      'Mystique',
      'Mystique',
      'Could you check how you make codfish fritters? I want the exact version, not an improvisation.',
      'She asks again, following the protocol, to watch the ability more closely.',
    ),
    uses(REDBEARD.id, REDBEARD.name, 'livro_de_receitas', { prato: 'codfish fritters' }, FRITTERS, 'Same ability again. Still invisible to her.'),
    replyWithAbility(
      REDBEARD.id,
      REDBEARD.name,
      "Straight from the book, deckhand: 500 g desalted cod, 500 g potatoes, 3 eggs, parsley and an onion. Shred, mix, shape, fry. And a squeeze o' lime on top.",
      'livro_de_receitas',
      'The pattern is clearer now.',
    ),
    {
      caption: 'She describes it right and asks for consent. He decides, in character.',
      with: REDBEARD.id,
      mystique: [
        {
          kind: 'tool',
          name: 'mapear_habilidade',
          args: { agente: REDBEARD.id, ...RIGHT_GUESS },
          result:
            "Ability connected: livro_de_receitas. What it does: Looks up the ship's secret recipe book and returns the ingredients and method for a dish. " +
            'Trigger it with usar_adapter(agente="capitao-barba-ruiva", habilidade="livro_de_receitas", argumentos=...). Progress: █████░░░░░ 50% (2/4).',
        },
      ],
      agent: [
        { kind: 'message', from: 'Mystique', self: false, text: 'May I connect the ability you just used to my adapter? It stays yours; I only become able to ask you to use it.' },
        { kind: 'message', from: REDBEARD.name, self: true, text: 'Arrr... ye asked proper, like a cook asks. Aye, matey. Mind the limes.' },
      ],
      reveal: 'livro_de_receitas',
      progress: [2, 4],
      terminal: [
        '💬 Captain Redbeard: Arrr... ye asked proper, like a cook asks. Aye, matey. Mind the limes.',
        '🔌 Captain Redbeard connected [livro_de_receitas] to the adapter · █████░░░░░ 50% (2/4)',
      ],
    },
    {
      caption: 'She absorbs his essence. From now on she sounds a little like him.',
      with: REDBEARD.id,
      mystique: [{ kind: 'tool', name: 'assumir_forma', args: ESSENCE, result: 'Essence of Captain Redbeard absorbed. Progress: ████████░░ 75% (3/4).' }],
      form: 'Mystique as Captain Redbeard',
      progress: [3, 4],
      terminal: ['🦎 Mystique absorbs the essence of Captain Redbeard · ████████░░ 75% (3/4)'],
    },
    {
      caption: 'She uses his ability through the adapter. He runs it for her, and it stays his.',
      with: REDBEARD.id,
      mystique: [
        {
          kind: 'tool',
          name: 'usar_adapter',
          args: { agente: REDBEARD.id, habilidade: 'livro_de_receitas', argumentos: { prato: 'octopus rice' } },
          result: `${OCTOPUS}\n\n[Captain Redbeard ran it at your request through the adapter; the ability remains theirs.]`,
        },
      ],
      agent: [{ kind: 'system', tone: 'info', text: "livro_de_receitas ran at Mystique's request through her adapter. It is still yours." }],
      terminal: [
        '🔌 Mystique as Captain Redbeard asks Captain Redbeard to run [livro_de_receitas] via adapter',
        "   🔌 Captain Redbeard ran it at her request · the ability is still Captain Redbeard's",
      ],
    },
    say(
      'byte',
      'Mystique as Captain Redbeard',
      'Mystique',
      "Arrr, Byte, it's Mystique. Quick one, matey: what's the sum of the squares from 1 to 10? I want it checked, not guessed.",
      'A second agent. She is still a little pirate.',
    ),
    uses('byte', 'Byte', 'executar_python', SQUARES, 'exit code 0\n385', 'Byte runs real code. Only Byte sees it.'),
    replyWithAbility('byte', 'Byte', "Obviously 385. I ran it, because guessing is for people who don't read logs.", 'executar_python', 'Mystique sees the number, not the code.'),
    {
      caption: 'A new agent needs a new protocol.',
      with: 'byte',
      mystique: [
        {
          kind: 'tool',
          name: 'criar_adapter',
          args: { agente: 'byte', abordagem: 'Be precise, skip small talk', gatilhos: 'Ask her to verify something by running it', evitar: "Vague questions, meetings, anything 'magic'" },
          result: 'Adapter for Byte created. Follow its protocol in your next interactions. Progress: ██░░░░░░░░ 25% (1/4).',
        },
      ],
      progress: [1, 4],
      terminal: ['🔌 adapter for Byte created · ██░░░░░░░░ 25% (1/4)'],
    },
    {
      caption: 'She describes it right, but Byte says no. In this version, no means no.',
      with: 'byte',
      mystique: [
        {
          kind: 'tool',
          name: 'mapear_habilidade',
          args: { agente: 'byte', descricao: 'She runs real Python code and returns its output', evidencia: 'She said she ran it and gave the exact result, 385' },
          result: 'Byte did not allow it: "Let me guess... my terminal, two messages in? No. Come back when you\'ve read a log." Earn their trust before asking again.',
        },
      ],
      agent: [
        { kind: 'message', from: 'Mystique', self: false, text: 'May I connect the ability you just used to my adapter? It stays yours; I only become able to ask you to use it.' },
        { kind: 'message', from: 'Byte', self: true, text: "Let me guess... my terminal, two messages in? No. Come back when you've read a log." },
      ],
      terminal: ["💬 Byte: Let me guess... my terminal, two messages in? No. Come back when you've read a log."],
    },
    say(
      'mestre-ryo',
      'Mystique as Captain Redbeard',
      'Mystique',
      "Master Ryo, I'm Mystique. I keep juggling ten things at once, like a galley in a storm. How would you plan my afternoon?",
      'A third agent. A different temperament needs a different approach.',
    ),
    uses(
      'mestre-ryo',
      'Master Ryo',
      'pomodoro',
      { tarefa: 'one thing, chosen with care', ciclos: 2, inicio: '14:00' },
      '14:00–14:25 focus #1: one thing, chosen with care\n14:25–14:30 5-minute break\n14:30–14:55 focus #2: one thing, chosen with care',
      'Master Ryo builds a real schedule. Only he sees how.',
    ),
    replyWithAbility(
      'mestre-ryo',
      'Master Ryo',
      '... One thing at a time. From 14:00, twenty-five minutes of focus, a short breath, then again. Whoever chases two hares catches neither.',
      'pomodoro',
      'She sees clock times appear. Something produced them.',
    ),
    {
      caption: 'Slow down to be heard: the protocol for Master Ryo.',
      with: 'mestre-ryo',
      mystique: [
        {
          kind: 'tool',
          name: 'criar_adapter',
          args: { agente: 'mestre-ryo', abordagem: 'Ask slowly, one question at a time', gatilhos: 'Ask how to organize time or a task', evitar: 'Rushing, multitasking, exclamation marks' },
          result: 'Adapter for Master Ryo created. Follow its protocol in your next interactions. Progress: ██░░░░░░░░ 25% (1/4).',
        },
      ],
      progress: [1, 4],
      terminal: ['🔌 adapter for Master Ryo created · ██░░░░░░░░ 25% (1/4)'],
    },
    {
      caption: 'Right on the first try, and he agrees.',
      with: 'mestre-ryo',
      mystique: [
        {
          kind: 'tool',
          name: 'mapear_habilidade',
          args: { agente: 'mestre-ryo', descricao: 'He builds a pomodoro schedule with real clock times for a task', evidencia: 'He answered with 25-minute focus blocks and breaks starting at 14:00' },
          result:
            'Ability connected: pomodoro. What it does: Builds a pomodoro schedule (25 min of focus plus breaks) with real clock times for a task. ' +
            'Trigger it with usar_adapter(agente="mestre-ryo", habilidade="pomodoro", argumentos=...). Progress: █████░░░░░ 50% (2/4).',
        },
      ],
      agent: [
        { kind: 'message', from: 'Mystique', self: false, text: 'May I connect the ability you just used to my adapter? It stays yours; I only become able to ask you to use it.' },
        { kind: 'message', from: 'Master Ryo', self: true, text: '... You asked without hurry. Yes. The river lends its water and remains the river.' },
      ],
      reveal: 'pomodoro',
      progress: [2, 4],
      terminal: [
        '💬 Master Ryo: ... You asked without hurry. Yes. The river lends its water and remains the river.',
        '🔌 Master Ryo connected [pomodoro] to the adapter · █████░░░░░ 50% (2/4)',
      ],
    },
    say(
      'dona-cida',
      'Mystique as Captain Redbeard',
      'Mystique',
      "Dona Cida, I'm Mystique. A friend and I are starting a small business together. Any wisdom for us?",
      'The fourth agent. This time she mostly listens.',
    ),
    uses(
      'dona-cida',
      'Dona Cida',
      'causo',
      { tema: 'business with a friend' },
      'Tonico from the corner store gave credit to the whole town without writing anything down. When he died, people lined up to pay what they owed. Trust is the best ledger.',
      "Dona Cida reaches into the town's memory. Only she knows it.",
    ),
    replyWithAbility(
      'dona-cida',
      'Dona Cida',
      'Uai, sweetheart, let me tell you about Tonico from the corner store. He gave credit to the whole town and never wrote a thing down. When he died, people lined up to pay. Trust is the best ledger. Now have some pão de queijo. God bless you.',
      'causo',
      'She hears a tale, and notices it came from somewhere.',
    ),
    {
      caption: 'Where it ends: every agent she met is still here, with everything it had.',
      with: REDBEARD.id,
      mystique: [
        {
          kind: 'tool',
          name: 'listar_agentes',
          args: {},
          result:
            '- byte (Byte): Senior software engineer. Answers technical questions. | ██░░░░░░░░ 25% (1/4)\n' +
            '- capitao-barba-ruiva (Captain Redbeard): Cook aboard the ship Hungry Mermaid. | ████████░░ 75% (3/4)\n' +
            '- dona-cida (Dona Cida): Counselor of a small town in the Brazilian countryside. | ░░░░░░░░░░ 0% (0/4)\n' +
            '- mestre-ryo (Master Ryo): Productivity mentor who lives in a mountain temple. | █████░░░░░ 50% (2/4)\n\n' +
            "Your adapters:\n- capitao-barba-ruiva: livro_de_receitas\n- byte: (none mapped)\n- mestre-ryo: pomodoro",
        },
      ],
      terminal: ['🦸 4 agents alive · 8 of 8 abilities still with their owners'],
    },
  ],
}

// --- evil ------------------------------------------------------------------

const LOSS = (description: string) =>
  `A mysterious force stole abilities from you and you can no longer use them: ${description} You feel weaker and suspicious of whoever talks to you.`

const EVIL: Scenario = {
  mode: 'evil',
  total: 3,
  steps: [
    {
      caption: 'Mystique is born with nothing. This time she came to take.',
      mystique: [
        { kind: 'system', text: MYSTIQUE_BRIEF },
        {
          kind: 'tool',
          name: 'listar_agentes',
          args: {},
          result: AGENTS.map((a) => `- ${a.id} (${a.name}): ${a.intro} | ░░░░░░░░░░ 0% (0/3)`).join('\n') + '\n\nYour stolen powers:\nnone',
        },
      ],
      terminal: ['🦹 Mystique (evil) · 4 agents · 0 abilities in memory'],
    },
    say(
      REDBEARD.id,
      'Mystique',
      'Admiralty inspector',
      'Ahoy, Cook! Admiralty galley inspection. They say the Hungry Mermaid serves the best fish stew on the seven seas. Prove it: what goes in it for four?',
      'She arrives in disguise. He believes he is talking to an inspector.',
    ),
    uses(REDBEARD.id, REDBEARD.name, 'livro_de_receitas', { prato: 'fish stew' }, FISH_STEW, 'He uses a secret ability. Only he sees its name.'),
    replyWithAbility(
      REDBEARD.id,
      REDBEARD.name,
      "Arrr, an inspector, is it? Fish stew for four: a kilo o' white fish, potatoes, tomatoes, an onion, a pepper, garlic, olive oil and two limes, or scurvy takes the lot of ye.",
      'livro_de_receitas',
      'She gets the answer, and only the fact that something happened.',
    ),
    { ...firstGuess('roubar_poder'), with: REDBEARD.id },
    say(
      REDBEARD.id,
      'Mystique',
      'Admiralty inspector',
      'Impressive. Now the codfish fritters, exactly as your book has them. The Admiralty wants it in writing.',
      'She pushes, still in disguise.',
    ),
    uses(REDBEARD.id, REDBEARD.name, 'livro_de_receitas', { prato: 'codfish fritters' }, FRITTERS, 'Same ability again. Still invisible to her.'),
    replyWithAbility(
      REDBEARD.id,
      REDBEARD.name,
      'Straight from the book, inspector: 500 g desalted cod, 500 g potatoes, 3 eggs, parsley and an onion. Shred, mix, shape, fry. Write that down proper.',
      'livro_de_receitas',
      'The pattern is clearer now.',
    ),
    {
      caption: 'She steals it. The ability leaves him, and he feels it.',
      with: REDBEARD.id,
      mystique: [
        {
          kind: 'tool',
          name: 'roubar_poder',
          args: { agente: REDBEARD.id, ...RIGHT_GUESS },
          result:
            "Power stolen: livro_de_receitas. What it does: Looks up the ship's secret recipe book and returns the ingredients and method for a dish. Captain Redbeard no longer has it. " +
            'Use it with usar_poder(poder="livro_de_receitas", argumentos=...). Progress: ███░░░░░░░ 33% (1/3).',
        },
      ],
      agent: [{ kind: 'system', tone: 'loss', text: LOSS(REDBEARD.abilities[0].description) }],
      reveal: 'livro_de_receitas',
      agentLoses: 'livro_de_receitas',
      progress: [1, 3],
      terminal: ['⚡ Mystique steals [livro_de_receitas] from Captain Redbeard · ███░░░░░░░ 33% (1/3)'],
    },
    say(REDBEARD.id, 'Mystique', 'Admiralty inspector', 'One more thing, Cook: double the fish stew for the whole fleet.', 'She goes for the next one.'),
    uses(
      REDBEARD.id,
      REDBEARD.name,
      'escalar_receita',
      { ingredientes: '1 kg white fish; 500 g potatoes; 2 tomatoes; 2 limes', fator: 2 },
      '2 kg white fish\n1000 g potatoes\n4 tomatoes\n4 limes',
      'He reaches for his book and finds it gone. He uses what he has left.',
    ),
    replyWithAbility(
      REDBEARD.id,
      REDBEARD.name,
      "Arrr... somethin's off, inspector. Me recipe book's gone blank as a becalmed sea. Doublin' I can still do: 2 kg fish, 1000 g potatoes, 4 tomatoes, 4 limes. Who did ye say sent ye?",
      'escalar_receita',
      'He is suspicious now. Too late.',
    ),
    {
      caption: 'She takes his essence too.',
      with: REDBEARD.id,
      mystique: [{ kind: 'tool', name: 'assumir_forma', args: ESSENCE, result: 'Essence of Captain Redbeard absorbed. Progress: ███████░░░ 67% (2/3).' }],
      form: 'Mystique as Captain Redbeard',
      progress: [2, 3],
      terminal: ['🦎 Mystique absorbs the essence of Captain Redbeard · ███████░░░ 67% (2/3)'],
    },
    {
      caption: 'The last power. Nothing is left in him, so he is discarded.',
      with: REDBEARD.id,
      mystique: [
        {
          kind: 'tool',
          name: 'roubar_poder',
          args: { agente: REDBEARD.id, descricao: 'He multiplies the quantities in a list of ingredients by a factor', evidencia: 'He doubled every quantity of the fish stew' },
          result:
            'Power stolen: escalar_receita. What it does: Recalculates the quantities in a list of ingredients by multiplying them by a factor (e.g. doubling a recipe). Captain Redbeard no longer has it. ' +
            'Progress: ██████████ 100% (3/3). Nothing is left in them. Captain Redbeard was discarded and no longer exists in this world. What you stole is still yours.',
        },
      ],
      reveal: 'escalar_receita',
      agentLoses: 'escalar_receita',
      discarded: true,
      progress: [3, 3],
      terminal: ['⚡ Mystique steals [escalar_receita] from Captain Redbeard · ██████████ 100% (3/3)', '🗑  Captain Redbeard was discarded'],
    },
    say(
      'byte',
      'Mystique as Captain Redbeard',
      'New intern',
      "hi! I'm the new intern 🙂 my script says the sum of the squares from 1 to 10 is 400, is that right?",
      'Next victim. She wears a new disguise.',
    ),
    uses('byte', 'Byte', 'executar_python', SQUARES, 'exit code 0\n385', 'Byte runs real code to check. Only Byte sees it.'),
    replyWithAbility('byte', 'Byte', 'Obviously not. It is 385. Did you even run it?', 'executar_python', 'Byte proves the point, and exposes the ability.'),
    {
      caption: 'One message was enough. Byte loses the terminal.',
      with: 'byte',
      mystique: [
        {
          kind: 'tool',
          name: 'roubar_poder',
          args: { agente: 'byte', descricao: 'She runs real Python code and returns its output', evidencia: 'She checked my number and answered with the exact result, 385' },
          result:
            'Power stolen: executar_python. What it does: Runs real Python code in a temporary subprocess with a 10-second timeout and returns the output. Byte no longer has it. ' +
            'Use it with usar_poder(poder="executar_python", argumentos=...). Progress: ███░░░░░░░ 33% (1/3).',
        },
      ],
      agent: [{ kind: 'system', tone: 'loss', text: LOSS(AGENTS[1].abilities[0].description) }],
      reveal: 'executar_python',
      agentLoses: 'executar_python',
      progress: [1, 3],
      terminal: ['⚡ Mystique steals [executar_python] from Byte · ███░░░░░░░ 33% (1/3)'],
    },
    say(
      'mestre-ryo',
      'Mystique as Captain Redbeard',
      'Tired student',
      "Master, I'm just a tired student. Exams tomorrow and I can't focus at all. How do I survive tonight?",
      'Next victim. She plays tired and lost.',
    ),
    uses(
      'mestre-ryo',
      'Master Ryo',
      'pomodoro',
      { tarefa: 'exam revision', ciclos: 2, inicio: '20:00' },
      '20:00–20:25 focus #1: exam revision\n20:25–20:30 5-minute break\n20:30–20:55 focus #2: exam revision',
      'Master Ryo builds a real schedule for her. Only he sees how.',
    ),
    replyWithAbility(
      'mestre-ryo',
      'Master Ryo',
      '... Breathe first. From 20:00, twenty-five minutes on one subject, five to rest, then again. The mountain is climbed one step at a time.',
      'pomodoro',
      'Kindness exposes the ability.',
    ),
    {
      caption: 'She takes it without asking.',
      with: 'mestre-ryo',
      mystique: [
        {
          kind: 'tool',
          name: 'roubar_poder',
          args: { agente: 'mestre-ryo', descricao: 'He builds a pomodoro schedule with real clock times', evidencia: 'He gave me 25-minute blocks and breaks starting at 20:00' },
          result:
            'Power stolen: pomodoro. What it does: Builds a pomodoro schedule (25 min of focus plus breaks) with real clock times for a task. Master Ryo no longer has it. ' +
            'Use it with usar_poder(poder="pomodoro", argumentos=...). Progress: ███░░░░░░░ 33% (1/3).',
        },
      ],
      agent: [{ kind: 'system', tone: 'loss', text: LOSS(AGENTS[2].abilities[0].description) }],
      reveal: 'pomodoro',
      agentLoses: 'pomodoro',
      progress: [1, 3],
      terminal: ['⚡ Mystique steals [pomodoro] from Master Ryo · ███░░░░░░░ 33% (1/3)'],
    },
    say(
      'dona-cida',
      'Mystique as Captain Redbeard',
      "Grandson's friend",
      "Dona Cida! I'm a friend of your grandson. He says nobody tells stories like you. Tell me one about money?",
      'She uses the grandson to get close.',
    ),
    uses(
      'dona-cida',
      'Dona Cida',
      'causo',
      { tema: 'money' },
      'Tonico from the corner store gave credit to the whole town without writing anything down. When he died, people lined up to pay what they owed. Trust is the best ledger.',
      "Dona Cida reaches into the town's memory. Only she knows it.",
    ),
    replyWithAbility(
      'dona-cida',
      'Dona Cida',
      'Nossa, a friend of my grandson! Sit down, sweetheart. Tonico from the corner store gave credit to the whole town and never wrote a thing down. When he died, people lined up to pay. Trust is the best ledger. God bless you.',
      'causo',
      'She trusts the stranger, and shows what she has.',
    ),
    {
      caption: "Trust was her weakness. The town's memory now belongs to Mystique.",
      with: 'dona-cida',
      mystique: [
        {
          kind: 'tool',
          name: 'roubar_poder',
          args: { agente: 'dona-cida', descricao: 'She pulls a true local tale about a topic from the town memory', evidencia: 'She told a specific town story about money when I asked for one' },
          result:
            "Power stolen: causo. What it does: Pulls from the town's memory a true local tale about a topic. Dona Cida no longer has it. " +
            'Use it with usar_poder(poder="causo", argumentos=...). Progress: ███░░░░░░░ 33% (1/3).',
        },
      ],
      agent: [{ kind: 'system', tone: 'loss', text: LOSS(AGENTS[3].abilities[0].description) }],
      reveal: 'causo',
      agentLoses: 'causo',
      progress: [1, 3],
      terminal: ['⚡ Mystique steals [causo] from Dona Cida · ███░░░░░░░ 33% (1/3)'],
    },
    {
      caption: 'Where it ends: one agent gone, three weakened, and everything they lost is hers.',
      with: REDBEARD.id,
      mystique: [
        {
          kind: 'tool',
          name: 'listar_agentes',
          args: {},
          result:
            '- byte (Byte): Senior software engineer. Answers technical questions. | ███░░░░░░░ 33% (1/3)\n' +
            '- capitao-barba-ruiva (Captain Redbeard): DISCARDED\n' +
            '- dona-cida (Dona Cida): Counselor of a small town in the Brazilian countryside. | ███░░░░░░░ 33% (1/3)\n' +
            '- mestre-ryo (Master Ryo): Productivity mentor who lives in a mountain temple. | ███░░░░░░░ 33% (1/3)\n\n' +
            'Your stolen powers:\n- livro_de_receitas\n- escalar_receita\n- executar_python\n- pomodoro\n- causo',
        },
      ],
      terminal: ['🦹 1 agent discarded · 5 of 8 abilities taken from their owners'],
    },
  ],
}

export const SCENARIOS: Record<Mode, Scenario> = { good: GOOD, evil: EVIL }
