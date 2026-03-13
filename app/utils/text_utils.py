import re
import unicodedata


def remove_accents(text: str) -> str:
    """
    Remove acentos e caracteres diacríticos.
    Exemplo:
    'AVANÇADO' -> 'AVANCADO'
    """
    if not text:
        return ""

    normalized = unicodedata.normalize("NFD", text)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def normalize_spaces(text: str) -> str:
    """
    Remove espaços duplicados e espaços no início/fim.
    """
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def remove_pdf_extension(text: str) -> str:
    """
    Remove a extensão .pdf do final do nome, ignorando maiúsculas/minúsculas.
    """
    if not text:
        return ""

    return re.sub(r"\.pdf$", "", text, flags=re.IGNORECASE).strip()


def remove_d4sign_tokens(text: str) -> str:
    """
    Remove variações comuns do trecho 'pdf-D4Sign' ou semelhantes.
    Exemplos removidos:
    - pdf-D4Sign
    - PDF-D4SIGN
    - pdf d4sign
    - _pdf-D4Sign
    """
    if not text:
        return ""

    cleaned = re.sub(r"[_\-\s]*pdf[_\-\s]*d4sign", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"[_\-\s]*d4sign", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def normalize_filename_text(text: str) -> str:
    """
    Faz uma normalização geral voltada para leitura do nome do arquivo.
    Objetivo:
    - remover extensão .pdf
    - remover tokens de assinatura (D4Sign)
    - trocar underline por espaço
    - manter NR-37 identificável
    - remover acentos
    - converter para maiúsculas
    - limpar espaços extras
    """
    if not text:
        return ""

    text = remove_pdf_extension(text)
    text = remove_d4sign_tokens(text)

    # troca underline por espaço
    text = text.replace("_", " ")

    # padroniza hífens com espaço ao redor quando estiverem soltos
    # mas sem destruir "NR-37"
    text = re.sub(r"\s*-\s*", "-", text)

    text = remove_accents(text)
    text = text.upper()
    text = normalize_spaces(text)

    return text


def normalize_certificate_type_tokens(text: str) -> str:
    """
    Padroniza variações de escrita para facilitar a identificação do tipo.
    Exemplos:
    - NR 37 -> NR-37
    - NR37  -> NR-37
    """
    if not text:
        return ""

    text = re.sub(r"\bNR\s*37\b", "NR-37", text, flags=re.IGNORECASE)
    text = re.sub(r"\bNR37\b", "NR-37", text, flags=re.IGNORECASE)
    text = normalize_spaces(text)
    return text


def normalize_person_name_for_output(text: str) -> str:
    """
    Gera uma versão segura para nome de arquivo final.
    Regras:
    - remove acentos
    - converte para maiúsculas
    - troca espaços por underscore
    - remove caracteres inválidos
    """
    if not text:
        return ""

    text = remove_accents(text)
    text = text.upper()
    text = normalize_spaces(text)

    # remove caracteres inválidos para nome de arquivo no Windows
    text = re.sub(r'[\\/:*?"<>|]', "", text)

    # troca espaços por underscore
    text = text.replace(" ", "_")

    # remove underscores duplicados
    text = re.sub(r"_+", "_", text).strip("_")

    return text


def normalize_input_filename(text: str) -> str:
    """
    Função principal para padronizar um nome de arquivo de entrada.
    """
    text = normalize_filename_text(text)
    text = normalize_certificate_type_tokens(text)
    return text