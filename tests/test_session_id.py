"""Testes unitários de validação da geração determinística e comprimento de session_id."""

from src.client.session import (
    ensure_min_session_id_length,
    generate_deterministic_session_id,
)


def test_generate_deterministic_session_id_length():
    """Valida se o session_id gerado possui no mínimo 16 caracteres."""
    session_id = generate_deterministic_session_id()
    assert isinstance(session_id, str)
    assert len(session_id) >= 16


def test_ensure_min_session_id_length_expansion():
    """Valida se um session_id curto é expandido para pelo menos 16 caracteres."""
    short_id = "abc"
    expanded = ensure_min_session_id_length(short_id)
    assert len(expanded) >= 16
    assert expanded.startswith("abc-")


def test_ensure_min_session_id_length_preserves_valid_id():
    """Valida se um session_id longo é mantido sem alterações."""
    valid_id = "session-1234567890-abcdef"
    result = ensure_min_session_id_length(valid_id)
    assert result == valid_id
