import argparse
from collections import Counter
import json
from pathlib import Path
import sys


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Analisa e contabiliza métricas de arquivos de texto."
    )
    parser.add_argument("arquivo", help="Caminho do arquivo de texto")
    parser.add_argument(
        "-l", "--linhas", action="store_true", help="Contabilizar linhas"
    )
    parser.add_argument(
        "-p", "--palavras", action="store_true", help="Contabilizar palavras"
    )
    parser.add_argument(
        "-c", "--chars", action="store_true", help="Contabilizar caracteres"
    )
    parser.add_argument(
        "--top", type=int, default=None, help="Top N palavras mais frequentes"
    )
    parser.add_argument(
        "--json", action="store_true", help="Formatar saída como JSON"
    )
    parser.add_argument(
        "-o", "--saida", default=None, help="Caminho do arquivo de saída"
    )
    return parser.parse_args(args)


def main(argv=None):
    args = parse_args(argv)

    if args.top is not None and args.top < 1:
        sys.stderr.write("Erro: --top deve ser um inteiro maior ou igual a 1.\n")
        sys.exit(2)

    p_arquivo = Path(args.arquivo)
    if not p_arquivo.is_file():
        sys.stderr.write(f"Erro: Arquivo '{args.arquivo}' não encontrado.\n")
        sys.exit(1)

    try:
        conteudo = p_arquivo.read_text(encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"Erro ao ler arquivo: {e}\n")
        sys.exit(1)

    # Se nenhuma flag de contagem foi fornecida, ativa as 3 padrão
    todas_desativadas = not (args.linhas or args.palavras or args.chars or (args.top is not None))
    medir_linhas = args.linhas or todas_desativadas
    medir_palavras = args.palavras or todas_desativadas
    medir_chars = args.chars or todas_desativadas
    medir_top = args.top is not None

    linhas_contadas = len(conteudo.splitlines()) if conteudo else 0
    raw_tokens = conteudo.split()
    tokens_limpos = []
    pontuacao = ".,!?;:\"'()[]{}"
    for t in raw_tokens:
        limpo = t.strip(pontuacao).lower()
        if limpo:
            tokens_limpos.append(limpo)

    palavras_contadas = len(raw_tokens)
    chars_contados = len(conteudo)

    top_lista = []
    if medir_top:
        contagem = Counter(tokens_limpos)
        # Ordena por frequência decrescente e palavra crescente
        ordenadas = sorted(contagem.items(), key=lambda x: (-x[1], x[0]))
        top_lista = [
            {"palavra": p, "ocorrencias": count}
            for p, count in ordenadas[: args.top]
        ]

    # Monta representação
    if args.json:
        dados_saida = {}
        if medir_linhas:
            dados_saida["linhas"] = linhas_contadas
        if medir_palavras:
            dados_saida["palavras"] = palavras_contadas
        if medir_chars:
            dados_saida["caracteres"] = chars_contados
        if medir_top:
            dados_saida["top_palavras"] = top_lista
        texto_final = json.dumps(dados_saida, indent=2, ensure_ascii=False)
    else:
        partes = []
        if medir_linhas:
            partes.append(f"Linhas: {linhas_contadas}")
        if medir_palavras:
            partes.append(f"Palavras: {palavras_contadas}")
        if medir_chars:
            partes.append(f"Caracteres: {chars_contados}")
        if medir_top:
            partes.append("Top Palavras:")
            for item in top_lista:
                partes.append(f"  - {item['palavra']}: {item['ocorrencias']}")
        texto_final = "\n".join(partes)

    if args.saida:
        p_out = Path(args.saida)
        p_out.parent.mkdir(parents=True, exist_ok=True)
        p_out.write_text(texto_final + "\n", encoding="utf-8")
        sys.stdout.write(f"Salvo em {args.saida}\n")
    else:
        sys.stdout.write(texto_final + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
