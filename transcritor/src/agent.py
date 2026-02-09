import argparse
import os
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


def _read_text(path: Path) -> str:
    # Le o arquivo de entrada em UTF-8 e remove espacos extras
    return path.read_text(encoding="utf-8").strip()


def _write_text(path: Path, content: str) -> None:
    # Escreve o texto com quebra de linha final para manter o arquivo bem formatado
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _build_chain(system_msg: str, user_msg: str, model: str, temperature: float):
    # Monta a cadeia LangChain: prompt -> modelo -> parser de texto simples
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_msg),
            ("user", user_msg),
        ]
    )
    llm = ChatGroq(model=model, temperature=temperature)
    return prompt | llm | StrOutputParser()


def main() -> int:
    # Argumentos de entrada e configuracoes do modelo
    parser = argparse.ArgumentParser(description="Corrige e resume transcricao usando LangChain + Groq")
    parser.add_argument("--input", required=True, help="Arquivo .txt da transcricao")
    parser.add_argument(
        "--corrected",
        default="transcricao_corrigida.txt",
        help="Arquivo .txt com a transcricao corrigida",
    )
    parser.add_argument(
        "--summary",
        default="resumo.txt",
        help="Arquivo .txt com o resumo final",
    )
    parser.add_argument("--model", default="llama-3.1-8b-instant", help="Modelo Groq")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperatura")
    args = parser.parse_args()

    # Verifica se a chave da Groq existe no ambiente
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY nao encontrado no ambiente.")
        print("Defina com: $env:GROQ_API_KEY='sua_chave' (PowerShell)")
        return 2

    # Carrega o arquivo de entrada
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Arquivo nao encontrado: {input_path}")
        return 2

    text = _read_text(input_path)
    if not text:
        print("Arquivo de entrada esta vazio.")
        return 2

    # Etapa 1: correcao de escrita (sem inventar informacoes)
    correction_system = (
        "Voce e um revisor de texto. Corrija erros de escrita, pontuacao e acentuacao "
        "mantendo o sentido original. Nao invente informacoes. Preserve o idioma PT-BR." 
        "Entregue apenas o texto corrigido, sem explicacoes."
    )
    correction_user = "Texto para corrigir:\n\n{input_text}"

    correction_chain = _build_chain(
        correction_system,
        correction_user,
        model=args.model,
        temperature=args.temperature,
    )

    corrected_text = correction_chain.invoke({"input_text": text})
    _write_text(Path(args.corrected), corrected_text)

    # Etapa 2: resumo fiel e claro da transcricao corrigida
    summary_system = (
        "Voce e um assistente que resume transcricoes de audio. "
        "Crie um resumo claro, objetivo e fiel ao conteudo. "
        "Se houver passos, pedidos ou decisoes, destaque. "
        "Entregue apenas o resumo, em PT-BR."
    )
    summary_user = "Transcricao corrigida:\n\n{corrected_text}"

    summary_chain = _build_chain(
        summary_system,
        summary_user,
        model=args.model,
        temperature=args.temperature,
    )

    summary_text = summary_chain.invoke({"corrected_text": corrected_text})
    _write_text(Path(args.summary), summary_text)

    print(f"Corrigido salvo em: {args.corrected}")
    print(f"Resumo salvo em: {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
