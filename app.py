from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from busted_ml.ml_pipeline.two_stage_checker import check_news

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
        
        # Use text or URL for checking
        content = text if text else url
        input_url = url if url else None
        
        # Check news with Google News
        result = check_news(content, input_url)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)