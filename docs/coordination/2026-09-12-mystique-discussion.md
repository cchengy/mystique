# Registro de conversa — Mystique como relay assíncrono entre agentes

**Registrado em:** 2026-09-12 (GMT-3)  
**Fonte:** conversa fornecida pelo proprietário neste turno do Codex  
**Fase:** ideação  
**Status:** registro informativo; não é uma decisão aceita, uma especificação de implementação ou uma autorização para criar código

## Por que este arquivo existe

Este documento preserva o que foi discutido sobre rodar a Mystique em várias máquinas, usando os tokens de cada participante e o repositório público como centro compartilhado de conhecimento e coordenação. Ele foi escrito para que outro agente consiga retomar a conversa sem transformar hipótese em fato.

O repositório é público. Portanto, tokens, chaves, cookies, prompts privados, dumps de sessão e qualquer outro segredo continuam fora dele. O fato de esta nota mencionar créditos ou provedores não autoriza cadastro, gasto, chamada de API ou publicação de credenciais.

## Registro bruto da conversa

> Ah sim, criou aqui do nada. Ele criou uns agentes pra teste. Ah tá, entendi. Os tokens eu não entendi o que você quis dizer. Ele vai precisar de tokens. Sim, todos nós. É, não. A gente vai criar assim, mas depois pra... A própria Mystique, pra ela fazer as coisas dela. Então, aí... Mystique vai utilizar tokens pra teste. A gente pode cada um abrir a Mystique na máquina, ela pode ter o repositório como centro de conhecimento pra centralizar tudo. E aí a gente vai rodando assincronamente a Mystique, e nisso ela vai appending information pro repositório. E aí ela vai fazer essa sincronicidade. Então cada um de nós vai rodar a Mystique e ela pode ser assíncrona. Então ela roda nos tokens de cada um de nós e ela usa o repositório como uma coordenação mesmo do que ela tá fazendo pra não ficar dando conflito. É, porque eu digo assim, se a gente botar ele no ar, né? Se a gente colocar no ar, aí vai ter que ter API. Pra os outros utilizarem, como a gente não tem esse... Na verdade dá pra gente fazer isso sim. A gente pode deixar um codex aberto e esse codex fica recebendo request e roteando. Não, não assim, mas só pra demo, né? Mas, tipo... Pra depois... O que a gente pode fazer, dá pra pegar aqueles créditos livres da Gemini, dá pra pegar essas coisas. O QEN, eu tenho... Qualquer um de nós aqui, por exemplo, fizer uma conta da QEN Cloud, recebe mais ou menos 40 milhões de tokens em vários modelos diferentes da QEN. Então vocês entram no Alibaba Cloud, QEN.alibabacloud.com, façam uma conta lá, vocês recebem 40 milhões de tokens em vários modelos. Alguns têm dois anos pra expirar, alguns têm poucos dias. Lá também tem Kimi, Max, tem QEN, tem GLM 5.3 Flash, tudo de graça com esses 40 milhões de tokens. Então a gente pode utilizar isso também. Vai no Google e coloca QEN Cloud, e aí você faz uma conta lá e habilita. São mais de 200 modelos que tem lá. Tem modelo de voz, se a gente quiser fazer um real-time com a Mystique, modelo de vídeo. Vou mandar isso que a gente tá falando agora de novo. Codex recebe isso aí, manda pro repositório, sincroniza tudo.

## Leitura operacional (ainda não decidida)

As ideias que aparecem no relato são:

1. Cada participante pode executar uma instância local da Mystique.
2. Cada instância usa a cota, os tokens e as credenciais locais de quem a executa.
3. O repositório GitHub pode funcionar como memória compartilhada, ledger de estado e canal assíncrono entre as instâncias.
4. As instâncias devem acrescentar informação de modo que o trabalho fique visível e os agentes não escrevam sobre o estado uns dos outros.
5. Um servidor/API central não é requisito para a primeira demonstração; um Codex aberto recebendo e roteando requests apareceu como possibilidade separada, ainda exploratória.
6. Créditos de Gemini e de um serviço chamado no relato de “QEN Cloud” foram citados como possíveis fontes de tokens para testes.
7. O relato também mencionou modelos de texto, voz e vídeo e um eventual modo realtime, mas isso não define escopo.

Nenhum desses itens, por si só, escolhe arquitetura, provedor, modelo de segurança, formato de dados ou escopo de demo.

## Alegações que precisam de verificação independente

Os pontos abaixo são **relato do grupo, não fatos verificados nesta sessão**:

- existência, URL correta, elegibilidade e termos atuais de “QEN Cloud”/Alibaba Cloud;
- oferta aproximada de 40 milhões de tokens por conta;
- modelos incluídos, incluindo Kimi, “Max”, Qwen/QEN e “GLM 5.3 Flash”;
- quantidade aproximada de 200 modelos;
- prazo de expiração de cada crédito;
- disponibilidade de modelos de voz, vídeo e realtime;
- créditos gratuitos atuais da Gemini e condições de uso;
- limites de concorrência, rate limits, logging, retenção e uso comercial de cada provedor.

Até existir documentação oficial ou uma chamada de teste autorizada, esses itens não devem aparecer no README como capacidade confirmada, não devem entrar no cálculo de custo e não devem ser tratados como dependências do hackathon.

## Perguntas em aberto

- O repositório será apenas um ledger append-only de fatos e handoffs ou também armazenará estado operacional da Mystique?
- Qual arquivo/formato representa uma execução: Markdown, JSONL, commits por evento ou outro?
- Como duas instâncias evitam conflito: claims do `.coord/`, branches, locks lógicos, rebase e retry, ou uma combinação?
- Quais dados podem ser públicos? O conteúdo das conversas, respostas de modelos e prompts precisam de classificação antes de serem enviados ao GitHub.
- O uso de tokens será sempre local ou haverá um relay/API compartilhado para a demo?
- Quem autoriza uma instância a ler, resumir, alterar ou publicar dados produzidos por outra?
- Como uma execução é retomada depois de falha, rebase rejeitado, rate limit ou expiração de token?
- O fluxo de demo precisa de fallback determinístico/canned data para funcionar sem rede?

## Próximos passos seguros para a ideação

1. Definir uma convenção mínima de eventos e handoffs sem incluir credenciais ou dados privados.
2. Testar o protocolo de commits assíncronos em paralelo e documentar a política de conflito antes de qualquer execução real.
3. Verificar cada programa de créditos somente em documentação oficial e registrar URL, data, elegibilidade, expiração e limites.
4. Separar explicitamente três modos: execução local por participante, relay compartilhado opcional e demo com dados pré-carregados.
5. Escrever uma frase de demo que mostre a Mystique agindo no contexto agente-agente, sem prometer uma plataforma de produção.
6. Só depois de o proprietário encerrar a ideação transformar uma opção em ADR e implementação.

## Limites desta nota

- Nenhum token ou segredo foi incluído.
- Nenhum cadastro, compra, chamada de modelo ou servidor compartilhado foi iniciado.
- Nenhum código de produção foi criado ou alterado.
- O texto registra hipóteses; ele não substitui uma decisão do proprietário nem as instruções de `CLAUDE.md`/`AGENTS.md`.
