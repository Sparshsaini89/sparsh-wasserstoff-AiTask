from flask import Flask, request, jsonify
import requests
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = Flask(__name__)

# Load Sentence-BERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Initialize FAISS index
embedding_dim = 384  # Dimension of embeddings from the Sentence-BERT model
index = faiss.IndexFlatL2(embedding_dim)

# Placeholder for content and embeddings
content = []
embeddings = []

# Fetch content from WordPress site
def fetch_content_from_wordpress():
    global content, embeddings
    response = requests.get('https://your-wordpress-site.com/wp-json/wp/v2/posts')
    posts = response.json()
    content = [post['content']['rendered'] for post in posts]
    embeddings = model.encode(content)
    index.add(np.array(embeddings))

@app.route('/initialize', methods=['GET'])
def initialize():
    fetch_content_from_wordpress()
    return jsonify({"status": "initialized"}), 200

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query')
    user_embedding = model.encode([user_query])
    D, I = index.search(np.array(user_embedding), k=5)
    results = [content[i] for i in I[0]]
    return jsonify({"results": results})

@app.route('/chain_of_thought', methods=['POST'])
def chain_of_thought():
    user_query = request.json.get('query')
    user_embedding = model.encode([user_query])
    D, I = index.search(np.array(user_embedding), k=5)
    results = [content[i] for i in I[0]]

    chain_of_thought = generate_chain_of_thought(user_query, results)
    return jsonify({"chain_of_thought": chain_of_thought})

def generate_chain_of_thought(query, results):
    # Implement your logic for chain of thought here
    thought_process = ["Initial Query: " + query]
    for result in results:
        thought_process.append("Considering: " + result[:150] + "...")
    thought_process.append("Final Response: " + results[0])
    return thought_process

if __name__ == '__main__':
    app.run(debug=True)
