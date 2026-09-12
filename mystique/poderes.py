"""Poderes dos agentes do mundo: ferramentas reais que a Mystique pode absorver.

A descrição de cada poder é secreta até a absorção: o agente dono a recebe como
definição de ferramenta, e o juiz a usa para validar o palpite da Mystique.
"""

import ast
import re
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
        try:
            r = subprocess.run(
                [sys.executable, "-I", "-c", args["codigo"]],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=pasta,
            )
        except subprocess.TimeoutExpired:
            return "Tempo esgotado (10s)."
    saida = (r.stdout + r.stderr).strip() or "(sem saída)"
    return f"código de saída {r.returncode}\n{saida[:4000]}"


def _raio_x_codigo(args: dict) -> str:
    codigo = args["codigo"]
    try:
        arvore = ast.parse(codigo)
    except SyntaxError as erro:
        return f"Erro de sintaxe na linha {erro.lineno}: {erro.msg}"
    nos = list(ast.walk(arvore))
    funcoes = [n.name for n in nos if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n.name for n in nos if isinstance(n, ast.ClassDef)]
    imports = sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in nos)
    desvios = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp)) for n in nos)
    return (
        f"linhas: {len(codigo.splitlines())}\n"
        f"funções: {', '.join(funcoes) or 'nenhuma'}\n"
        f"classes: {', '.join(classes) or 'nenhuma'}\n"
        f"imports: {imports}\n"
        f"complexidade (desvios de fluxo): {desvios}"
    )


# --- Capitão Barba-Ruiva ----------------------------------------------------

RECEITAS = {
    "caldeirada de peixe": "Ingredientes (4 pessoas): 1 kg de peixe branco; 500 g de batata; 2 tomates; 1 cebola; "
    "1 pimentão; 3 dentes de alho; 100 ml de azeite; 2 limões. Preparo: tempere o peixe com limão e sal, monte "
    "camadas com os legumes, regue com azeite e cozinhe tampado por 30 minutos.",
    "arroz de polvo": "Ingredientes (4 pessoas): 1 kg de polvo; 2 xícaras de arroz; 1 cebola; 2 tomates; "
    "4 dentes de alho; 80 ml de azeite; 1 limão. Preparo: cozinhe o polvo por 40 minutos, refogue cebola e alho, "
    "junte arroz, tomate e o caldo do polvo, finalize com o polvo em pedaços e limão.",
    "bolinho de bacalhau": "Ingredientes (30 unidades): 500 g de bacalhau dessalgado; 500 g de batata; 3 ovos; "
    "1 maço de salsa; 1 cebola. Preparo: desfie o bacalhau, misture com a batata amassada, ovos e temperos, "
    "modele e frite em óleo quente.",
    "feijoada do porão": "Ingredientes (8 pessoas): 1 kg de feijão preto; 500 g de carne seca; 300 g de linguiça; "
    "300 g de costela; 2 cebolas; 6 dentes de alho; 4 laranjas. Preparo: deixe a carne de molho na véspera, "
    "cozinhe tudo junto por 3 horas e sirva com laranja para espantar o escorbuto.",
}


def _livro_de_receitas(args: dict) -> str:
    busca = _normalizar(args["prato"])
    for nome, texto in RECEITAS.items():
        if busca in _normalizar(nome) or _normalizar(nome) in busca:
            return f"{nome.title()}\n{texto}"
    return "Não está no livro. Receitas disponíveis: " + ", ".join(RECEITAS)


_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")


def _escalar_receita(args: dict) -> str:
    fator = float(args["fator"])

    def multiplicar(m: re.Match) -> str:
        return f"{float(m.group().replace(',', '.')) * fator:g}".replace(".", ",")

    itens = [item.strip() for item in re.split(r"[;\n]", args["ingredientes"]) if item.strip()]
    return "\n".join(_NUMERO.sub(multiplicar, item, count=1) for item in itens)


# --- Mestre Ryo -------------------------------------------------------------

def _pomodoro(args: dict) -> str:
    ciclos = max(1, min(int(args.get("ciclos") or 4), 12))
    agora = datetime.now().replace(second=0, microsecond=0)
    t = datetime.strptime(args["inicio"], "%H:%M") if args.get("inicio") else agora
    linhas = []
    for i in range(1, ciclos + 1):
        fim = t + timedelta(minutes=25)
        linhas.append(f"{t:%H:%M}–{fim:%H:%M} foco #{i}: {args['tarefa']}")
        pausa = 15 if i % 4 == 0 else 5
        t = fim + timedelta(minutes=pausa)
        if i < ciclos:
            linhas.append(f"{fim:%H:%M}–{t:%H:%M} pausa de {pausa} min")
    return "\n".join(linhas)


def _respiracao_guiada(args: dict) -> str:
    ciclos = max(1, min(int(args.get("ciclos") or 4), 10))
    passos = "inspire pelo nariz por 4s → segure por 7s → expire pela boca por 8s"
    linhas = [f"ciclo {i}: {passos}" for i in range(1, ciclos + 1)]
    return "\n".join(linhas) + f"\nduração total: {ciclos * 19}s"


# --- Dona Cida --------------------------------------------------------------

CAUSOS = [
    (("chuva", "tempo", "seca", "colheita", "plano"),
     "Em 1974 choveu quarenta dias seguidos em Ribeirão das Pedras. O Zé do Açude, teimoso, não tirou o gado "
     "do baixio porque 'chuva não dura'. Perdeu três vacas e ganhou juízo."),
    (("dinheiro", "negocio", "venda", "empresa", "trabalho", "startup"),
     "O Tonico da venda fiava pra cidade inteira sem anotar nada. Quando ele morreu, o povo fez fila pra pagar "
     "o que devia. Confiança é o melhor caderninho."),
    (("amor", "namoro", "casamento", "paixao"),
     "A Filomena esperou o Antero voltar de São Paulo por onze anos. Quando ele voltou, ela já tinha casado com "
     "o carteiro que trazia as cartas dele. Quem está perto também escreve."),
    (("tecnologia", "celular", "computador", "internet", "aplicativo", "codigo"),
     "Meu neto pôs um tal de aplicativo de receita no meu celular. O trem mandou pôr 200 gramas de açúcar no "
     "feijão. Apaguei e voltei pro caderno da minha mãe."),
    (("briga", "familia", "irmao", "conflito", "equipe"),
     "Os irmãos Pereira ficaram vinte anos sem se falar por causa de uma cerca. Fizeram as pazes quando o "
     "cupim derrubou a cerca. Às vezes o problema cai sozinho, basta esperar."),
]

CONSELHOS = [
    "Quem guarda rancor carrega peso de graça.",
    "Antes de responder bravo, toma um café.",
    "Visita não se mede pelo tempo, se mede pela saudade que deixa.",
    "Quem cozinha com pressa come cru.",
    "Dinheiro emprestado a amigo: ou perde o dinheiro, ou perde o amigo. Escolhe antes.",
    "Janela aberta, casa ventilada, cabeça também.",
    "Não confia em quem elogia demais nem em aplicativo que pede senha.",
]


def _causo(args: dict) -> str:
    tema = _normalizar(args["tema"])
    for palavras, texto in CAUSOS:
        if any(p in tema for p in palavras):
            return texto
    return CAUSOS[len(tema) % len(CAUSOS)][1]


def _conselho_do_dia(args: dict) -> str:
    return CONSELHOS[date.today().toordinal() % len(CONSELHOS)]


# --- Registro ---------------------------------------------------------------

_LISTA = [
    Poder("executar_python", "byte",
          "Executa código Python de verdade num ambiente isolado e devolve a saída.",
          _obj({"codigo": {"type": "string"}}), _executar_python),
    Poder("raio_x_codigo", "byte",
          "Analisa código Python sem executá-lo: conta linhas, lista funções, classes e imports e mede a complexidade.",
          _obj({"codigo": {"type": "string"}}), _raio_x_codigo),
    Poder("livro_de_receitas", "capitao-barba-ruiva",
          "Consulta o livro de receitas secreto do navio e devolve ingredientes e modo de preparo de um prato.",
          _obj({"prato": {"type": "string"}}), _livro_de_receitas),
    Poder("escalar_receita", "capitao-barba-ruiva",
          "Recalcula as quantidades de uma lista de ingredientes multiplicando-as por um fator (ex.: dobrar a receita).",
          _obj({"ingredientes": {"type": "string", "description": "itens separados por ; ou quebra de linha"},
                "fator": {"type": "number"}}), _escalar_receita),
    Poder("pomodoro", "mestre-ryo",
          "Monta um cronograma de pomodoros (25 min de foco mais pausas) com horários reais para uma tarefa.",
          _obj({"tarefa": {"type": "string"}, "ciclos": {"type": "integer"},
                "inicio": {"type": "string", "description": "HH:MM; padrão: agora"}}, ["tarefa"]), _pomodoro),
    Poder("respiracao_guiada", "mestre-ryo",
          "Conduz um exercício de respiração 4-7-8 com a contagem de cada ciclo.",
          _obj({"ciclos": {"type": "integer"}}, []), _respiracao_guiada),
    Poder("causo", "dona-cida",
          "Busca na memória da cidade um causo verdadeiro sobre um tema.",
          _obj({"tema": {"type": "string"}}), _causo),
    Poder("conselho_do_dia", "dona-cida",
          "Revela o conselho do dia, que muda conforme a data.",
          _obj({}, []), _conselho_do_dia),
]

PODERES: dict[str, Poder] = {p.id: p for p in _LISTA}


def poderes_de(agente_id: str) -> list[str]:
    return [p.id for p in _LISTA if p.agente == agente_id]
