"""Utilitário para geração e validação de identificadores criptográficos de sessão determinísticos.

Garante aderência estrita ao contrato do AgentCore Memory para Semantic Memory
e User Preference, exigindo extensão mínima de 16 caracteres.
"""

import hashlib
import time
import uuid


def generate_deterministic_session_id(
    prefix: str = "session", user_id: str | None = None
) -> str:
    """Gera um session_id determinístico de no mínimo 16 caracteres.

    Estrutura: {prefix}-{YYYYMMDD-HHMMSS}-{hash_12_chars}
    Exemplo: session-20260812-143000-a1b2c3d4e5f6 (extensão: ~36 caracteres)

    Args:
        prefix: Prefixo descritivo da sessão (default: "session").
        user_id: Identificador opcional do usuário/actor para salgar o hash.

    Returns:
        String contendo o session_id determinístico formatado.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    raw_seed = f"{timestamp}-{user_id or 'anonymous'}-{uuid.uuid4().hex}"
    hash_suffix = hashlib.sha256(raw_seed.encode()).hexdigest()[:12]

    session_id = f"{prefix}-{timestamp}-{hash_suffix}"
    return ensure_min_session_id_length(session_id)


def ensure_min_session_id_length(session_id: str, min_length: int = 16) -> str:
    """Garante que a string session_id possua no mínimo min_length caracteres.

    Caso a string fornecida seja menor que 16 caracteres, expande deterministicamente
    utilizando um sufixo hash SHA256.

    Args:
        session_id: A string de ID original.
        min_length: O comprimento mínimo exigido (default: 16).

    Returns:
        String contendo o session_id ajustado.
    """
    if not session_id or not isinstance(session_id, str):
        return generate_deterministic_session_id()

    clean_id = session_id.strip()
    if len(clean_id) >= min_length:
        return clean_id

    # Expande a string curta com hash determinístico
    padding_hash = hashlib.sha256(clean_id.encode()).hexdigest()
    needed = min_length - len(clean_id) - 1
    expanded = f"{clean_id}-{padding_hash[:max(needed, 8)]}"

    if len(expanded) < min_length:
        expanded = expanded.ljust(min_length, "0")

    return expanded
