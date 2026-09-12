"""Powers of the world's agents: real tools that Mystique can earn.

Each power's description is secret until it is earned: the owning agent receives it
as a tool definition, and the judge uses it to validate Mystique's guess.
"""

import ast
import os
import re
import signal
import subprocess
import sys
import tempfile
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class Poder:
    id: str
    agente: str
    descricao: str
    parametros: dict
    executar: Callable[[dict], str]


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def _obj(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": list(props) if required is None else required}


# --- Byte -------------------------------------------------------------------

def _executar_python(args: dict) -> str:
    with tempfile.TemporaryDirectory() as pasta:
        # New session so a timeout kills the whole process group, not just the child;
        # stdin closed so code calling input() never reads from the demo terminal.
        processo = subprocess.Popen(
            [sys.executable, "-I", "-c", args["codigo"]],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=pasta,
            start_new_session=True,
        )
        try:
            stdout, stderr = processo.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(processo.pid, signal.SIGKILL)
            processo.communicate()
            return "Timed out (10s)."
    saida = (stdout + stderr).strip() or "(no output)"
    return f"exit code {processo.returncode}\n{saida[:4000]}"


def _raio_x_codigo(args: dict) -> str:
    codigo = args["codigo"]
    try:
        arvore = ast.parse(codigo)
    except SyntaxError as erro:
        return f"Syntax error on line {erro.lineno}: {erro.msg}"
    nos = list(ast.walk(arvore))
    funcoes = [n.name for n in nos if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n.name for n in nos if isinstance(n, ast.ClassDef)]
    imports = sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in nos)
    desvios = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp)) for n in nos)
    return (
        f"lines: {len(codigo.splitlines())}\n"
        f"functions: {', '.join(funcoes) or 'none'}\n"
        f"classes: {', '.join(classes) or 'none'}\n"
        f"imports: {imports}\n"
        f"complexity (branches): {desvios}"
    )


# --- Captain Redbeard -------------------------------------------------------

RECEITAS = {
    "fish stew": "Ingredients (4 people): 1 kg white fish; 500 g potatoes; 2 tomatoes; 1 onion; 1 bell pepper; "
    "3 garlic cloves; 100 ml olive oil; 2 limes. Method: season the fish with lime and salt, layer it with the "
    "vegetables, drizzle with olive oil and simmer covered for 30 minutes.",
    "octopus rice": "Ingredients (4 people): 1 kg octopus; 2 cups rice; 1 onion; 2 tomatoes; 4 garlic cloves; "
    "80 ml olive oil; 1 lime. Method: boil the octopus for 40 minutes, sauté onion and garlic, add rice, tomato "
    "and the octopus broth, finish with the octopus in pieces and lime.",
    "codfish fritters": "Ingredients (30 pieces): 500 g desalted cod; 500 g potatoes; 3 eggs; 1 bunch parsley; "
    "1 onion. Method: shred the cod, mix with the mashed potatoes, eggs and seasoning, shape and deep-fry.",
    "bilge feijoada": "Ingredients (8 people): 1 kg black beans; 500 g dried beef; 300 g sausage; 300 g pork ribs; "
    "2 onions; 6 garlic cloves; 4 oranges. Method: soak the beef overnight, cook everything together for 3 hours "
    "and serve with orange to keep scurvy away.",
}


def _livro_de_receitas(args: dict) -> str:
    busca = _normalizar(args["prato"])
    for nome, texto in RECEITAS.items():
        if busca in _normalizar(nome) or _normalizar(nome) in busca:
            return f"{nome.title()}\n{texto}"
    return "Not in the book. Available recipes: " + ", ".join(RECEITAS)


_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")


def _escalar_receita(args: dict) -> str:
    fator = float(args["fator"])

    def multiplicar(m: re.Match) -> str:
        return f"{float(m.group().replace(',', '.')) * fator:g}"

    itens = [item.strip() for item in re.split(r"[;\n]", args["ingredientes"]) if item.strip()]
    return "\n".join(_NUMERO.sub(multiplicar, item, count=1) for item in itens)


# --- Master Ryo -------------------------------------------------------------

def _pomodoro(args: dict) -> str:
    ciclos = max(1, min(int(args.get("ciclos") or 4), 12))
    agora = datetime.now().replace(second=0, microsecond=0)
    t = datetime.strptime(args["inicio"], "%H:%M") if args.get("inicio") else agora
    linhas = []
    for i in range(1, ciclos + 1):
        fim = t + timedelta(minutes=25)
        linhas.append(f"{t:%H:%M}–{fim:%H:%M} focus #{i}: {args['tarefa']}")
        pausa = 15 if i % 4 == 0 else 5
        t = fim + timedelta(minutes=pausa)
        if i < ciclos:
            linhas.append(f"{fim:%H:%M}–{t:%H:%M} {pausa}-minute break")
    return "\n".join(linhas)


def _respiracao_guiada(args: dict) -> str:
    ciclos = max(1, min(int(args.get("ciclos") or 4), 10))
    passos = "inhale through the nose for 4s → hold for 7s → exhale through the mouth for 8s"
    linhas = [f"cycle {i}: {passos}" for i in range(1, ciclos + 1)]
    return "\n".join(linhas) + f"\ntotal duration: {ciclos * 19}s"


# --- Dona Cida --------------------------------------------------------------

CAUSOS = [
    (("rain", "weather", "drought", "harvest", "plan"),
     "In 1974 it rained forty days straight in Ribeirão das Pedras. Stubborn Zé do Açude wouldn't move his cattle "
     "off the lowland because 'rain never lasts'. He lost three cows and gained some sense."),
    (("money", "business", "sale", "company", "work", "startup"),
     "Tonico from the corner store gave credit to the whole town without writing anything down. When he died, "
     "people lined up to pay what they owed. Trust is the best ledger."),
    (("love", "dating", "marriage", "passion"),
     "Filomena waited eleven years for Antero to come back from São Paulo. When he did, she had already married "
     "the mailman who delivered his letters. Whoever is close by also writes."),
    (("technology", "phone", "computer", "internet", "app", "code"),
     "My grandson put one of those recipe apps on my phone. The thing told me to put 200 grams of sugar in the "
     "beans. I deleted it and went back to my mother's notebook."),
    (("fight", "family", "brother", "conflict", "team"),
     "The Pereira brothers didn't speak for twenty years over a fence. They made peace when termites knocked the "
     "fence down. Sometimes the problem falls on its own; you just have to wait."),
]

CONSELHOS = [
    "Holding a grudge is carrying weight for free.",
    "Before you answer angry, have a coffee.",
    "A visit isn't measured by time, it's measured by how much you miss it after.",
    "Whoever cooks in a hurry eats it raw.",
    "Lend money to a friend and you lose either the money or the friend. Choose first.",
    "Open window, fresh house, fresh head too.",
    "Don't trust anyone who flatters too much, or any app that asks for your password.",
]


def _causo(args: dict) -> str:
    tema = _normalizar(args["tema"])
    for palavras, texto in CAUSOS:
        if any(p in tema for p in palavras):
            return texto
    return CAUSOS[len(tema) % len(CAUSOS)][1]


def _conselho_do_dia(args: dict) -> str:
    return CONSELHOS[date.today().toordinal() % len(CONSELHOS)]


# --- Registry ---------------------------------------------------------------

_LISTA = [
    Poder("executar_python", "byte",
          "Runs real Python code in a temporary subprocess with a 10-second timeout and returns the output.",
          _obj({"codigo": {"type": "string", "description": "Python code"}}), _executar_python),
    Poder("raio_x_codigo", "byte",
          "Analyzes Python code without running it: counts lines, lists functions, classes and imports, and "
          "measures complexity.",
          _obj({"codigo": {"type": "string", "description": "Python code"}}), _raio_x_codigo),
    Poder("livro_de_receitas", "capitao-barba-ruiva",
          "Looks up the ship's secret recipe book and returns the ingredients and method for a dish.",
          _obj({"prato": {"type": "string", "description": "dish name"}}), _livro_de_receitas),
    Poder("escalar_receita", "capitao-barba-ruiva",
          "Recalculates the quantities in a list of ingredients by multiplying them by a factor (e.g. doubling "
          "a recipe).",
          _obj({"ingredientes": {"type": "string", "description": "items separated by ; or line breaks"},
                "fator": {"type": "number", "description": "multiplication factor"}}), _escalar_receita),
    Poder("pomodoro", "mestre-ryo",
          "Builds a pomodoro schedule (25 min of focus plus breaks) with real clock times for a task.",
          _obj({"tarefa": {"type": "string", "description": "task"},
                "ciclos": {"type": "integer", "description": "number of cycles"},
                "inicio": {"type": "string", "description": "HH:MM; default: now"}}, ["tarefa"]), _pomodoro),
    Poder("respiracao_guiada", "mestre-ryo",
          "Guides a 4-7-8 breathing exercise with the count for each cycle.",
          _obj({"ciclos": {"type": "integer", "description": "number of cycles"}}, []), _respiracao_guiada),
    Poder("causo", "dona-cida",
          "Pulls from the town's memory a true local tale about a topic.",
          _obj({"tema": {"type": "string", "description": "topic"}}), _causo),
    Poder("conselho_do_dia", "dona-cida",
          "Reveals the advice of the day, which changes with the date.",
          _obj({}, []), _conselho_do_dia),
]

PODERES: dict[str, Poder] = {p.id: p for p in _LISTA}


def poderes_de(agente_id: str) -> list[str]:
    return [p.id for p in _LISTA if p.agente == agente_id]
