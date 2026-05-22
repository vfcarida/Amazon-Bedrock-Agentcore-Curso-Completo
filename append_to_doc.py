import os

target_file = r"c:\Users\vinicius\Documents\GeminiCode\Amazon-Bedrock-Agentcore-Curso-Completo\CURSO_COMPLETO_AWS_AGENTCORE.md"
source_file = r"c:\Users\vinicius\Documents\GeminiCode\Amazon-Bedrock-Agentcore-Curso-Completo\temp.md"

if __name__ == "__main__":
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()
    with open(target_file, "a", encoding="utf-8") as f:
        f.write("\n\n" + content + "\n\n")
    print(f"Appended {len(content)} characters to {target_file}")
