from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
from collections import Counter
import os

app = Flask(__name__)
CORS(app)

# Function to download spaCy model
def download_spacy_model(model_name):
    try:
        # Check if the model is already downloaded
        spacy.load(model_name)
    except IOError:
        # Download the model if not found
        print(f"Downloading spaCy model: {model_name}")
        os.system(f"python -m spacy download {model_name}")

# Download spaCy model during app startup
download_spacy_model("en_core_web_sm")

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def generate_hashtags_from_text(text, num_hashtags=250):
    # Process the text with spaCy
    doc = nlp(text)

    # Extract keywords (nouns and proper nouns)
    keywords = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'PROPN']]

    # Use Counter to get the most common keywords
    common_keywords = [keyword for keyword, _ in Counter(keywords).most_common(num_hashtags)]

    return common_keywords

@app.route('/get_hashtags', methods=['POST'])
def get_hashtags():
    try:
        data = request.json
        blog_text = data.get('blog_text', '')

        if not blog_text:
            return jsonify({'error': 'Blog text is empty.'}), 400

        hashtags = generate_hashtags_from_text(blog_text)

        # Format hashtags for the React side
        formatted_hashtags = [{'value': hashtag, 'label': '#'+hashtag.capitalize()} for hashtag in hashtags]

        return jsonify({'hashtags': formatted_hashtags})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
