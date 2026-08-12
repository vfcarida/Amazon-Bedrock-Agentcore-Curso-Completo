"""Testes de integridade da estrutura e regras de políticas Cedar."""

from pathlib import Path


def test_policies_directory_exists_and_contains_cedar_files():
    """Valida se o diretório /policies contém as políticas .cedar esperadas."""
    policies_dir = Path(__file__).resolve().parent.parent / "policies"
    assert policies_dir.exists()
    assert policies_dir.is_dir()

    expected_files = [
        "default_deny.cedar",
        "permit_create_task.cedar",
        "permit_list_tasks.cedar",
        "permit_update_task.cedar",
        "permit_delete_task.cedar",
    ]

    for fname in expected_files:
        pfile = policies_dir / fname
        assert pfile.exists(), f"Política ausente: {fname}"
        content = pfile.read_text(encoding="utf-8")
        assert len(content.strip()) > 0


def test_default_deny_policy_has_forbidden_clause():
    """Valida se a política default_deny contém a cláusula forbidden."""
    policy_path = (
        Path(__file__).resolve().parent.parent
        / "policies"
        / "default_deny.cedar"
    )
    content = policy_path.read_text(encoding="utf-8")
    assert "forbidden" in content
    assert "principal" in content
    assert "action" in content
    assert "resource" in content
