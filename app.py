from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import base64
import requests
import logging
import time
from datetime import datetime

load_dotenv()
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variáveis de ambiente
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
MAX_PROMPT_LENGTH = 512
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", '006698')  # Use uma variável de ambiente para a senha

# Definição dos endpoints dos modelos para a API Hugging Face
MODEL_API_URLS = {
    "stable-diffusion": "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
}

# Middleware para autenticação
def require_admin_password(f):
    def decorated_function(*args, **kwargs):
        if request.json.get('password') != ADMIN_PASSWORD:
            logging.warning("Tentativa de acesso sem senha correta")
            return jsonify({'error': 'Senha inválida'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Rota para a página inicial
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Erro ao renderizar index.html: {e}")
        return jsonify({'error': str(e)}), 500

# Rota para carregar arquivos de código
@app.route('/code/<path:filename>')
def get_code(filename):
    admin_cookie = request.cookies.get('admin')
    if admin_cookie != ADMIN_PASSWORD:
        logging.warning("Tentativa de acesso sem cookie de admin válido")
        return jsonify({'error': 'Acesso não autorizado'}), 401
    try:
        # Verifica se o arquivo existe
        full_path = os.path.join(app.root_path, filename)
        if not os.path.exists(full_path):
            logging.error(f"Arquivo {filename} não encontrado")
            return jsonify({'error': f'Arquivo {filename} não encontrado'}), 404
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Erro ao ler arquivo {filename}: {e}")
        return jsonify({'error': str(e)}), 500

# Salvar alterações
@app.route('/update-content', methods=['POST'])
@require_admin_password
def update_content():
    data = request.json
    file_map = {
        'css': 'static/style.css',
        'js': 'static/script.js',
        'html': 'templates/index.html',
        'py': 'app.py'
    }
    
    file_type = data.get('type')
    content = data.get('content')
    
    if not file_type or not content:
        logging.warning("Dados incompletos para atualização de conteúdo")
        return jsonify({'error': 'Dados incompletos'}), 400
    
    file_path = file_map.get(file_type)
    if not file_path:
        logging.warning(f"Tipo de arquivo {file_type} não suportado")
        return jsonify({'error': 'Tipo de arquivo não suportado'}), 400
    
    try:
        full_path = os.path.join(app.root_path, file_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Conteúdo de {file_path} atualizado com sucesso")
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Erro ao atualizar conteúdo de {file_path}: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint para criar nova página
@app.route('/create-page', methods=['POST'])
@require_admin_password
def create_page():
    page_name = request.json.get('pageName')
    content = request.json.get('content', '<h1>Página em branco</h1>')
    
    if not page_name:
        logging.warning("Nome da página não fornecido")
        return jsonify({'error': 'Nome da página não fornecido'}), 400
    
    try:
        full_path = os.path.join(app.root_path, 'templates', f'{page_name}.html')
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Página {page_name} criada com sucesso")
        return jsonify({'status': 'success', 'page_url': f'/{page_name}'})
    except Exception as e:
        logging.error(f"Erro ao criar página {page_name}: {e}")
        return jsonify({'error': str(e)}), 500

# Geração de imagem com retry e validações
@app.route('/gerar-imagem', methods=['POST'])
def gerar_imagem():
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        model = data.get('model', 'stable-diffusion')
        
        # Validações
        if not prompt:
            logging.warning("Prompt vazio")
            return jsonify({'error': 'Prompt vazio'}), 400
        if len(prompt) > MAX_PROMPT_LENGTH:
            logging.warning(f"Prompt excede {MAX_PROMPT_LENGTH} caracteres")
            return jsonify({'error': f'Prompt excede {MAX_PROMPT_LENGTH} caracteres'}), 400
        if model not in MODEL_API_URLS:
            logging.warning(f"Modelo {model} inválido")
            return jsonify({'error': 'Modelo inválido'}), 400

        # Lógica de retry
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    MODEL_API_URLS[model],
                    headers={"Authorization": f"Bearer {HUGGING_FACE_TOKEN}"},
                    json={"inputs": prompt},
                    timeout=30
                )
                
                if response.status_code == 200:
                    logging.info(f"Imagem gerada com sucesso para prompt: {prompt}")
                    return jsonify({
                        'imagem_base64': base64.b64encode(response.content).decode('utf-8'),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'image_size': len(response.content)
                    })
                elif response.status_code == 503 and attempt < max_retries - 1:
                    logging.warning(f"Tentativa {attempt + 1} falhou, restando {max_retries - attempt - 1} tentativas")
                    time.sleep(retry_delay)
                    continue
                else:
                    logging.error(f"Erro ao gerar imagem: {response.text}")
                    return jsonify({'error': response.text}), response.status_code
            except requests.exceptions.RequestException as e:
                logging.error(f"Erro de conexão: {e}")
                if attempt == max_retries - 1:
                    raise

    except Exception as e:
        logging.error(f"Erro desconhecido ao gerar imagem: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint de ping
@app.route('/ping', methods=['GET'])
def ping():
    logging.info("Ping recebido")
    return jsonify({'status': 'online', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)