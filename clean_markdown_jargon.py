import re

def clean_jargon():
    path = r"c:\Users\vinicius\Documents\GeminiCode\Amazon-Bedrock-Agentcore-Curso-Completo\CURSO_COMPLETO_AWS_AGENTCORE.md"
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Dictionary of regex replacements to simplify the text
    replacements = [
        (r'\b[Ee]difique a\b', r'Construa a'),
        (r'\b[Ee]difique\b', r'Construa'),
        (r'\bmatriz orgânica\b', r'infraestrutura'),
        (r'\bmatriz unificada\b', r'estrutura principal'),
        (r'\bmatriz atrelada\b', r'estrutura principal'),
        (r'\bmatriz interligada\b', r'arquitetura conectada'),
        (r'\bmatriz de\b', r'base de'),
        (r'\bmatriz\b', r'estrutura base'),
        (r'\bpuramente\b', r'simplesmente'),
        (r'\borgânica\b', r'prática'),
        (r'\borgânico\b', r'prático'),
        (r'\bsubjacente\b', r'principal'),
        (r'\batrelado\b', r'conectado'),
        (r'\batada\b', r'conectada'),
        (r'\binegociável\b', r'essencial'),
        (r'\binabalável\b', r'robusta'),
        (r'\b[Ee]strito\b', r'Rigoroso'),
        (r'\bestrita\b', r'rígida'),
        (r'\bestrito\b', r'rígido'),
        (r'\biterativo\b', r'passo a passo'),
        (r'\binterligado paralelo\b', r'conectado de forma paralela'),
        (r'\bpurificado\b', r'limpo'),
        (r'\boblitera\b', r'apaga'),
        (r'\bobliterar\b', r'apagar'),
        (r'\btransbordo\b', r'deploy'),
        (r'\bcibernético\b', r'digital'),
        (r'\bemaranhado\b', r'conjunto'),
        (r'\bprovidenciando\b', r'gerando')
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Markdown clean up completed.")

if __name__ == '__main__':
    clean_jargon()
