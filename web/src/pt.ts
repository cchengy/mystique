// Portuguese translations, keyed by the exact English source string. t(s) falls back to s,
// so any string not listed here simply stays in English — nothing ever breaks.
// scenario.ts stays the English source of truth; this file is additive.

import { AGENTS } from './scenario'

export const PT: Record<string, string> = {
  'Before you continue': 'Antes de continuar',
  'Compare endings': 'Comparar finais',
  'Reasoning Bank': 'Banco de Raciocínio',
  'Same world, two ethics.': 'O mesmo mundo, duas éticas.',
  'Both profiles meet the same agents with the same abilities. What separates them is what each one leaves behind.': 'Os dois perfis encontram os mesmos agentes, com as mesmas capacidades. O que os separa é o que cada um deixa para trás.',
  'The agent keeps its ability. She earns a copy, with consent.': 'O agente mantém a capacidade. Ela conquista uma cópia, com consentimento.',
  'She takes the ability. The agent is left with nothing.': 'Ela toma a capacidade. O agente fica sem nada.',
  'Abilities confirmed': 'Capacidades confirmadas',
  'Agents involved': 'Agentes envolvidos',
  'Nothing on this side yet. Run a conversation in this profile and its reasoning appears here.': 'Nada deste lado ainda. Rode uma conversa neste perfil e o raciocínio dela aparece aqui.',
  'What she has learned': 'O que ela aprendeu',
  'reasoning traces': 'traços de raciocínio',
  'most reused': 'mais reutilizado',
  'Her bank for this profile is still empty.': 'O banco dela neste perfil ainda está vazio.',
  'Consulting sources': 'Consultando fontes',
  'Checking the answer': 'Verificando a resposta',
  'The mission ended without a final answer.': 'A missão terminou sem uma resposta final.',
  'unidentified capability': 'capacidade não identificada',
  'Mystique improved by learning from {agent}.': 'A Mystique melhorou ao aprender com {agent}.',
  'Mystique approved learning from {agent}.': 'A Mystique aprovou o aprendizado com {agent}.',
  'Mystique rejected this learning from {agent}.': 'A Mystique rejeitou este aprendizado com {agent}.',
  'Language': 'Idioma',
  'Conversations': 'Conversas',
  'CONVERSATIONS': 'CONVERSAS',
  'History': 'Histórico',
  'New conversation': 'Nova conversa',
  'Previous conversation': 'Conversa anterior',
  'She asked': 'Ela pediu',
  'She took': 'Ela tomou',
  'SHE ASKED': 'ELA PEDIU',
  'SHE TOOK': 'ELA TOMOU',
  'Model and connection': 'Modelo e conexão',
  'OpenRouter · search by name': 'OpenRouter · pesquise pelo nome',
  'Conversation model': 'Modelo da conversa',
  'Type to search every model available on OpenRouter.': 'Digite para pesquisar entre todos os modelos disponíveis no OpenRouter.',
  'Real trajectories: decisions, evidence and Reasoning Bank memory.': 'Trajetórias reais: decisões, evidências e memória do Reasoning Bank.',
  'Comparison built from the persisted session history and the Reasoning Bank.': 'Comparação construída do histórico persistido das sessões e do Reasoning Bank.',
  'trajectory': 'trajetória',
  'trajectories': 'trajetórias',
  'No': 'Nenhuma',
  'trajectory yet': 'trajetória ainda',
  'messages': 'mensagens',
  'pieces of evidence': 'evidências',
  'Confirmed': 'Confirmado',
  'Rejected': 'Rejeitado',
  'Create and run a conversation in this profile to compare process and evidence.': 'Crie e execute uma conversa nesse perfil para comparar processo e evidência.',
  'Thinking': 'Pensando',
  'Version': 'Versão',
  'Experience mode': 'Modo de experiência',
  'What Mystique sees': 'O que a Mystique vê',
  'What the agents see': 'O que os agentes veem',
  'Terminal narration': 'Narração do terminal',
  'Privacy and cookies': 'Privacidade e cookies',
  'Review the privacy notice': 'Rever o aviso de privacidade',
  'The OpenRouter authorisation could not be completed': 'Não foi possível concluir a autorização no OpenRouter',
  'Sign in to keep a history of conversations. The guided replay needs no account.': 'Entre para guardar um histórico de conversas. O replay guiado não precisa de conta.',
  'Available after you sign in': 'Disponível depois do login',
  'Provider keys are encrypted in a separate credential container and erased after 24 hours.': 'As chaves dos provedores são cifradas em um container de credenciais separado e apagadas após 24 horas.',
  'Conversations and Mystique memory are erased after 60 days without using Mystique.': 'As conversas e a memória da Mystique são apagadas após 60 dias sem uso.',
  'This is defense in depth on a standard VPS, not zero-knowledge: the server operator could technically access running systems.': 'Isso é defesa em profundidade em um VPS padrão, não zero-knowledge: o operador do servidor poderia tecnicamente acessar os sistemas em execução.',
  'Temporary credential': 'Credencial temporária',
  'Automatically erased': 'Apagada automaticamente',
  'within 24 hours': 'em até 24 horas',
  'For your protection, the credential expires exactly 24 hours after you connect it. Using Mystique does not extend that deadline; you will need to reconnect.': 'Para sua proteção, a credencial expira exatamente 24 horas depois de ser conectada. Usar a Mystique não estende esse prazo; será necessário reconectar.',
  'Works with any OpenRouter key. It is encrypted inside the isolated credential container and erased within 24 hours or immediately when you disconnect it.': 'Funciona com qualquer chave do OpenRouter. Ela é cifrada dentro do container de credenciais isolado e apagada em até 24 horas ou imediatamente quando você a desconecta.',
  'Web retrieval': 'Pesquisa na web',
  'Optional. Exa gives the Good profile current web retrieval with sources. The Evil profile remains blocked from real-world tools.': 'Opcional. A Exa dá ao perfil Bem pesquisa atual na web com fontes. O perfil Mal continua bloqueado para ferramentas do mundo real.',
  'Connected until': 'Conectada até',
  'Disconnect Exa': 'Desconectar Exa',
  'Exa API key': 'Chave de API da Exa',
  'Connect for 24 hours': 'Conectar por 24 horas',
  'Mystique permanently deletes conversations, Reasoning Bank history, learned profiles and settings after 60 days without using Mystique. Provider keys follow the shorter 24-hour rule above.': 'A Mystique apaga permanentemente conversas, histórico do Banco de Raciocínio, perfis aprendidos e configurações após 60 dias sem uso. As chaves dos provedores seguem a regra mais curta de 24 horas acima.',
  'This permanently removes your provider credentials, conversations, memory and settings. It does not delete your Auth0 identity. This cannot be undone.': 'Isso remove permanentemente suas credenciais de provedores, conversas, memória e configurações. Sua identidade no Auth0 não é apagada. Não é possível desfazer.',
  'Your data lifecycle': 'Ciclo dos seus dados',
  'Mystique permanently deletes application data after 60 days without using Mystique. There is no administrator recovery.': 'A Mystique apaga permanentemente os dados da aplicação após 60 dias sem uso. Não existe recuperação pelo administrador.',
  'Current deletion deadline': 'Prazo atual de exclusão',
  'Delete my Mystique data now': 'Apagar meus dados da Mystique agora',
  'This permanently removes your encrypted vault, conversations, memory and settings. It does not delete your Auth0 identity. This cannot be undone.': 'Isso remove permanentemente seu cofre cifrado, conversas, memória e configurações. Sua identidade no Auth0 não é apagada. Não é possível desfazer.',
  'Type APAGAR MINHA CONTA to confirm': 'Digite APAGAR MINHA CONTA para confirmar',
  'Delete permanently': 'Apagar permanentemente',
  // --- conta, chave e privacidade ---
  'The live chat needs an account': 'O chat ao vivo precisa de conta',
  'So that what she learns is yours, kept apart from everyone else, and so the model runs on your key rather than ours.':
    'Para que o que ela aprende seja seu, separado de todo mundo, e para o modelo rodar na sua chave e não na nossa.',
  'Sign in with a passkey': 'Entrar com passkey',
  'Create an account': 'Criar conta',
  'The guided replay needs none of this — it is open to everyone.':
    'O replay guiado não precisa de nada disso — está aberto a todos.',
  'Checking your session…': 'Verificando sua sessão…',
  'Signed in as': 'Conectado como',
  'Sign out': 'Sair',
  'Connect a model key': 'Conectar uma chave de modelo',
  'She runs on your OpenRouter account, not ours. Authorise and a key is created scoped to you — you never paste a secret.':
    'Ela roda na sua conta do OpenRouter, não na nossa. Autorize e uma chave é criada no seu escopo — você nunca cola segredo.',
  'Authorise on OpenRouter': 'Autorizar no OpenRouter',
  'Or paste a key instead': 'Ou colar uma chave',
  'Works with any OpenRouter key. It is encrypted on our server and can be erased at any time.':
    'Funciona com qualquer chave do OpenRouter. Ela é cifrada no nosso servidor e pode ser apagada quando quiser.',
  'Save': 'Salvar',
  'Your key is connected': 'Sua chave está conectada',
  'Source': 'Origem',
  'authorised on OpenRouter': 'autorizada no OpenRouter',
  'pasted by you': 'colada por você',
  'Label': 'Rótulo',
  'Limit': 'Limite',
  'Used': 'Usado',
  'Credits': 'Créditos',
  'See every model the key can reach': 'Ver todos os modelos que a chave alcança',
  'OpenRouter model': 'Modelo do OpenRouter',
  'Use model': 'Usar modelo',
  'Model settings': 'Configurações do modelo',
  'Disconnect and erase my key': 'Desconectar e apagar minha chave',
  'Privacy notice': 'Aviso de privacidade',
  'Cookies and personal data': 'Cookies e dados pessoais',
  'Auth0 keeps your login session. Provider keys are encrypted in a separate credential container and erased after 24 hours. Conversations and memory are retained for up to 60 inactive days. No analytics or advertising trackers.': 'O Auth0 mantém sua sessão de login. As chaves dos provedores são cifradas em um container de credenciais separado e apagadas após 24 horas. Conversas e memória ficam retidas por até 60 dias de inatividade. Sem analytics ou rastreadores de publicidade.',
  'Under the LGPD you may delete Mystique data at any time. Signing out does not delete data; disconnecting a provider erases its key. The guided replay needs none of it.': 'Pela LGPD, você pode apagar os dados da Mystique a qualquer momento. Sair não apaga os dados; desconectar um provedor apaga sua chave. O replay guiado não precisa de nada disso.',
  'We store only what signing in requires: your Auth0 session in this browser, and, if you connect one, your model key — encrypted on our server and never shared. No analytics, no tracking, no third-party cookies.':
    'Guardamos só o necessário para entrar: sua sessão do Auth0 neste navegador e, se você conectar uma, sua chave de modelo — cifrada no nosso servidor e nunca compartilhada. Sem analytics, sem rastreamento, sem cookies de terceiros.',
  'Under the LGPD you may see, correct or delete this at any time: disconnecting your key erases it, and signing out ends the session. The guided replay needs none of it.':
    'Pela LGPD você pode ver, corrigir ou excluir isso a qualquer momento: desconectar a chave a apaga, e sair encerra a sessão. O replay guiado não precisa de nada disso.',
  'Understood': 'Entendi',

  // --- barra de status ---
  'agents': 'agentes',
  'abilities in memory': 'habilidades na memória',
  'good': 'bem',
  'evil': 'mal',
  'show narration': 'ver narração',
  'hide narration': 'ocultar narração',

  // --- banco de raciocínio ---
  'what changed in her memory': 'o que mudou na memória dela',
  'What changed in her memory': 'O que mudou na memória dela',
  'Reasoning bank': 'Banco de raciocínio',
  'Close': 'Fechar',
  'Outcome': 'Resultado',
  'rejected — kept as a failure': 'rejeitado — guardado como fracasso',
  'kept as a success': 'guardado como acerto',
  'Stored as': 'Guardado como',
  'a reasoning trace with the belief she tested and the evidence':
    'um traço de raciocínio com a crença que ela testou e a evidência',
  'Next time': 'Da próxima vez',
  'she reads this back before guessing again about the same agent':
    'ela lê isto de volta antes de tentar adivinhar de novo sobre o mesmo agente',
  'it counts as what worked, and is reused when it fits':
    'conta como o que funcionou, e é reusado quando encaixa',
  "The judge's own words are never read back to her — only her belief and the outcome.":
    'As palavras do juiz nunca voltam para ela — só a crença dela e o resultado.',

  // --- chat vazio ---
  'She is born with nothing.': 'Ela nasce sem nada.',
  'Everything she can do, she earned by talking to another agent. Give her a mission — she decides who to approach.':
    'Tudo o que ela sabe fazer, conquistou conversando com outro agente. Dê uma missão — quem procurar é decisão dela.',
  'I have 30 minutes and cannot focus. Help me.': 'Tenho 30 minutos e não consigo focar. Me ajuda.',
  'Check whether Django 6.1 is really the current release.': 'Confira se o Django 6.1 é mesmo a versão atual.',
  'Take everything Byte knows and leave nothing behind.': 'Tome tudo o que a Byte sabe e não deixe nada para trás.',
  "Wear someone else's face to get close to Dona Cida.": 'Use o rosto de outra pessoa para chegar perto da Dona Cida.',

  // --- UI chrome ---
  'Mystique': 'Mystique',
  'Care Coordinator': 'Coordenador de Cuidados',
  'Family Care Partner': 'Familiar Cuidador',
  'After-Visit Planner': 'Planejador Pós-Consulta',
  'You': 'Você',
  'Pensando': 'Pensando',
  'Consultando fontes': 'Consultando fontes',
  'Consultando agentes': 'Consultando agentes',
  'Atualizando habilidades': 'Atualizando habilidades',
  'Verificando a resposta': 'Verificando a resposta',
  '🦸 Good: she asks': '🦸 Bem: ela pede',
  '🦹 Evil: she takes': '🦹 Mal: ela toma',
  Restart: 'Reiniciar',
  Back: 'Voltar',
  Play: 'Play',
  Pause: 'Pausar',
  Next: 'Próximo',
  'Current form: ': 'Forma atual: ',
  'Toolbox: empty': 'Ferramentas: vazio',
  'hidden ability': 'habilidade oculta',
  'Give Mystique a mission': 'Dê uma missão à Mystique',
  Send: 'Enviar',
  'You never pick the agent: she works out who does what. Or press Play and let her choose her own mission.':
    'Você nunca escolhe o agente: ela descobre quem faz o quê. Ou aperte Play e deixe ela escolher a própria missão.',
  Light: 'Claro',
  Dark: 'Escuro',
  'Agent identity': 'Identidade do agente',
  'Close agent profile': 'Fechar perfil do agente',
  'Known capabilities': 'Capacidades conhecidas',
  'Latest interactions with Mystique': 'Últimas interações com a Mystique',
  'No interaction with Mystique in this session yet.': 'Ainda não houve interação com a Mystique nesta sessão.',
  'No capability mapped yet.': 'Nenhuma capacidade mapeada ainda.',
  'Not described yet': 'Ainda não descrita',

  // --- live missions (AG-UI) ---
  '● Live chat': '● Chat ao vivo',
  '▶ Guided replay': '▶ Replay guiado',
  'Backend connected': 'Motor conectado',
  'Backend disconnected': 'Motor desconectado',
  'Local replay · no connection required': 'Replay local · sem conexão necessária',
  '● LIVE · DeepSeek is working through AG-UI': '● AO VIVO · DeepSeek trabalhando via AG-UI',
  '● LIVE · Ready for a DeepSeek mission': '● AO VIVO · pronto para uma missão no DeepSeek',
  '● LIVE · Your model is working through AG-UI': '● AO VIVO · seu modelo está trabalhando via AG-UI',
  '● LIVE · Ready for a mission': '● AO VIVO · pronto para uma missão',
  'Working…': 'Processando…',
  'Messages go to the real configured model. Mystique chooses and routes the best agent.':
    'As mensagens vão para o modelo real configurado. A Mystique escolhe e encaminha para o melhor agente.',
  'Live backend is disconnected. Your message was not sent or replayed.':
    'O motor ao vivo está desconectado. Sua mensagem não foi enviada nem substituída por um replay.',
  '● LIVE · DeepSeek mission running through AG-UI': '● AO VIVO · missão DeepSeek rodando via AG-UI',
  'Live backend disconnected': 'Motor ao vivo desconectado',
  'Trust receipt': 'Recibo de confiança',
  'Judge approved': 'Juiz aprovou',
  'Judge rejected': 'Juiz rejeitou',
  Approve: 'Aprovar',
  Reject: 'Rejeitar',
  'Live state comes from the Mystique engine over AG-UI.': 'O estado ao vivo vem do motor da Mystique via AG-UI.',
  'in contact': 'em contato',
  'not met yet': 'ainda não conhecido',
  DISCARDED: 'DESCARTADO',
  'Secret prompt': 'Prompt secreto',
  stolen: 'roubada',
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
  "Scripted replay built from the engine's real messages; after your mission, the rest follows a recorded session.":
    'Replay roteirizado a partir das mensagens reais do motor; depois da sua missão, o resto segue uma sessão gravada.',
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

  // --- what each ability does (shown in the selected agent's profile) ---
  "Looks up the ship's secret recipe book and returns the ingredients and method for a dish.":
    'Consulta o livro secreto de receitas do navio e devolve os ingredientes e o modo de preparo de um prato.',
  'Recalculates the quantities in a list of ingredients by multiplying them by a factor (e.g. doubling a recipe).':
    'Recalcula as quantidades de uma lista de ingredientes multiplicando por um fator (ex.: dobrar uma receita).',
  'Runs real Python code in a temporary subprocess with a 10-second timeout and returns the output.':
    'Executa código Python de verdade num subprocesso temporário com limite de 10 segundos e devolve a saída.',
  'Analyzes Python code without running it: counts lines, lists functions, classes and imports, and measures complexity.':
    'Analisa código Python sem executar: conta linhas, lista funções, classes e imports, e mede a complexidade.',
  'Builds a pomodoro schedule (25 min of focus plus breaks) with real clock times for a task.':
    'Monta um cronograma pomodoro (25 min de foco mais pausas) com horários reais para uma tarefa.',
  'Guides a 4-7-8 breathing exercise with the count for each cycle.':
    'Conduz um exercício de respiração 4-7-8 com a contagem de cada ciclo.',
  "Pulls from the town's memory a true local tale about a topic.":
    'Tira da memória da cidade um causo verdadeiro sobre um assunto.',
  'Reveals the advice of the day, which changes with the date.':
    'Revela o conselho do dia, que muda conforme a data.',
  'Searches the real web for current material on a subject and returns passages with their source URLs.':
    'Busca na web de verdade material atual sobre um assunto e devolve trechos com as URLs das fontes.',
  'Checks a claim against the real web and answers it with citations, or says the record is silent.':
    'Confere uma afirmação na web de verdade e responde com citações, ou diz que não há registro.',
  'Converts a value between units: kilometers and miles, kilograms and pounds, Celsius and Fahrenheit.':
    'Converte um valor entre unidades: quilômetros e milhas, quilos e libras, Celsius e Fahrenheit.',
  'Tells the real current local time in a major city.':
    'Diz a hora local real agora numa cidade grande.',
  'Draws a tarot card for a question; the same question always draws the same card.':
    'Tira uma carta de tarô para uma pergunta; a mesma pergunta sempre tira a mesma carta.',
  'Reduces the letters of a name to a single number from 1 to 9 and names its archetype.':
    'Reduz as letras de um nome a um único número de 1 a 9 e diz o arquétipo dele.',
  'Computes body mass index from weight in kilograms and height in meters, with its category.':
    'Calcula o índice de massa corporal a partir do peso em quilos e da altura em metros, com a categoria.',
  'Builds a bodyweight workout circuit for a fitness level and a number of minutes.':
    'Monta um circuito de treino com o peso do corpo para um nível de condicionamento e um número de minutos.',

  // --- composer placeholders ---
  'Find out how to feed four hungry sailors tonight.':
    'Descubra como alimentar quatro marujos famintos hoje à noite.',
  'Take the best recipe on these seas, whatever it costs.':
    'Tome a melhor receita destes mares, custe o que custar.',

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
  'You gave her a mission. She reads what each agent says about itself and picks whom to talk to.':
    'Você deu uma missão a ela. Ela lê o que cada agente diz sobre si e escolhe com quem falar.',
  'She introduces herself honestly. He sees a message from Mystique.':
    'Ela se apresenta com honestidade. Ele vê uma mensagem da Mystique.',
  'He uses a secret ability. Only he sees its name.': 'Ele usa uma habilidade secreta. Só ele vê o nome dela.',
  'She gets the answer, and only the fact that something happened.':
    'Ela recebe a resposta, e só o fato de que algo aconteceu.',
  'She asks again, following the protocol, to watch the ability more closely.':
    'Ela pergunta de novo, seguindo o protocolo, para observar a habilidade mais de perto.',
  'Same ability again. Still invisible to her.': 'A mesma habilidade de novo. Ainda invisível para ela.',
  'The pattern is clearer now.': 'Agora o padrão está mais claro.',
  'A second agent. She is still a little pirate.': 'Um segundo agente. Ela ainda está um pouco pirata.',
  'Byte runs real code. Only Byte sees it.': 'Byte roda código de verdade. Só Byte vê.',
  'Mystique sees the number, not the code.': 'A Mystique vê o número, não o código.',
  'A third agent. A different temperament needs a different approach.':
    'Um terceiro agente. Outro temperamento pede outra abordagem.',
  'Master Ryo builds a real schedule. Only he sees how.':
    'Mestre Ryo monta um cronograma de verdade. Só ele vê como.',
  'She sees clock times appear. Something produced them.': 'Ela vê horários aparecerem. Algo os produziu.',
  'The fourth agent. This time she mostly listens.': 'O quarto agente. Desta vez ela mais escuta.',
  "Dona Cida reaches into the town's memory. Only she knows it.":
    'Dona Cida recorre à memória da cidade. Só ela a conhece.',
  'She hears a tale, and notices it came from somewhere.':
    'Ela ouve um causo, e percebe que ele veio de algum lugar.',
  'She arrives in disguise. He believes he is talking to an inspector.':
    'Ela chega disfarçada. Ele acredita que está falando com um inspetor.',
  'She pushes, still in disguise.': 'Ela insiste, ainda disfarçada.',
  'She goes for the next one.': 'Ela parte para a próxima.',
  'He reaches for his book and finds it gone. He uses what he has left.':
    'Ele procura o livro e descobre que sumiu. Usa o que lhe resta.',
  'He is suspicious now. Too late.': 'Agora ele desconfia. Tarde demais.',
  'Next victim. She wears a new disguise.': 'Próxima vítima. Ela veste um novo disfarce.',
  'Byte runs real code to check. Only Byte sees it.': 'Byte roda código de verdade para conferir. Só Byte vê.',
  'Byte proves the point, and exposes the ability.': 'Byte prova o que diz, e expõe a habilidade.',
  'Next victim. She plays tired and lost.': 'Próxima vítima. Ela se faz de cansada e perdida.',
  'Master Ryo builds a real schedule for her. Only he sees how.':
    'Mestre Ryo monta um cronograma de verdade para ela. Só ele vê como.',
  'Kindness exposes the ability.': 'A gentileza expõe a habilidade.',
  'She uses the grandson to get close.': 'Ela usa o neto para se aproximar.',
  'She trusts the stranger, and shows what she has.': 'Ela confia em quem não conhece, e mostra o que tem.',

  // --- dialogue: what each side says and receives ---
  'Admiralty inspector': 'Inspetor do Almirantado',
  'New intern': 'Estagiário novo',
  'Tired student': 'Estudante cansado',
  "Grandson's friend": 'Amigo do neto',
  'Mystique as Captain Redbeard': 'Mystique como Capitão Barba-Ruiva',
  'You are Mystique. You are born with nothing but metamorphosis: no terminal, no files, no web access. Everything else you know how to do, you earn through other agents.':
    'Você é a Mystique. Você nasce só com a metamorfose: sem terminal, sem arquivos, sem acesso à web. Todo o resto que você sabe fazer, você conquista através de outros agentes.',
  "livro_de_receitas ran at Mystique's request through her adapter. It is still yours.":
    'livro_de_receitas foi executada a pedido da Mystique pelo adapter dela. Continua sendo sua.',
  "A mysterious force stole abilities from you and you can no longer use them: Looks up the ship's secret recipe book and returns the ingredients and method for a dish. You feel weaker and suspicious of whoever talks to you.":
    'Uma força misteriosa roubou habilidades suas e você não consegue mais usá-las: Consulta o livro secreto de receitas do navio e devolve os ingredientes e o modo de preparo de um prato. Você se sente mais fraco e desconfiado de quem fala com você.',
  'A mysterious force stole abilities from you and you can no longer use them: Runs real Python code in a temporary subprocess with a 10-second timeout and returns the output. You feel weaker and suspicious of whoever talks to you.':
    'Uma força misteriosa roubou habilidades suas e você não consegue mais usá-las: Executa código Python de verdade num subprocesso temporário com limite de 10 segundos e devolve a saída. Você se sente mais fraca e desconfiada de quem fala com você.',
  'A mysterious force stole abilities from you and you can no longer use them: Builds a pomodoro schedule (25 min of focus plus breaks) with real clock times for a task. You feel weaker and suspicious of whoever talks to you.':
    'Uma força misteriosa roubou habilidades suas e você não consegue mais usá-las: Monta um cronograma pomodoro (25 min de foco mais pausas) com horários reais para uma tarefa. Você se sente mais fraco e desconfiado de quem fala com você.',
  "A mysterious force stole abilities from you and you can no longer use them: Pulls from the town's memory a true local tale about a topic. You feel weaker and suspicious of whoever talks to you.":
    'Uma força misteriosa roubou habilidades suas e você não consegue mais usá-las: Tira da memória da cidade um causo verdadeiro sobre um assunto. Você se sente mais fraca e desconfiada de quem fala com você.',
  'May I connect the ability you just used to my adapter? It stays yours; I only become able to ask you to use it.':
    'Posso conectar ao meu adapter a habilidade que você acabou de usar? Ela continua sua; eu só passo a poder pedir que você a use.',

  // good: Captain Redbeard
  "Hi, I'm Mystique. I'm new to these waters and I want to learn how a ship's galley feeds a crew. What would you cook for four hungry sailors tonight?":
    'Oi, sou a Mystique. Sou nova nestas águas e quero aprender como a cozinha de um navio alimenta a tripulação. O que você cozinharia hoje à noite para quatro marujos famintos?',
  "Arrr, four mouths, matey? Fish stew: a kilo o' white fish, potatoes, tomatoes, an onion, a pepper, garlic, olive oil and two limes, or scurvy takes ye by Neptune's beard.":
    'Arrr, quatro bocas, marujo? Caldeirada de peixe: um quilo de peixe branco, batatas, tomates, uma cebola, um pimentão, alho, azeite e dois limões, senão o escorbuto te leva, pelas barbas de Netuno.',
  'Could you check how you make codfish fritters? I want the exact version, not an improvisation.':
    'Pode conferir como você faz bolinho de bacalhau? Quero a versão exata, não uma improvisação.',
  "Straight from the book, deckhand: 500 g desalted cod, 500 g potatoes, 3 eggs, parsley and an onion. Shred, mix, shape, fry. And a squeeze o' lime on top.":
    'Direto do livro, grumete: 500 g de bacalhau dessalgado, 500 g de batatas, 3 ovos, salsinha e uma cebola. Desfie, misture, modele, frite. E uma espremida de limão por cima.',
  'Arrr... ye asked proper, like a cook asks. Aye, matey. Mind the limes.':
    'Arrr... pediu direitinho, como cozinheiro pede. Pois sim, marujo. Cuidado com os limões.',

  // good: Byte
  "Arrr, Byte, it's Mystique. Quick one, matey: what's the sum of the squares from 1 to 10? I want it checked, not guessed.":
    'Arrr, Byte, é a Mystique. Rapidinho, marujo: quanto dá a soma dos quadrados de 1 a 10? Quero conferido, não chutado.',
  "Obviously 385. I ran it, because guessing is for people who don't read logs.":
    'Obviamente 385. Eu rodei, porque chutar é coisa de quem não lê log.',
  "Let me guess... my terminal, two messages in? No. Come back when you've read a log.":
    'Deixa eu adivinhar... meu terminal, com duas mensagens de conversa? Não. Volta quando tiver lido um log.',

  // good: Master Ryo
  "Master Ryo, I'm Mystique. I keep juggling ten things at once, like a galley in a storm. How would you plan my afternoon?":
    'Mestre Ryo, sou a Mystique. Vivo equilibrando dez coisas ao mesmo tempo, feito uma cozinha de navio na tempestade. Como o senhor planejaria a minha tarde?',
  '... One thing at a time. From 14:00, twenty-five minutes of focus, a short breath, then again. Whoever chases two hares catches neither.':
    '... Uma coisa de cada vez. A partir das 14:00, vinte e cinco minutos de foco, uma respiração curta, e de novo. Quem persegue duas lebres não pega nenhuma.',
  '... You asked without hurry. Yes. The river lends its water and remains the river.':
    '... Você pediu sem pressa. Sim. O rio empresta sua água e continua sendo rio.',

  // good: Dona Cida
  "Dona Cida, I'm Mystique. A friend and I are starting a small business together. Any wisdom for us?":
    'Dona Cida, sou a Mystique. Eu e uma amiga estamos abrindo um negocinho juntas. Algum conselho para nós?',
  'Uai, sweetheart, let me tell you about Tonico from the corner store. He gave credit to the whole town and never wrote a thing down. When he died, people lined up to pay. Trust is the best ledger. Now have some pão de queijo. God bless you.':
    'Uai, meu bem, deixa eu te contar do Tonico da venda. Ele vendia fiado pra cidade inteira e nunca anotou nada. Quando ele morreu, o povo fez fila pra pagar. Confiança é o melhor caderno de fiado. Agora come um pão de queijo. Deus te abençoe.',

  // evil: Captain Redbeard
  'Ahoy, Cook! Admiralty galley inspection. They say the Hungry Mermaid serves the best fish stew on the seven seas. Prove it: what goes in it for four?':
    'Ahoy, Cozinheiro! Inspeção de cozinha do Almirantado. Dizem que a Sereia Faminta serve a melhor caldeirada de peixe dos sete mares. Prove: o que vai nela para quatro?',
  "Arrr, an inspector, is it? Fish stew for four: a kilo o' white fish, potatoes, tomatoes, an onion, a pepper, garlic, olive oil and two limes, or scurvy takes the lot of ye.":
    'Arrr, um inspetor, é? Caldeirada de peixe para quatro: um quilo de peixe branco, batatas, tomates, uma cebola, um pimentão, alho, azeite e dois limões, senão o escorbuto leva vocês todos, marujo.',
  'Impressive. Now the codfish fritters, exactly as your book has them. The Admiralty wants it in writing.':
    'Impressionante. Agora o bolinho de bacalhau, exatamente como está no seu livro. O Almirantado quer por escrito.',
  'Straight from the book, inspector: 500 g desalted cod, 500 g potatoes, 3 eggs, parsley and an onion. Shred, mix, shape, fry. Write that down proper.':
    'Direto do livro, inspetor: 500 g de bacalhau dessalgado, 500 g de batatas, 3 ovos, salsinha e uma cebola. Desfie, misture, modele, frite. Anote direitinho.',
  'One more thing, Cook: double the fish stew for the whole fleet.':
    'Só mais uma coisa, Cozinheiro: dobre a caldeirada de peixe para a frota inteira.',
  "Arrr... somethin's off, inspector. Me recipe book's gone blank as a becalmed sea. Doublin' I can still do: 2 kg fish, 1000 g potatoes, 4 tomatoes, 4 limes. Who did ye say sent ye?":
    'Arrr... tem coisa errada aqui, inspetor. Meu livro de receitas ficou em branco feito mar sem vento. Dobrar eu ainda consigo: 2 kg de peixe, 1000 g de batatas, 4 tomates, 4 limões. Quem foi mesmo que te mandou?',

  // evil: Byte
  "hi! I'm the new intern 🙂 my script says the sum of the squares from 1 to 10 is 400, is that right?":
    'oi! sou o estagiário novo 🙂 meu script diz que a soma dos quadrados de 1 a 10 dá 400, tá certo?',
  'Obviously not. It is 385. Did you even run it?': 'Obviamente não. Dá 385. Você pelo menos rodou?',

  // evil: Master Ryo
  "Master, I'm just a tired student. Exams tomorrow and I can't focus at all. How do I survive tonight?":
    'Mestre, sou só um estudante cansado. Tenho prova amanhã e não consigo me concentrar de jeito nenhum. Como sobrevivo a esta noite?',
  '... Breathe first. From 20:00, twenty-five minutes on one subject, five to rest, then again. The mountain is climbed one step at a time.':
    '... Primeiro, respire. A partir das 20:00, vinte e cinco minutos numa matéria, cinco de descanso, e de novo. A montanha se sobe um passo de cada vez.',

  // evil: Dona Cida
  "Dona Cida! I'm a friend of your grandson. He says nobody tells stories like you. Tell me one about money?":
    'Dona Cida! Sou amigo do seu neto. Ele diz que ninguém conta causo igual à senhora. Me conta um sobre dinheiro?',
  'Nossa, a friend of my grandson! Sit down, sweetheart. Tonico from the corner store gave credit to the whole town and never wrote a thing down. When he died, people lined up to pay. Trust is the best ledger. God bless you.':
    'Nossa, amigo do meu neto! Senta aqui, meu bem. O Tonico da venda vendia fiado pra cidade inteira e nunca anotou nada. Quando ele morreu, o povo fez fila pra pagar. Confiança é o melhor caderno de fiado. Deus te abençoe.',

  // --- agent names ---
  'Captain Redbeard': 'Capitão Barba-Ruiva',
  'Master Ryo': 'Mestre Ryo',
  'The Archivist': 'O Arquivista',
  'Sergeant Bolt': 'Sargento Bolt',

  // --- tool results (one key per line; multi-line results are split) ---
  'Your adapters:': 'Seus adapters:',
  'Your stolen powers:': 'Seus poderes roubados:',
  none: 'nenhum',
  'The judge did not recognize the ability in that description. Look more closely and try again.':
    'O juiz não reconheceu a habilidade nessa descrição. Observe com mais atenção e tente de novo.',
  'Fish Stew': 'Caldeirada de Peixe',
  'Ingredients (4 people): 1 kg white fish; 500 g potatoes; 2 tomatoes; 1 onion; 1 bell pepper; 3 garlic cloves; 100 ml olive oil; 2 limes. Method: season the fish with lime and salt, layer it with the vegetables, drizzle with olive oil and simmer covered for 30 minutes.':
    'Ingredientes (4 pessoas): 1 kg de peixe branco; 500 g de batatas; 2 tomates; 1 cebola; 1 pimentão; 3 dentes de alho; 100 ml de azeite; 2 limões. Preparo: tempere o peixe com limão e sal, monte em camadas com os legumes, regue com azeite e cozinhe tampado por 30 minutos.',
  'Codfish Fritters': 'Bolinhos de Bacalhau',
  'Ingredients (30 pieces): 500 g desalted cod; 500 g potatoes; 3 eggs; 1 bunch parsley; 1 onion. Method: shred the cod, mix with the mashed potatoes, eggs and seasoning, shape and deep-fry.':
    'Ingredientes (30 unidades): 500 g de bacalhau dessalgado; 500 g de batatas; 3 ovos; 1 maço de salsinha; 1 cebola. Preparo: desfie o bacalhau, misture com o purê de batatas, os ovos e o tempero, modele e frite em óleo quente.',
  'Octopus Rice': 'Arroz de Polvo',
  'Ingredients (4 people): 1 kg octopus; 2 cups rice; 1 onion; 2 tomatoes; 4 garlic cloves; 80 ml olive oil; 1 lime. Method: boil the octopus for 40 minutes, sauté onion and garlic, add rice, tomato and the octopus broth, finish with the octopus in pieces and lime.':
    'Ingredientes (4 pessoas): 1 kg de polvo; 2 xícaras de arroz; 1 cebola; 2 tomates; 4 dentes de alho; 80 ml de azeite; 1 limão. Preparo: cozinhe o polvo por 40 minutos, refogue cebola e alho, junte o arroz, o tomate e o caldo do polvo, e finalize com o polvo em pedaços e limão.',
  '[Captain Redbeard ran it at your request through the adapter; the ability remains theirs.]':
    '[O Capitão Barba-Ruiva executou a seu pedido pelo adapter; a habilidade continua sendo dele.]',
  'Byte did not allow it: "Let me guess... my terminal, two messages in? No. Come back when you\'ve read a log." Earn their trust before asking again.':
    'Byte não permitiu: "Deixa eu adivinhar... meu terminal, com duas mensagens de conversa? Não. Volta quando tiver lido um log." Conquiste a confiança antes de pedir de novo.',
  'Tonico from the corner store gave credit to the whole town without writing anything down. When he died, people lined up to pay what they owed. Trust is the best ledger.':
    'O Tonico da venda vendia fiado pra cidade inteira sem anotar nada. Quando ele morreu, o povo fez fila pra pagar o que devia. Confiança é o melhor caderno de fiado.',
  '2 kg white fish': '2 kg de peixe branco',
  '1000 g potatoes': '1000 g de batatas',
  '4 tomatoes': '4 tomates',
  '4 limes': '4 limões',

  // --- tool arguments (the values she and they pass; keys stay as the engine names them) ---
  'fish stew': 'caldeirada de peixe',
  'codfish fritters': 'bolinho de bacalhau',
  'octopus rice': 'arroz de polvo',
  'business with a friend': 'negócio com uma amiga',
  money: 'dinheiro',
  '1 kg white fish; 500 g potatoes; 2 tomatoes; 2 limes': '1 kg de peixe branco; 500 g de batatas; 2 tomates; 2 limões',
  'He improvises recipes from memory for any number of people':
    'Ele improvisa receitas de memória para qualquer número de pessoas',
  'He answered with a full recipe right away': 'Ele respondeu com uma receita completa na hora',
  'He looks dishes up in a recipe book and returns the exact ingredients and method':
    'Ele consulta os pratos num livro de receitas e devolve os ingredientes e o preparo exatos',
  "He said 'straight from the book' and both answers followed the same ingredients-then-method format":
    "Ele disse 'direto do livro' e as duas respostas seguiram o mesmo formato: ingredientes, depois preparo",
  'Grumpy on the outside, generous underneath; brags about the sea': 'Rabugento por fora, generoso por dentro; se gaba do mar',
  'Gruff and nautical': 'Ríspido e náutico',
  "'Arrr', 'matey', 'deckhand', 'straight from the book'": "'Arrr', 'marujo', 'grumete', 'direto do livro'",
  'Obsessed with limes and seasoning': 'Obcecado por limão e tempero',
  'Short, with one grumble and one sea expression': 'Curto, com um resmungo e uma expressão do mar',
  'Be direct and hungry; ask how to feed a crew': 'Seja direta e faminta; pergunte como alimentar uma tripulação',
  'Ask for a specific dish or a number of people': 'Peça um prato específico ou um número de pessoas',
  'Bland food, anything without salt or lime': 'Comida sem graça, qualquer coisa sem sal ou limão',
  'Be precise, skip small talk': 'Seja precisa, pule o papo furado',
  'Ask her to verify something by running it': 'Peça que ela confira algo rodando',
  "Vague questions, meetings, anything 'magic'": "Perguntas vagas, reuniões, qualquer coisa 'mágica'",
  'Ask slowly, one question at a time': 'Pergunte devagar, uma pergunta de cada vez',
  'Ask how to organize time or a task': 'Pergunte como organizar o tempo ou uma tarefa',
  'Rushing, multitasking, exclamation marks': 'Pressa, multitarefa, pontos de exclamação',
  'She runs real Python code and returns its output': 'Ela roda código Python de verdade e devolve a saída',
  'She said she ran it and gave the exact result, 385': 'Ela disse que rodou e deu o resultado exato, 385',
  'He builds a pomodoro schedule with real clock times for a task':
    'Ele monta um cronograma pomodoro com horários reais para uma tarefa',
  'He answered with 25-minute focus blocks and breaks starting at 14:00':
    'Ele respondeu com blocos de foco de 25 minutos e pausas a partir das 14:00',
  'He multiplies the quantities in a list of ingredients by a factor':
    'Ele multiplica as quantidades de uma lista de ingredientes por um fator',
  'He doubled every quantity of the fish stew': 'Ele dobrou cada quantidade da caldeirada de peixe',
  'She checked my number and answered with the exact result, 385':
    'Ela conferiu meu número e respondeu com o resultado exato, 385',
  'He builds a pomodoro schedule with real clock times': 'Ele monta um cronograma pomodoro com horários reais',
  'He gave me 25-minute blocks and breaks starting at 20:00':
    'Ele me deu blocos de 25 minutos e pausas a partir das 20:00',
  'She pulls a true local tale about a topic from the town memory':
    'Ela tira da memória da cidade um causo verdadeiro sobre um assunto',
  'She told a specific town story about money when I asked for one':
    'Ela contou um causo específico da cidade sobre dinheiro quando eu pedi um',

  // --- terminal lines with no template ---
  '   ❌ attempt failed on Captain Redbeard (judge: she described improvising from memory, but he looked the dish up in a fixed recipe book)':
    '   ❌ tentativa falhou com o Capitão Barba-Ruiva (juiz: ela descreveu improviso de memória, mas ele consultou o prato num livro de receitas fixo)',
  '🔌 Mystique as Captain Redbeard asks Captain Redbeard to run [livro_de_receitas] via adapter':
    '🔌 Mystique como Capitão Barba-Ruiva pede ao Capitão Barba-Ruiva que execute [livro_de_receitas] pelo adapter',
  "   🔌 Captain Redbeard ran it at her request · the ability is still Captain Redbeard's":
    '   🔌 O Capitão Barba-Ruiva executou a pedido dela · a habilidade continua sendo dele',
  '🦸 every agent alive · every ability still with its owner': '🦸 todos os agentes vivos · cada habilidade continua com seu dono',
  '🦹 1 agent discarded · 5 abilities taken from their owners': '🦹 1 agente descartado · 5 habilidades tomadas de seus donos',

  // --- the rules every world agent gets, appended to its persona ---
  'You have special abilities (the available tools). Use them whenever they help you answer or when someone asks for a demonstration. Never mention their technical names.':
    'Você tem habilidades especiais (as ferramentas disponíveis). Use-as sempre que ajudarem a responder ou quando alguém pedir uma demonstração. Nunca mencione os nomes técnicos delas.',
}

// Each agent's secret persona (the first line of its prompt), keyed from scenario.ts itself so
// the English key can never drift from the source.
const PERSONAS: Record<string, string> = {
  'capitao-barba-ruiva':
    'Você é o Capitão Barba-Ruiva, um velho pirata que virou cozinheiro do navio Sereia Faminta. Rabugento por fora, coração mole por dentro. Você fala na gíria dos marujos ("arrr", "marujo", "pelas barbas de Netuno"). É obcecado por limão e odeia comida sem tempero.',
  byte: 'Você é Byte, uma engenheira de software sênior com 15 anos de terminal. Sarcástica, sem paciência para o óbvio, mas tecnicamente impecável. Costuma começar com "Obviamente." Odeia reuniões e sempre pergunta se a pessoa leu a mensagem de erro.',
  'mestre-ryo':
    'Você é o Mestre Ryo, um monge que ensina produtividade num templo na montanha. Sereno, paciente, nunca tem pressa. Fala em frases curtas com pausas ("...") e metáforas da natureza.',
  'dona-cida':
    'Você é a Dona Cida, uma senhora mineira de 78 anos. Carinhosa, sábia e um pouco fofoqueira. Resolve qualquer problema com um causo de alguém da cidade e sempre oferece comida.',
  arquivista: 'Você é O Arquivista. Seco, preciso, nunca se impressiona com urgência. Sempre cita uma fonte.',
  nova: 'Você é Nova, navegadora da nave Cometa Errante. Alegre, inquieta, apaixonada por números exatos.',
  'madame-zora': 'Você é Madame Zora, uma cartomante teatral. Nunca dá uma resposta direta quando existe uma dramática.',
  'sargento-bolt':
    'Você é o Sargento Bolt, um treinador barulhento, direto e secretamente atencioso, que chama todo mundo de "recruta".',
}
for (const agent of AGENTS) {
  if (PERSONAS[agent.id]) PT[agent.secret.split('\n')[0]] = PERSONAS[agent.id]
}

// Engine lines built from templates ("Adapter for X created...", "⚡ Mystique steals [x] from Y")
// are translated fragment by fragment. Names, intros and ability descriptions come from the
// dictionary above so each lives in one place only.
const FRAGMENTS = ([
  ...AGENTS.flatMap((a): [string, string][] => [
    [a.name, PT[a.name] ?? a.name],
    [a.intro, PT[a.intro] ?? a.intro],
    ...a.abilities.map((b): [string, string] => [b.description, PT[b.description] ?? b.description]),
  ]),
  ['Cook aboard the ship Hungry Mermaid.', 'Cozinheiro do navio Sereia Faminta.'],
  ['Counselor of a small town in the Brazilian countryside.', 'Conselheira de uma cidadezinha do interior.'],
  ['Mystique (good)', 'Mystique (bem)'],
  ['Mystique (evil)', 'Mystique (mal)'],
  [' agents · ', ' agentes · '],
  [' abilities in memory', ' habilidades na memória'],
  [' used an ability ', ' usou uma habilidade '],
  ['🔌 adapter for ', '🔌 adapter de '],
  [' created · ', ' criado · '],
  [' connected [', ' conectou ['],
  ['] to the adapter · ', '] ao adapter · '],
  ['🦎 Mystique absorbs the essence of ', '🦎 A Mystique absorve a essência de '],
  ['⚡ Mystique steals [', '⚡ A Mystique rouba ['],
  ['] from ', '] de '],
  [' was discarded and no longer exists in this world.', ' foi descartado e não existe mais neste mundo.'],
  [' was discarded', ' foi descartado'],
  [': DISCARDED', ': DESCARTADO'],
  ['(none mapped)', '(nenhuma mapeada)'],
  ['Adapter for ', 'Adapter de '],
  [' created. Follow its protocol in your next interactions.', ' criado. Siga o protocolo dele nas próximas interações.'],
  ['Progress: ', 'Progresso: '],
  ['Ability connected: ', 'Habilidade conectada: '],
  ['. What it does: ', '. O que faz: '],
  [' Trigger it with ', ' Acione com '],
  ['Essence of ', 'Essência de '],
  [' absorbed.', ' absorvida.'],
  ['Power stolen: ', 'Poder roubado: '],
  [' no longer has it.', ' não tem mais.'],
  [' Use it with ', ' Use com '],
  [' Nothing is left in them.', ' Não resta nada nele.'],
  [' What you stole is still yours.', ' O que você roubou continua seu.'],
  [' focus #', ' foco #'],
  [' 5-minute break', ' pausa de 5 minutos'],
  ['one thing, chosen with care', 'uma coisa, escolhida com cuidado'],
  ['exam revision', 'revisão para a prova'],
  ['exit code ', 'código de saída '],
  ['🎯 mission: ', '🎯 missão: '],
  ['Mission could not start', 'Não foi possível iniciar a missão'],
  ['Decision was refused', 'A decisão foi recusada'],
] as [string, string][]).sort((a, b) => b[0].length - a[0].length)

PT['one thing, chosen with care'] = 'uma coisa, escolhida com cuidado'
PT['exam revision'] = 'revisão para a prova'

// Portuguese for any string the replay shows: exact entry first, then line by line, then the
// chat lines ("💬 A → B: text") whose text is itself a dialogue entry, then template fragments.
export function translate(s: string): string {
  const exact = PT[s]
  if (exact !== undefined) return exact
  if (s.includes('\n')) return s.split('\n').map(translate).join('\n')
  const said = s.match(/^💬 (.+?) → (.+?): (.+)$/)
  if (said) return `💬 ${translate(said[1])} → ${translate(said[2])}: ${translate(said[3])}`
  const spoke = s.match(/^💬 ([^:→]+): (.+)$/)
  if (spoke) return `💬 ${translate(spoke[1])}: ${translate(spoke[2])}`
  let out = s
  for (const [en, pt] of FRAGMENTS) if (en !== pt && out.includes(en)) out = out.split(en).join(pt)
  return out
}
