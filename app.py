import os
import sys
from colorama import init, Fore, Back, Style

init(autoreset=True)

# Paleta de cores 
TITLE_COLOR   = Fore.CYAN + Style.BRIGHT
BORDER_COLOR  = Fore.BLUE
OPTION_NUM    = Fore.YELLOW + Style.BRIGHT
OPTION_TEXT   = Fore.WHITE
PROMPT_COLOR  = Fore.GREEN + Style.BRIGHT
ERROR_COLOR   = Fore.RED
EXIT_COLOR    = Fore.MAGENTA + Style.BRIGHT
SUCCESS_COLOR = Fore.GREEN + Style.BRIGHT
WARNING_COLOR = Fore.YELLOW
INFO_COLOR    = Fore.CYAN
RESET         = Style.RESET_ALL

# Critérios de qualidade 
PESO_MIN        = 95.0      # gramas
PESO_MAX        = 105.0     # gramas
CORES_APROVADAS = {"azul", "verde"}
COMP_MIN        = 10.0      # centímetros
COMP_MAX        = 20.0      # centímetros
CAP_CAIXA       = 10        # peças por caixa

# Armazenamento em memória
pecas: list[dict]  = []   # todas as peças cadastradas
caixas: list[dict] = []   # caixas (abertas e fechadas)

_proximo_id = 1           # contador sequencial de IDs


def _proximo_id_peca() -> int:
    global _proximo_id
    id_atual = _proximo_id
    _proximo_id += 1
    return id_atual


def _caixa_atual() -> dict | None:
    """Retorna a caixa aberta atual (última da lista), ou None se não houver."""
    if caixas and not caixas[-1]["fechada"]:
        return caixas[-1]
    return None


def _abrir_nova_caixa() -> dict:
    """Cria e registra uma nova caixa aberta."""
    nova = {
        "numero": len(caixas) + 1,
        "pecas": [],
        "fechada": False,
    }
    caixas.append(nova)
    return nova


def _avaliar_qualidade(peso: float, cor: str, comprimento: float) -> tuple[bool, list[str]]:
    """
    Avalia se a peça passa nos critérios de qualidade.
    Retorna (aprovada, lista_de_reprovações).
    """
    reprovacoes = []
    if not (PESO_MIN <= peso <= PESO_MAX):
        reprovacoes.append(
            f"Peso {peso:.1f}g fora do intervalo [{PESO_MIN}g – {PESO_MAX}g]"
        )
    if cor.lower() not in CORES_APROVADAS:
        reprovacoes.append(
            f"Cor '{cor}' não aprovada (aceitas: azul, verde)"
        )
    if not (COMP_MIN <= comprimento <= COMP_MAX):
        reprovacoes.append(
            f"Comprimento {comprimento:.1f}cm fora do intervalo [{COMP_MIN}cm – {COMP_MAX}cm]"
        )
    return (len(reprovacoes) == 0, reprovacoes)


# Helpers de UI

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    clear_screen()
    border = BORDER_COLOR + "═" * 60
    print()
    print(border)
    print(BORDER_COLOR + "║" + " " * 58 + BORDER_COLOR + "║")
    title_line = "  Controle de Produção e Qualidade das Peças Fabricadas   "
    print(BORDER_COLOR + "║" + TITLE_COLOR + title_line + BORDER_COLOR + "║")
    print(BORDER_COLOR + "║" + " " * 58 + BORDER_COLOR + "║")
    print(border)
    print()


def print_menu():
    options = [
        ("1", "Cadastrar nova peça"),
        ("2", "Listar peças aprovadas / reprovadas"),
        ("3", "Remover peça cadastrada"),
        ("4", "Listar caixas fechadas"),
        ("5", "Gerar relatório final"),
        ("0", "Sair"),
    ]

    print(BORDER_COLOR + "  ┌" + "─" * 44 + "┐")
    print(BORDER_COLOR + "  │" + OPTION_TEXT + "  MENU PRINCIPAL" + " " * 28 + BORDER_COLOR + "│")
    print(BORDER_COLOR + "  ├" + "─" * 44 + "┤")

    for num, text in options:
        if num == "0":
            print(BORDER_COLOR + "  ├" + "─" * 44 + "┤")
            print(
                BORDER_COLOR + "  │  "
                + EXIT_COLOR + f"[{num}]"
                + "  "
                + Fore.LIGHTRED_EX + f"{text:<37}"
                + BORDER_COLOR + "│"
            )
        else:
            print(
                BORDER_COLOR + "  │  "
                + OPTION_NUM + f"[{num}]"
                + "  "
                + OPTION_TEXT + f"{text:<37}"
                + BORDER_COLOR + "│"
            )

    print(BORDER_COLOR + "  └" + "─" * 44 + "┘")
    print()


def get_choice():
    prompt = PROMPT_COLOR + "  ▶  Escolha uma opção: " + RESET
    return input(prompt).strip()


def _input_float(prompt: str, unidade: str = "") -> float | None:
    """Lê um número decimal do usuário. Retorna None se inválido."""
    raw = input(PROMPT_COLOR + f"  ▶  {prompt}: " + RESET).strip()
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        print(ERROR_COLOR + f"  ✖  Valor inválido! Digite um número{' em ' + unidade if unidade else ''}.")
        return None


def _input_texto(prompt: str) -> str:
    """Lê uma string não vazia do usuário."""
    return input(PROMPT_COLOR + f"  ▶  {prompt}: " + RESET).strip()


def _separador():
    print(BORDER_COLOR + "  " + "─" * 44)


# 1: Cadastrar nova peça

def cadastrar_peca():
    print()
    print(INFO_COLOR + "  Preencha os dados da peça (ou deixe em branco para cancelar):")
    print()

    # Descrição
    descricao = _input_texto("Descrição")
    if not descricao:
        print(WARNING_COLOR + "\n  ⚠  Operação cancelada (descrição vazia).")
        return

    # Peso 
    peso = _input_float("Peso (g)", "gramas")
    if peso is None:
        return

    # Cor
    cor = _input_texto("Cor").lower()
    if not cor:
        print(WARNING_COLOR + "\n  ⚠  Operação cancelada (cor vazia).")
        return

    # Comprimento
    comprimento = _input_float("Comprimento (cm)", "centímetros")
    if comprimento is None:
        return

    # Avaliação de qualidade 
    aprovada, motivos = _avaliar_qualidade(peso, cor, comprimento)

    # Monta o registro da peça 
    id_peca = _proximo_id_peca()
    peca = {
        "id":          id_peca,
        "descricao":   descricao,
        "peso":        peso,
        "cor":         cor.lower(),
        "comprimento": comprimento,
        "aprovada":    aprovada,
        "motivos":     motivos,   # lista de motivos de reprovação
        "caixa":       None,      # número da caixa (preenchido se aprovada)
    }

    # Armazenamento
    if aprovada:
        # Obtém ou cria a caixa aberta
        caixa = _caixa_atual()
        if caixa is None:
            caixa = _abrir_nova_caixa()
            print(INFO_COLOR + f"\n  📦  Nova caixa #{caixa['numero']} aberta automaticamente.")

        caixa["pecas"].append(id_peca)
        peca["caixa"] = caixa["numero"]

        # Fecha a caixa se atingiu a capacidade máxima
        if len(caixa["pecas"]) >= CAP_CAIXA:
            caixa["fechada"] = True
            print(WARNING_COLOR + f"  🔒  Caixa #{caixa['numero']} fechada "
                  f"({CAP_CAIXA}/{CAP_CAIXA} peças). Nova caixa será aberta na próxima peça aprovada.")

    # Adiciona à lista geral de peças
    pecas.append(peca)

    # Feedback visual
    print()
    _separador()
    if aprovada:
        print(SUCCESS_COLOR + f"  ✔  Peça #{id_peca} APROVADA e armazenada na Caixa #{peca['caixa']}!")
    else:
        print(ERROR_COLOR + f"  ✖  Peça #{id_peca} REPROVADA pelos seguintes motivos:")
        for motivo in motivos:
            print(ERROR_COLOR + f"       • {motivo}")

    _separador()
    print()
    print(OPTION_TEXT + f"  ID:           #{id_peca}")
    print(OPTION_TEXT + f"  Descrição:    {descricao}")
    print(OPTION_TEXT + f"  Peso:         {peso:.1f} g")
    print(OPTION_TEXT + f"  Cor:          {cor.lower()}")
    print(OPTION_TEXT + f"  Comprimento:  {comprimento:.1f} cm")
    _separador()


def listar_pecas():
    reprovadas = [p for p in pecas if not p["aprovada"]]
    aprovadas  = [p for p in pecas if p["aprovada"]]

    if not pecas:
        print()
        print(WARNING_COLOR + "  ⚠  Nenhuma peça cadastrada ainda.")
        return

    # ════════════════════════════════════════════════════════════════
    # Seção 1 – PEÇAS REPROVADAS
    # ════════════════════════════════════════════════════════════════
    print()
    print(BORDER_COLOR + "  ╔" + "═" * 44 + "╗")
    reprov_label = f"  PEÇAS REPROVADAS  ({len(reprovadas)} peça(s))"
    print(BORDER_COLOR + "  ║" + ERROR_COLOR + f"{reprov_label:<44}" + BORDER_COLOR + "║")
    print(BORDER_COLOR + "  ╚" + "═" * 44 + "╝")

    if not reprovadas:
        print(WARNING_COLOR + "\n  ⚠  Nenhuma peça reprovada.\n")
    else:
        for p in reprovadas:
            print()
            print(BORDER_COLOR + "  " + "─" * 46)
            print(ERROR_COLOR  + f"  ✖  Peça #{p['id']}  —  {p['descricao']}")
            print(BORDER_COLOR + "  " + "─" * 46)
            print(OPTION_TEXT  + f"  Peso:         {p['peso']:.1f} g")
            print(OPTION_TEXT  + f"  Cor:          {p['cor']}")
            print(OPTION_TEXT  + f"  Comprimento:  {p['comprimento']:.1f} cm")
            print(BORDER_COLOR + "  " + "┄" * 46)
            print(ERROR_COLOR  + "  Motivo(s):")
            for motivo in p["motivos"]:
                print(ERROR_COLOR + f"    • {motivo}")
            print(BORDER_COLOR + "  " + "─" * 46)

    # ════════════════════════════════════════════════════════════════
    # Seção 2 – PEÇAS APROVADAS (agrupadas por caixa)
    # ════════════════════════════════════════════════════════════════
    print()
    print(BORDER_COLOR + "  ╔" + "═" * 44 + "╗")
    aprov_label = f"  PEÇAS APROVADAS  ({len(aprovadas)} peça(s))"
    print(BORDER_COLOR + "  ║" + SUCCESS_COLOR + f"{aprov_label:<44}" + BORDER_COLOR + "║")
    print(BORDER_COLOR + "  ╚" + "═" * 44 + "╝")

    if not aprovadas:
        print(WARNING_COLOR + "\n  ⚠  Nenhuma peça aprovada.\n")
    else:
        # Itera por cada caixa que tenha ao menos uma peça
        caixas_com_pecas = [c for c in caixas if c["pecas"]]
        for caixa in caixas_com_pecas:
            status_caixa = "🔒 FECHADA" if caixa["fechada"] else "📦 ABERTA"
            ocup = f"{len(caixa['pecas'])}/{CAP_CAIXA}"
            header = f"  Caixa #{caixa['numero']}  {status_caixa}  [{ocup}]"
            print()
            print(INFO_COLOR + "  " + "─" * 44)
            print(INFO_COLOR + header)
            print(INFO_COLOR + "  " + "─" * 44)

            # Cabeçalho da tabela
            print(OPTION_TEXT
                  + f"  {'ID':<5} {'Descrição':<20} {'Peso(g)':<9} {'Cor':<8} {'Comp.(cm)'}")
            print(BORDER_COLOR + "  " + "┄" * 44)

            for id_p in caixa["pecas"]:
                p = next((x for x in pecas if x["id"] == id_p), None)
                if p:
                    desc_trunc = p["descricao"][:18]
                    print(SUCCESS_COLOR
                          + f"  #{p['id']:<4} {desc_trunc:<20} {p['peso']:<9.1f} {p['cor']:<8} {p['comprimento']:.1f}")

        print()
        print(BORDER_COLOR + "  " + "─" * 44)

    # Totais
    print()
    print(BORDER_COLOR + "  " + "═" * 44)
    print(TITLE_COLOR  + f"  Total cadastrado : {len(pecas)} peça(s)")
    print(SUCCESS_COLOR + f"  Aprovadas        : {len(aprovadas)}")
    print(ERROR_COLOR   + f"  Reprovadas       : {len(reprovadas)}")
    print(BORDER_COLOR + "  " + "═" * 44)


def remover_peca():
    print()
    raw = _input_texto("Informe o ID da peça a remover")
    if not raw:
        print(WARNING_COLOR + "\n  ⚠  Operação cancelada.")
        return

    try:
        id_busca = int(raw)
    except ValueError:
        print(ERROR_COLOR + "\n  ✖  ID inválido! Informe um número inteiro.")
        return

    # Busca a peça
    peca = next((p for p in pecas if p["id"] == id_busca), None)

    if peca is None:
        print()
        print(WARNING_COLOR + f"  ⚠  Peça #{id_busca} não encontrada no sistema.")
        return

    # Exibe os dados encontrados
    print()
    _separador()
    print(INFO_COLOR + "  Peça encontrada:")
    _separador()
    status_txt = (SUCCESS_COLOR + "APROVADA" if peca["aprovada"] else ERROR_COLOR + "REPROVADA")
    print(OPTION_TEXT + f"  ID:           #{peca['id']}")
    print(OPTION_TEXT + f"  Descrição:    {peca['descricao']}")
    print(OPTION_TEXT + f"  Peso:         {peca['peso']:.1f} g")
    print(OPTION_TEXT + f"  Cor:          {peca['cor']}")
    print(OPTION_TEXT + f"  Comprimento:  {peca['comprimento']:.1f} cm")
    print(OPTION_TEXT + f"  Status:       " + status_txt)
    if peca["aprovada"]:
        print(OPTION_TEXT + f"  Caixa:        #{peca['caixa']}")
    else:
        for motivo in peca["motivos"]:
            print(ERROR_COLOR + f"       • {motivo}")
    _separador()

    # Confirmação 
    print()
    confirmacao = _input_texto("Confirma a exclusão? (s/N)").lower()
    if confirmacao != "s":
        print(WARNING_COLOR + "\n  ⚠  Exclusão cancelada.")
        return

    # Remove da caixa (se aprovada)
    if peca["aprovada"] and peca["caixa"] is not None:
        caixa = next((c for c in caixas if c["numero"] == peca["caixa"]), None)
        if caixa and id_busca in caixa["pecas"]:
            caixa["pecas"].remove(id_busca)
            # Reabre a caixa caso estivesse fechada (voltou a ter vaga)
            if caixa["fechada"]:
                caixa["fechada"] = False
                print(INFO_COLOR + f"  📦  Caixa #{caixa['numero']} reaberta "
                      f"(agora com {len(caixa['pecas'])}/{CAP_CAIXA} peças).")

    # Remove da lista geral 
    pecas.remove(peca)

    print()
    print(SUCCESS_COLOR + f"  ✔  Peça #{id_busca} removida com sucesso!")
    _separador()


def listar_caixas():
    fechadas = [c for c in caixas if c["fechada"]]
    abertas  = [c for c in caixas if not c["fechada"] and c["pecas"]]

    if not caixas or not any(c["pecas"] for c in caixas):
        print()
        print(WARNING_COLOR + "  ⚠  Nenhuma caixa criada ainda.")
        return

    if not fechadas:
        print()
        print(WARNING_COLOR + "  ⚠  Nenhuma caixa fechada até o momento.")
        if abertas:
            print(INFO_COLOR + f"  ℹ  Há {len(abertas)} caixa(s) ainda aberta(s).")
        return

    # Título 
    print()
    print(BORDER_COLOR + "  ╔" + "═" * 44 + "╗")
    label = f"  CAIXAS FECHADAS  ({len(fechadas)} caixa(s))"
    print(BORDER_COLOR + "  ║" + INFO_COLOR + f"{label:<44}" + BORDER_COLOR + "║")
    print(BORDER_COLOR + "  ╚" + "═" * 44 + "╝")

    # Detalhe de cada caixa fechada
    for caixa in fechadas:
        total_cx = len(caixa["pecas"])
        print()
        print(INFO_COLOR + "  " + "═" * 46)
        print(INFO_COLOR + f"  🔒  Caixa #{caixa['numero']}  —  {total_cx}/{CAP_CAIXA} peças  [FECHADA]")
        print(INFO_COLOR + "  " + "─" * 46)

        # Cabeçalho da tabela
        print(OPTION_TEXT + f"  {'ID':<5} {'Descrição':<20} {'Peso(g)':<9} {'Cor':<8} {'Comp.(cm)'}")
        print(BORDER_COLOR + "  " + "┄" * 46)

        for id_p in caixa["pecas"]:
            p = next((x for x in pecas if x["id"] == id_p), None)
            if p:
                desc_trunc = p["descricao"][:18]
                print(SUCCESS_COLOR
                      + f"  #{p['id']:<4} {desc_trunc:<20} {p['peso']:<9.1f} {p['cor']:<8} {p['comprimento']:.1f}")

        print(INFO_COLOR + "  " + "═" * 46)

    # Resumo geral
    total_pecas_fechadas = sum(len(c["pecas"]) for c in fechadas)
    print()
    print(BORDER_COLOR + "  " + "═" * 46)
    print(TITLE_COLOR  + f"  Caixas fechadas  : {len(fechadas)}")
    if abertas:
        print(INFO_COLOR + f"  Caixas abertas   : {len(abertas)}")
    print(SUCCESS_COLOR + f"  Peças em caixas fechadas : {total_pecas_fechadas}")
    print(BORDER_COLOR + "  " + "═" * 46)


def gerar_relatorio():
    if not pecas:
        print()
        print(WARNING_COLOR + "  ⚠  Nenhuma peça cadastrada. Relatório indisponível.")
        return

    aprovadas  = [p for p in pecas if p["aprovada"]]
    reprovadas = [p for p in pecas if not p["aprovada"]]
    fechadas   = [c for c in caixas if c["fechada"]]
    abertas    = [c for c in caixas if not c["fechada"] and c["pecas"]]
    total      = len(pecas)

    # ════════════════════════════════════════════════════════════════
    # Cabeçalho do relatório
    # ════════════════════════════════════════════════════════════════
    print()
    print(BORDER_COLOR + "  ╔" + "═" * 50 + "╗")
    print(BORDER_COLOR + "  ║" + TITLE_COLOR + f"{'  RELATÓRIO FINAL DE PRODUÇÃO':<50}" + BORDER_COLOR + "║")
    print(BORDER_COLOR + "  ╚" + "═" * 50 + "╝")

    # ════════════════════════════════════════════════════════════════
    # Seção 1 – Resumo geral
    # ════════════════════════════════════════════════════════════════
    pct_apr  = (len(aprovadas)  / total * 100) if total else 0
    pct_repr = (len(reprovadas) / total * 100) if total else 0

    print()
    print(BORDER_COLOR + "  " + "─" * 50)
    print(TITLE_COLOR  + "  1. RESUMO GERAL")
    print(BORDER_COLOR + "  " + "─" * 50)
    print(OPTION_TEXT  + f"  Total de peças cadastradas : {total}")
    print(SUCCESS_COLOR + f"  Peças aprovadas            : {len(aprovadas)}  ({pct_apr:.1f}%)")
    print(ERROR_COLOR   + f"  Peças reprovadas           : {len(reprovadas)}  ({pct_repr:.1f}%)")
    print(BORDER_COLOR + "  " + "─" * 50)

    # ════════════════════════════════════════════════════════════════
    # Seção 2 – Peças reprovadas e motivos
    # ════════════════════════════════════════════════════════════════
    print()
    print(BORDER_COLOR + "  " + "─" * 50)
    print(TITLE_COLOR  + "  2. PEÇAS REPROVADAS E MOTIVOS")
    print(BORDER_COLOR + "  " + "─" * 50)

    if not reprovadas:
        print(SUCCESS_COLOR + "\n  ✔  Nenhuma peça reprovada!\n")
    else:
        # Agrupa e conta os motivos (texto base sem valores numéricos)
        from collections import Counter

        def _tipo_motivo(motivo: str) -> str:
            """Extrai o tipo de critério do texto do motivo."""
            m = motivo.lower()
            if "peso" in m:
                return "Peso fora do intervalo permitido (95g – 105g)"
            if "cor" in m:
                return "Cor não aprovada (somente azul ou verde)"
            if "comprimento" in m:
                return "Comprimento fora do intervalo permitido (10cm – 20cm)"
            return motivo

        contador_motivos: Counter = Counter()
        for p in reprovadas:
            for motivo in p["motivos"]:
                contador_motivos[_tipo_motivo(motivo)] += 1

        # Lista das peças
        print()
        print(OPTION_TEXT + f"  {'ID':<5} {'Descrição':<22} {'Motivos'}")
        print(BORDER_COLOR + "  " + "┄" * 50)
        for p in reprovadas:
            desc_trunc   = p["descricao"][:20]
            primeiro_mot = _tipo_motivo(p["motivos"][0])[:28] if p["motivos"] else ""
            extra        = f"  (+{len(p['motivos'])-1})" if len(p["motivos"]) > 1 else ""
            print(ERROR_COLOR + f"  #{p['id']:<4} {desc_trunc:<22} {primeiro_mot}{extra}")

        # Consolidado dos motivos
        print()
        print(BORDER_COLOR + "  " + "┄" * 50)
        print(WARNING_COLOR + "  Consolidado por critério de reprovação:")
        print(BORDER_COLOR + "  " + "┄" * 50)
        for tipo, qtd in contador_motivos.most_common():
            barra = "█" * qtd
            print(WARNING_COLOR + f"  {barra:<12} {qtd:>2}x  {tipo}")
        print(BORDER_COLOR + "  " + "─" * 50)

    # ════════════════════════════════════════════════════════════════
    # Seção 3 – Caixas utilizadas
    # ════════════════════════════════════════════════════════════════
    print()
    print(BORDER_COLOR + "  " + "─" * 50)
    print(TITLE_COLOR  + "  3. CAIXAS UTILIZADAS")
    print(BORDER_COLOR + "  " + "─" * 50)

    caixas_usadas = [c for c in caixas if c["pecas"]]
    if not caixas_usadas:
        print(WARNING_COLOR + "\n  ⚠  Nenhuma caixa utilizada.\n")
    else:
        print()
        print(OPTION_TEXT + f"  {'Caixa':<8} {'Status':<12} {'Peças':>6}  {'Ocupação'}")
        print(BORDER_COLOR + "  " + "┄" * 50)
        for c in caixas_usadas:
            status  = "🔒 FECHADA" if c["fechada"] else "📦 ABERTA"
            qtd     = len(c["pecas"])
            barra   = "█" * qtd + "░" * (CAP_CAIXA - qtd)
            cor_ln  = INFO_COLOR if c["fechada"] else SUCCESS_COLOR
            print(cor_ln + f"  #{c['numero']:<7} {status:<14} {qtd:>4}   [{barra}] {qtd}/{CAP_CAIXA}")

        print()
        print(BORDER_COLOR + "  " + "┄" * 50)
        print(TITLE_COLOR  + f"  Total de caixas utilizadas : {len(caixas_usadas)}")
        print(INFO_COLOR   + f"  Caixas fechadas            : {len(fechadas)}")
        if abertas:
            print(SUCCESS_COLOR + f"  Caixas abertas (em uso)    : {len(abertas)}")
        print(SUCCESS_COLOR + f"  Peças em caixas fechadas   : {sum(len(c['pecas']) for c in fechadas)}")
        print(BORDER_COLOR + "  " + "─" * 50)


# Roteador de opções

def handle_option(choice: str) -> bool:
    """Processa a opção escolhida. Retorna False quando deve sair."""
    actions = {
        "1": ("Cadastrar nova peça",              cadastrar_peca),
        "2": ("Listar peças aprovadas/reprovadas", listar_pecas),
        "3": ("Remover peça cadastrada",           remover_peca),
        "4": ("Listar caixas fechadas",            listar_caixas),
        "5": ("Gerar relatório final",             gerar_relatorio),
    }

    if choice == "0":
        print()
        print(EXIT_COLOR + "  Encerrando o sistema... Até logo! 👋")
        print()
        return False

    if choice in actions:
        label, func = actions[choice]
        print()
        print(BORDER_COLOR + "  " + "─" * 44)
        print(TITLE_COLOR + f"  ► {label}")
        print(BORDER_COLOR + "  " + "─" * 44)
        func()
        print()
        input(PROMPT_COLOR + "  Pressione ENTER para voltar ao menu...")
        return True

    print()
    print(ERROR_COLOR + "  ✖  Opção inválida! Por favor, escolha entre 0 e 5.")
    print()
    return True


# Ponto de entrada 

def main():
    running = True
    while running:
        print_header()
        print_menu()
        choice = get_choice()
        running = handle_option(choice)


if __name__ == "__main__":
    main()