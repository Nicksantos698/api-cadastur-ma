import os
from flask import Flask, jsonify
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)
CORS(app) # Permite que o site acesse a API

# BUSCANDO AS CHAVES DAS VARIÁVEIS DE AMBIENTE DO RENDER
URL_SUPABASE = os.environ.get("SUPABASE_URL")
CHAVE_PUBLICA = os.environ.get("SUPABASE_KEY")

# Verificação de segurança
if not URL_SUPABASE or not CHAVE_PUBLICA:
    print("ERRO: Variáveis de ambiente SUPABASE_URL ou SUPABASE_KEY não configuradas!")
    supabase = None
else:
    supabase = create_client(URL_SUPABASE, CHAVE_PUBLICA)

@app.route('/')
def index():
    return {
        "projeto": "API Cadastur Maranhão",
        "status": "online",
        "endpoints": {
            "listar_todos": "/api/v1/empresas"
        }
    }

@app.route('/api/v1/empresas', methods=['GET'])
def get_empresas():
    try:
        # CORREÇÃO AQUI: A linha abaixo precisa de 8 espaços (ou 2 tabs) de recuo
        resposta = supabase.table("empresas_ma").select("*").order("id").execute()
        
        return jsonify({
            "quantidade": len(resposta.data),
            "dados": resposta.data
        }), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao conectar ao banco: {str(e)}"}), 500

if __name__ == "__main__":
    # O Render usa a variável de ambiente PORT, se não existir usa 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
