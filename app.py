import os
from flask import Flask, jsonify, request  # Adicionado 'request' aqui
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
            "listar_todos": "/api/v1/empresas",
            "filtros_disponiveis": "?select=coluna1,coluna2&nome=termo_de_busca"
        }
    }

@app.route('/api/v1/empresas', methods=['GET'])
def get_empresas():
    try:
        # 1. Captura parâmetros da URL (Postman)
        # Se não passar nada, seleciona tudo (*)
        colunas = request.args.get('select', '*')
        
        # Se quiser filtrar por parte do nome (ex: ?nome=TURISMO)
        busca_nome = request.args.get('nome', None)

        # 2. Monta a query base
        query = supabase.table("empresas_ma").select(colunas)

        # 3. Aplica filtro de nome se ele existir na URL
        if busca_nome:
            query = query.ilike('nome_prestador', f'%{busca_nome}%')

        # 4. Executa a busca ordenada por ID
        resposta = query.order("id").execute()
        
        return jsonify({
            "quantidade": len(resposta.data),
            "dados": resposta.data
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro na requisição: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
