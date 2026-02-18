from flask import Flask, render_template, jsonify, request
import news_service
import os

app = Flask(__name__)

# Configuración inicial 
# En un entorno real esto iría en una base de datos o archivo json persistente
DEFAULT_CONFIG = {
    "topics": [
        "SARLAFT",
        "Lavado de activos",
        "Artículo 323 Código Penal",
        "Financiación del terrorismo",
        "Extinción de dominio"
    ],
    "period": "7d",
    "max_topic": 20
}

current_config = DEFAULT_CONFIG.copy()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    global current_config
    if request.method == 'POST':
        data = request.json
        if 'topics' in data:
            current_config['topics'] = data['topics']
        return jsonify(current_config)
    return jsonify(current_config)

@app.route('/api/news', methods=['GET'])
def get_news():
    # Obtener parámetros si se quieren sobreescribir
    period = request.args.get('period', current_config['period'])
    
    # Llamar al servicio de scraping
    # Esto puede tardar, en producción se usaría Celery/Redis
    try:
        articles = news_service.fetch_news(
            topics=current_config['topics'],
            period=period,
            max_per_topic=current_config['max_topic']
        )
        return jsonify(articles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render asigna un puerto en una variable de entorno llamada PORT
    port = int(os.environ.get("PORT", 5000))
    # '0.0.0.0' permite que el servicio sea accesible desde el exterior
    app.run(host='0.0.0.0', port=port)

