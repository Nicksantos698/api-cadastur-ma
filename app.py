from flask import Flask, jsonify
from flask_cors import CORS
from supabase import create_client
import os

app = Flask(__name__)
CORS(app) # Permite que o site acesse a API

# Configurações do Supabase
URL_SUPABASE = "https://zaaoyieedbtqpqmnntmp.supabase.co"
CHAVE_PUBLICA = "sb_publishable__3C7E6EfiL96wCzcbQVv2Q_v5aMP9Rp"
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
        # Busca todos os dados da tabela
        # Usamos .select("*") para pegar tudo e .order("nome_prestador") para organizar
        resposta = supabase.table("empresas_ma").select("*").order("nome_prestador").execute()
        
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