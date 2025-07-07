#!/usr/bin/env python3
"""
Script pour générer automatiquement les interpréteurs de variables 
à partir du fichier universal_variables.json
"""

import json
import os
from pathlib import Path

def load_variables(json_file="universal_variables.json"):
    """Charger les variables depuis le fichier JSON"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erreur: Fichier {json_file} non trouvé")
        return {}
    except json.JSONDecodeError:
        print(f"Erreur: Format JSON invalide dans {json_file}")
        return {}

def generate_js_interpreter(variables):
    """Générer l'interpréteur JavaScript"""
    var_exports = []
    var_usage = []
    
    for key, value in variables.items():
        var_name = key.upper()
        var_exports.append(f"  {var_name}: vars.{key}")
        var_usage.append(var_name)
    
    content = f"""const fs = require('fs');
const path = require('path');

// Charger les variables depuis le fichier JSON
function loadVariables() {{
  try {{
    const filePath = path.join(__dirname, 'universal_variables.json');
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
  }} catch (error) {{
    console.error('Erreur lors du chargement des variables:', error);
    return {{}};
  }}
}}

// Exporter les variables
const vars = loadVariables();

module.exports = {{
{',\n'.join(var_exports)}
}};

// Usage:
// const {{ {', '.join(var_usage)} }} = require('./variables');
// console.log(HOST); // "{variables.get('host', '')}"
// console.log(APP_PORT); // "{variables.get('app_port', '')}"
"""
    
    return content

def generate_python_interpreter(variables):
    """Générer l'interpréteur Python"""
    properties = []
    exports = []
    usage = []
    
    for key, value in variables.items():
        var_name = key.upper()
        properties.append(f"""    @property
    def {var_name}(self) -> str:
        return self._vars.get('{key}', '')""")
        exports.append(f"{var_name} = vars.{var_name}")
        usage.append(var_name)
    
    content = f"""import json
import os
from typing import Dict, Any

class Variables:
    def __init__(self):
        self._vars = self._load_variables()
    
    def _load_variables(self) -> Dict[str, Any]:
        \"\"\"Charger les variables depuis le fichier JSON\"\"\"
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'universal_variables.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des variables: {{e}}")
            return {{}}
    
{chr(10).join(properties)}

# Instance globale
vars = Variables()

# Exporter les variables pour un accès direct
{chr(10).join(exports)}

# Usage:
# from variables import {', '.join(usage)}
# print(HOST)  # "{variables.get('host', '')}"
# print(APP_PORT)  # "{variables.get('app_port', '')}"
"""
    
    return content

def generate_shell_interpreter(variables):
    """Générer l'interpréteur Shell"""
    jq_exports = []
    grep_exports = []
    usage_examples = []
    
    for key, value in variables.items():
        var_name = key.upper()
        jq_exports.append(f"        export {var_name}=$(jq -r '.{key}' \"$json_file\")")
        grep_exports.append(f"        export {var_name}=$(grep -o '\"{key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"' \"$json_file\" | cut -d'\"' -f4)")
        usage_examples.append(f"# echo ${var_name}  # \"{value}\"")
    
    content = f"""#!/bin/bash

# Fonction pour charger les variables depuis le fichier JSON
load_variables() {{
    local script_dir="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
    local json_file="$script_dir/universal_variables.json"
    
    if [[ ! -f "$json_file" ]]; then
        echo "Erreur: Fichier universal_variables.json non trouvé" >&2
        return 1
    fi
    
    # Utiliser jq pour parser le JSON (installer avec: apt install jq ou brew install jq)
    if command -v jq &> /dev/null; then
{chr(10).join(jq_exports)}
    else
        # Fallback sans jq (parsing basique)
{chr(10).join(grep_exports)}
    fi
}}

# Charger les variables automatiquement
load_variables

# Usage:
# source ./variables.sh
{chr(10).join(usage_examples)}
"""
    
    return content

def update_interpreters():
    """Mettre à jour tous les interpréteurs"""
    print("🔄 Lecture du fichier universal_variables.json...")
    variables = load_variables()
    
    if not variables:
        print("❌ Aucune variable trouvée, arrêt du script")
        return
    
    print(f"✅ {len(variables)} variable(s) trouvée(s): {list(variables.keys())}")
    
    # Générer les interpréteurs
    interpreters = {
        'variables.js': generate_js_interpreter(variables),
        'variables.py': generate_python_interpreter(variables),
        'variables.sh': generate_shell_interpreter(variables)
    }
    
    # Écrire les fichiers
    for filename, content in interpreters.items():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filename} mis à jour")
        except Exception as e:
            print(f"❌ Erreur lors de l'écriture de {filename}: {e}")
    
    print("\n🎉 Tous les interpréteurs ont été mis à jour!")

if __name__ == "__main__":
    update_interpreters()