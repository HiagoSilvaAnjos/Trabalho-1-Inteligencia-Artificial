from flask import Flask, jsonify, request
import subprocess
import os

app = Flask(__name__)

# Define o caminho base do projeto de forma dinâmica
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/executar', methods=['POST'])
def executar_algoritmo():
    # Comando para rodar o script de Hill Climbing
    script_path = os.path.join(BASE_DIR, 'codigo', 'hill_climbing.py')
    try:
        # Executa e captura o JSON de saída
        resultado = subprocess.check_output(
            ['python', script_path, '--num_execucoes', '30', '--max_iter', '200'],
            text=True
        )
        
        # Salva o resultado em CSV automaticamente (substitui o nó "Salvar CSV" do n8n)
        import pandas as pd
        import json
        try:
            dados = json.loads(resultado)
            df = pd.DataFrame(dados)
            resultados_dir = os.path.join(BASE_DIR, 'resultados')
            os.makedirs(resultados_dir, exist_ok=True)
            df.to_csv(os.path.join(resultados_dir, 'execucoes.csv'), index=False)
        except Exception as e:
            print("Erro ao salvar CSV localmente:", e)

        # Retorna o JSON encapsulado na chave "execucoes" (o n8n "Análise Gemini" exige esse formato: $json.execucoes)
        return jsonify({"execucoes": dados, "total": len(dados)})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/gerar-graficos', methods=['POST'])
def gerar_graficos():
    # Comando para rodar o script de análise e gráficos
    script_path = os.path.join(BASE_DIR, 'codigo', 'analisar_resultados.py')
    try:
        resultado = subprocess.check_output(['python', script_path], text=True)
        return jsonify({
            "status": "sucesso",
            "mensagem": "Gráficos gerados na pasta resultados/",
            "log": resultado
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
