from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from busted_ml.ml_pipeline.two_stage_checker import check_news
from busted_ml.scraper.scraper import scrape_article

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('Front_End', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('Front_End', filename)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        url = data.get('url', '').strip()
        
        if not text and not url:
            return jsonify({'error': 'No input provided'}), 400
        
        # Get content
        content = text
        input_url = None
        
        if url:
            input_url = url
            # Try to scrape if URL provided
            try:
                article = scrape_article(url, "User")
                content = article['title'] + " " + article['content']
            except:
                content = text if text else "Unable to fetch content"
        
        # Check news with NewsAPI
        result = check_news(content, input_url)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)