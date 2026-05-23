import os
from translate_dict import translations

def apply_translations():
    base_dir = r"c:\Users\vinicius\Documents\GeminiCode\Amazon-Bedrock-Agentcore-Curso-Completo"
    skip_files = ['append_to_doc.py', 'extract_comments.py', 'extract_py_comments.py', 'translate_dict.py', 'apply_translations.py']
    
    # Files to process
    files_to_process = []
    for root, dirs, files in os.walk(base_dir):
        if '.git' in root or '.venv' in root or '__pycache__' in root or 'cdk.out' in root:
            continue
        for f in files:
            if f.endswith('.py') and f not in skip_files:
                files_to_process.append(os.path.join(root, f))
    
    # Don't forget the main markdown file
    files_to_process.append(os.path.join(base_dir, 'CURSO_COMPLETO_AWS_AGENTCORE.md'))
    
    for path in files_to_process:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        for en, pt in translations.items():
            if not en or not pt:
                continue
            # Simple string replace
            content = content.replace(en, pt)
            
        if content != original_content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {os.path.basename(path)}")

if __name__ == '__main__':
    apply_translations()
