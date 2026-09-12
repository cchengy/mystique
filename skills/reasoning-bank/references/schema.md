# Schema and layout

Field names follow Istara's `ReasoningMemoryItem`
(`frontend/src/lib/reasoningBankTypes.ts`), so traces move between systems unchanged.

```
<workspace>/
├── bank/
│   └── <id>.json      one trace
└── WIKI.md            rebuilt on every write, for humans
```

| Field | Type | Meaning |
|---|---|---|
| `id` | string | short unique id |
| `agent_id` | string | who or what the trace is about |
| `source_kind` | string | which step produced it |
| `source_id` | string | the specific episode |
| `outcome` | `success` \| `failure` | did the belief hold |
| `title` | string | one line, scannable |
| `description` | string | **the belief tested, in the agent's own words** — safe to recall |
| `content` | string | **the evidence/verdict** — may contain privileged knowledge, do NOT recall into context |
| `tags` | string[] | for retrieval |
| `domain` | string | problem family |
| `evidence_refs` | object[] | pointers to what justified the outcome |
| `judge_score` | number \| null | if a judge scored it |
| `confidence` | number | how sure the agent was **before** the verdict |
| `status` | string | `active` \| `expired` |
| `usage_count` | int | how often it was actually recalled |
| `created_at` | ISO 8601 | with offset |

## Retrieval order

Failures first, then by recency. The purpose of recall is to stop a repeat, and a success the
agent already internalised is worth less than a failure it is about to make again.

## Expiry

A trace never recalled after many chances is noise. Expire by `usage_count == 0` and age rather
than by age alone — age says nothing about whether a memory was useful.
