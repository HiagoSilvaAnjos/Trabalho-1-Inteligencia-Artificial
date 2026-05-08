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

@app.route('/salvar-metricas', methods=['POST'])
def salvar_metricas():
    try:
        import json
        dados_gemini = request.get_json()
        
        # O Gemini retorna a estrutura candidates[0].content.parts[0].text
        # Precisamos extrair esse texto, limpá-lo e convertê-lo para dicionário Python.
        texto_resposta = dados_gemini.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        if not texto_resposta:
            return jsonify({"erro": "Resposta do Gemini não contém texto."}), 400
            
        # Tentar fazer o parse do texto para JSON
        metricas_limpas = json.loads(texto_resposta)
        
        # Salvar fisicamente o arquivo
        resultados_dir = os.path.join(BASE_DIR, 'resultados')
        os.makedirs(resultados_dir, exist_ok=True)
        caminho_arquivo = os.path.join(resultados_dir, 'metricas_gemini.json')
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(metricas_limpas, f, indent=4, ensure_ascii=False)
            
        return jsonify({
            "status": "sucesso",
            "mensagem": "Métricas do Gemini salvas com sucesso.",
            "arquivo": caminho_arquivo,
            "metricas": metricas_limpas
        })
    except json.JSONDecodeError:
        return jsonify({"erro": "O texto retornado pelo Gemini não é um JSON válido.", "texto_recebido": texto_resposta}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
