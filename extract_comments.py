import re
import json

def extract_comments():
    with open('CURSO_COMPLETO_AWS_AGENTCORE.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    comments_map = {}
    in_code = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            in_code = not in_code
        elif in_code:
            # Match python style comments that are not inside strings (simple heuristic)
            if '#' in line:
                # Find the last '#' that might be a comment
                parts = line.split('#')
                # A simplistic approach: just grab everything after the first '#' if it's not a color hex
                comment_part = '#' + '#'.join(parts[1:])
                # Exclude if it looks like a hex code, e.g. #FFFFFF
                if not re.match(r'^#[0-9a-fA-F]{6}\b', comment_part.strip()):
                    # Add to map if it has alphabetical characters (not just formatting like ####)
                    if re.search(r'[a-zA-Z]', comment_part):
                        original = comment_part.strip()
                        if original not in comments_map:
                            comments_map[original] = ""

    with open('comments_to_translate.json', 'w', encoding='utf-8') as f:
        json.dump(comments_map, f, indent=2, ensure_ascii=False)
        
if __name__ == '__main__':
    extract_comments()
