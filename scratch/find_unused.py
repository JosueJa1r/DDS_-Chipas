import os
import re

def search_usages():
    keywords = [
        "Agricultor",
        "Semilla",
        "simulacion_monte_carlo",
        "calcular_probabilidad_exito",
        "integral_acumulacion_nutrientes",
        "requiere_enmienda",
        "evaluar_aptitud",
        "vender_cosecha",
        "estimar_rendimiento"
    ]
    
    files_to_check = []
    for root, dirs, files in os.walk("."):
        if ".venv" in root or "__pycache__" in root or ".git" in root or "scratch" in root:
            continue
        for f in files:
            if f.endswith(".py") or f.endswith(".js") or f.endswith(".html"):
                files_to_check.append(os.path.join(root, f))
                
    print(f"Checking usages in {len(files_to_check)} files:")
    for kw in keywords:
        usages = []
        for path in files_to_check:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # Find all occurrences
                matches = re.findall(rf"\b{kw}\b", content)
                # Count definitions versus usages
                # For simplicity, let's find matches and print file paths
                if matches:
                    # Let's count how many times it appears in the file
                    count = len(matches)
                    usages.append((path, count))
        print(f"\nKeyword '{kw}':")
        for u in usages:
            print(f"  In {u[0]}: {u[1]} times")

if __name__ == "__main__":
    search_usages()
