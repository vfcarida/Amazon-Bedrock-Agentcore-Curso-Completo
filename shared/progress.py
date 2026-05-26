"""Progress tracking for workshop modules.

Displays a visual checklist showing which modules have been completed,
based on the presence of deployed resources (saved configs).
"""
# Módulo de progresso: Exibe um checklist visual no terminal mostrando
# quais módulos do curso já foram completados. Detecta automaticamente
# o progresso verificando se os recursos correspondentes existem na AWS.

from . import utils

# Definições dos Módulos: (id, nome_amigável, verifica_se_esta_pronto)
MODULES = [
    ("00", "Prerequisites", lambda: bool(utils.get_all_cfn_outputs())),
    ("01", "Introduction & CLI", lambda: True),  # Sem recursos passíveis de deploy nessa fase
    ("02", "Runtime", lambda: utils.load_config("runtime") is not None),
    ("03", "Tools", lambda: _runtime_has_tools()),
    ("04", "Memory", lambda: utils.load_config("memory") is not None),
    ("05", "Gateway & Identity", lambda: utils.load_config("gateway") is not None),
    ("06", "Policy", lambda: utils.load_config("policy") is not None),
    ("07", "Observability & Evaluations", lambda: utils.load_config("evaluations") is not None),
    ("08", "Full Deployment", lambda: _all_services_active()),
]


def _runtime_has_tools() -> bool:
    """Check if the runtime is deployed (tools are part of agent code, not separate config)."""
    return utils.load_config("runtime") is not None


def _all_services_active() -> bool:
    """Check if all core services have configs."""
    required = ["runtime", "memory", "gateway", "policy"]
    return all(utils.load_config(name) is not None for name in required)


def show(current_module: str | None = None) -> None:
    # Mostra uma caixa visual com o progresso do workshop.
    # Cada módulo é marcado com:
    # ✅ = Completado (recurso detectado)
    # 🔵 = Módulo atual (você está aqui)
    # ⬜ = Ainda não completado
    """Display the workshop progress checklist.

    Args:
        current_module: The module ID currently being worked on (e.g., "02").
    """
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║           AgentCore Workshop Progress                    ║")
    print("╠══════════════════════════════════════════════════════════╣")

    for mod_id, label, check_fn in MODULES:
        try:
            done = check_fn()
        except Exception:
            done = False

        if mod_id == current_module:
            icon = "🔵"
            suffix = " ← you are here"
        elif done:
            icon = "✅"
            suffix = ""
        else:
            icon = "⬜"
            suffix = ""

        print(f"║  {icon}  Module {mod_id}: {label:<36}{suffix:>4} ║")

    print("╚══════════════════════════════════════════════════════════╝")
    print()


def check_prerequisites() -> dict:
    """Verify that CloudFormation prerequisites are in place.

    Returns:
        Dict of CFN outputs if found, raises otherwise.
    """
    outputs = utils.get_all_cfn_outputs()
    if not outputs:
        print("❌ No CloudFormation outputs found.")
        print("   The prerequisites stack may not be deployed yet.")
        print("   Check the Workshop Studio console for stack status.")
        raise RuntimeError("Prerequisites stack not found.")

    print("✅ CloudFormation prerequisites detected:")
    for key, value in sorted(outputs.items()):
        # Abrevia valores muito longos pra não quebrar a tela do terminal
        display = value if len(value) < 60 else value[:57] + "..."
        print(f"   {key}: {display}")
    print()
    return outputs
