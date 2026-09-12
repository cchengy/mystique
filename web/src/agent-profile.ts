export type AgentDialogue = {
  from: string
  to: string
  text: string
}

const normalize = (value: string) => value.trim().toLocaleLowerCase('pt-BR')

export function latestAgentInteractions(
  interactions: AgentDialogue[],
  identities: string[],
  limit = 3,
): AgentDialogue[] {
  const accepted = new Set(identities.map(normalize))
  return interactions
    .filter(({ from, to }) => accepted.has(normalize(from)) || accepted.has(normalize(to)))
    .slice(-limit)
}
