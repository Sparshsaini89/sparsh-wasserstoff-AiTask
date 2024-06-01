from flask import Flask, request, jsonify
import requests
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration

app = Flask(__name__)

# Load Sentence-BERT model
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load RAG model and tokenizer
rag_tokenizer = RagTokenizer.from_pretrained('facebook/rag-sequence-nq')
rag_retriever = RagRetriever.from_pretrained('facebook/rag-sequence-nq', index_name="exact", use_dummy_dataset=True)
rag_model = RagSequenceForGeneration.from_pretrained('facebook/rag-sequence-nq', retriever=rag_retriever)

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
    embeddings = embedding_model.encode(content)
    index.add(np.array(embeddings))

@app.route('/initialize', methods=['GET'])
def initialize():
    fetch_content_from_wordpress()
    return jsonify({"status": "initialized"}), 200

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query')
    user_embedding = embedding_model.encode([user_query])
    D, I = index.search(np.array(user_embedding), k=5)
    results = [content[i] for i in I[0]]
    return jsonify({"results": results})

@app.route('/chain_of_thought', methods=['POST'])
def chain_of_thought():
    user_query = request.json.get('query')
    user_embedding = embedding_model.encode([user_query])
    D, I = index.search(np.array(user_embedding), k=5)
    results = [content[i] for i in I[0]]

    chain_of_thought = generate_chain_of_thought(user_query, results)
    return jsonify({"chain_of_thought": chain_of_thought})

def generate_chain_of_thought(query, results):
    thought_process = ["Initial Query: " + query]
    for result in results:
        thought_process.append("Considering: " + result[:150] + "...")

    final_response = generate_response(query, results)
    thought_process.append("Final Response: " + final_response)
    return thought_process

def generate_response(query, results):
    context = query + " ".join(results)
    inputs = rag_tokenizer(context, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = rag_model.generate(**inputs, max_length=150, num_return_sequences=1)
    response = rag_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

if __name__ == '__main__':
    app.run(debug=True)
