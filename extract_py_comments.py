import os
import re
import json

def extract_py_comments():
    comments_map = {}
    base_dir = r"c:\Users\vinicius\Documents\GeminiCode\Amazon-Bedrock-Agentcore-Curso-Completo"
    skip_files = ['append_to_doc.py', 'extract_comments.py', 'extract_py_comments.py']
    
    for root, dirs, files in os.walk(base_dir):
        if '.git' in root or '.venv' in root or '__pycache__' in root or 'cdk.out' in root:
            continue
        for f in files:
            if f.endswith('.py') and f not in skip_files:
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith('#'):
                        # Simplistic heuristic for full-line comments
                        comment = line.strip()
                        # Exclude #!/usr/bin/env python, coding: utf-8, etc.
                        if comment.startswith('#!') or 'coding: utf-8' in comment:
                            continue
                        if re.search(r'[a-zA-Z]', comment):
                            if comment not in comments_map:
                                comments_map[comment] = ""
                    elif '#' in line:
                        # inline comment
                        parts = line.split('#', 1)
                        # Avoid matching '#' inside strings if possible. 
                        # A very crude check: count quotes before '#'
                        before = parts[0]
                        if before.count('"') % 2 == 0 and before.count("'") % 2 == 0:
                            comment = '#' + parts[1]
                            if re.search(r'[a-zA-Z]', comment):
                                if comment not in comments_map:
                                    comments_map[comment] = ""

    # Also grab comments from the markdown file since we need to translate those too, 
    # but the ones that are still in English.
    
    with open(os.path.join(base_dir, 'py_comments.json'), 'w', encoding='utf-8') as f:
        json.dump(comments_map, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    extract_py_comments()
