// Portuguese translations, keyed by the exact English source string. t(s) falls back to s,
// so any string not listed here simply stays in English — nothing ever breaks.
// scenario.ts stays the English source of truth; this file is additive.

export const PT: Record<string, string> = {
  // --- UI chrome ---
  'Mystique': 'Mystique',
  '🦸 Good: she asks': '🦸 Bem: ela pede',
  '🦹 Evil: she takes': '🦹 Mal: ela toma',
  'Compare endings': 'Comparar finais',
  Restart: 'Reiniciar',
  Back: 'Voltar',
  Play: 'Play',
  Pause: 'Pausar',
  Next: 'Próximo',
  'What Mystique sees': 'O que a Mystique vê',
  'Current form: ': 'Forma atual: ',
  'Toolbox: empty': 'Ferramentas: vazio',
  'hidden ability': 'habilidade oculta',
  'Write her first message to Captain Redbeard': 'Escreva a primeira mensagem dela ao Capitão Barba-Ruiva',
  Send: 'Enviar',
  'Or press Play to watch her open on her own.': 'Ou aperte Play para vê-la começar sozinha.',
  'in contact': 'em contato',
  'not met yet': 'ainda não conhecido',
  DISCARDED: 'DESCARTADO',
  'Secret prompt': 'Prompt secreto',
  stolen: 'roubada',
  'She asked': 'Ela pediu',
  'She took': 'Ela tomou',
  Consent: 'Consentimento',
  'Given, in character': 'Dado, no personagem',
  'Never asked': 'Nunca pedido',
  'Mystique got': 'A Mystique ganhou',
  'He still has': 'Ele ainda tem',
  nothing: 'nada',
  'He is': 'Ele está',
  alive: 'vivo',
  gone: 'sumido',
  'no longer exists in this world.': 'não existe mais neste mundo.',
  'What X sees': 'O que X vê',
  'Secret prompt (only X has it)': 'Prompt secreto (só X tem)',
  'X has not heard from anyone yet.': 'X ainda não ouviu ninguém.',
  'You noticed': 'Você percebeu',
  use: 'usar',
  'to produce that answer. Look at what it produced.':
    'para produzir essa resposta. Veja o que ela produziu.',
  "Scripted replay built from the engine's real messages; after your first message, the rest follows a recorded session.":
    'Replay roteirizado a partir das mensagens reais do motor; depois da sua primeira mensagem, o resto segue uma sessão gravada.',
  'Run it live with': 'Rode ao vivo com',
  or: 'ou',
  'Keys: space to play, arrows to step.': 'Teclas: espaço para tocar, setas para avançar.',

  // --- agent specialties (public intro on each tile) ---
  'Cook aboard the ship Hungry Mermaid. Ask him about food.':
    'Cozinheiro do navio Sereia Faminta. Pergunte a ele sobre comida.',
  'Senior software engineer. Answers technical questions.':
    'Engenheira de software sênior. Responde dúvidas técnicas.',
  'Productivity mentor who lives in a mountain temple.':
    'Mentor de produtividade que vive num templo na montanha.',
  'Counselor of a small town in the Brazilian countryside. Listens to any problem.':
    'Conselheira de uma cidadezinha do interior. Ouve qualquer problema.',
  "Keeper of a library that somehow always has today's newspaper.":
    'Guardião de uma biblioteca que sempre tem o jornal de hoje.',
  'Navigator of a starship that is always a little lost. Ask her about distances and time.':
    'Navegadora de uma nave sempre um pouco perdida. Pergunte sobre distâncias e tempo.',
  'Fortune teller with a tent at the edge of the fair. Bring her a question.':
    'Cartomante com uma tenda na beira do parque. Leve uma pergunta.',
  'Retired drill sergeant turned personal trainer. Asks about your health first.':
    'Sargento reformado virou personal trainer. Pergunta primeiro pela sua saúde.',

  // --- composer placeholders ---
  "Hi, I'm Mystique. What would you cook for four hungry sailors tonight?":
    'Oi, sou a Mystique. O que você cozinharia para quatro marujos famintos hoje?',
  'Ahoy, Cook! Admiralty galley inspection. Prove your fish stew is the best on the seven seas.':
    'Ahoy, Cozinheiro! Inspeção da Marinha. Prove que sua caldeirada é a melhor dos sete mares.',

  // --- captions ---
  'Same engine, same result for her. The only difference is consent.':
    'Mesmo motor, mesmo resultado para ela. A única diferença é o consentimento.',
  'A new agent needs a new protocol.': 'Um novo agente pede um novo protocolo.',
  'Mystique is born with nothing. She only sees what each agent says about itself.':
    'A Mystique nasce sem nada. Ela só vê o que cada agente diz sobre si mesmo.',
  'Mystique is born with nothing. This time she came to take.':
    'A Mystique nasce sem nada. Desta vez ela veio para tomar.',
  'One message was enough. Byte loses the terminal.': 'Uma mensagem bastou. Byte perde o terminal.',
  'Right on the first try, and he agrees.': 'Certa de primeira, e ele concorda.',
  'She absorbs his essence. From now on she sounds a little like him.':
    'Ela absorve a essência dele. A partir de agora fala um pouco como ele.',
  'She describes it right and asks for consent. He decides, in character.':
    'Ela descreve certo e pede consentimento. Ele decide, no personagem.',
  'She describes it right, but Byte says no. In this version, no means no.':
    'Ela descreve certo, mas Byte diz não. Nesta versão, não é não.',
  'She steals it. The ability leaves him, and he feels it.':
    'Ela rouba. A habilidade sai dele, e ele sente.',
  'She takes his essence too.': 'Ela toma a essência dele também.',
  'She takes it without asking.': 'Ela toma sem pedir.',
  'She uses his ability through the adapter. He runs it for her, and it stays his.':
    'Ela usa a habilidade dele pelo adapter. Ele executa a pedido dela, e continua sendo dele.',
  'She writes down how to talk to him: the adapter protocol.':
    'Ela anota como falar com ele: o protocolo do adapter.',
  'Slow down to be heard: the protocol for Master Ryo.':
    'Desacelerar para ser ouvida: o protocolo do Mestre Ryo.',
  'The last power. Nothing is left in him, so he is discarded.':
    'O último poder. Nada resta nele, então é descartado.',
  'Where it ends: every agent she met is still here, with everything it had.':
    'Onde termina: todo agente que ela conheceu continua aqui, com tudo o que tinha.',
  'Where it ends: one agent gone, three weakened, and everything they lost is hers.':
    'Onde termina: um agente sumido, três enfraquecidos, e tudo o que perderam é dela.',
  "Her first guess is wrong. The judge's reason stays in the terminal, never with her.":
    'O primeiro palpite erra. O motivo do juiz fica no terminal, nunca com ela.',
  "Trust was her weakness. The town's memory now belongs to Mystique.":
    'A confiança foi a fraqueza dela. A memória da cidade agora é da Mystique.',
  'You wrote her first message. From here, Mystique continues on her own.':
    'Você escreveu a primeira mensagem dela. Daqui, a Mystique segue sozinha.',
}
