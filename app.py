from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from busted_ml.ml_pipeline.predict import run_prediction
from busted_ml.scraper.google_news_checker import search_google_news, check_domain

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
            return jsonify({'error': 'Please provide text or URL'}), 400

        content = text if text else url

        # Get ML prediction
        ml_result = run_prediction(content)
        prediction = ml_result["prediction"]
        confidence = ml_result["confidence"]

        # Search for verified sources
        verified_articles = search_google_news(content)

        # Check domain if URL provided
        domain_status = check_domain(url) if url else "unknown"

        # Adjust confidence based on verification
        if prediction == "REAL" and len(verified_articles) == 0:
            # ML thinks it's real but no sources found
            prediction = "UNVERIFIED"
            confidence = confidence * 0.6
        elif prediction == "FAKE" and len(verified_articles) == 0:
            # ML thinks it's fake and no sources confirm it
            confidence = confidence * 0.9

        # Build response
        response = {
            "prediction": prediction,
            "confidence": min(confidence, 0.99),
            "verified_sources": verified_articles,
            "domain_status": domain_status
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)