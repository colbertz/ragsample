from flask import Flask, request, jsonify, render_template, Response
from search import search_in_meili, rerank_results, ask_deepseek
from queue import Queue
import json
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.form.get('query')
    if not user_query:
        return jsonify({'error': 'Query cannot be empty'}), 400

    def generate_response():
        token_queue = Queue()
        
        def process_query():
            try:
                search_results = search_in_meili(user_query)
                reranked_results = json.loads(rerank_results(user_query, search_results))
                
                def token_callback(token):
                    token_queue.put(token)
                
                ask_deepseek(user_query, reranked_results, stream_callback=token_callback)
                token_queue.put(None)  # Signal completion
            except Exception as e:
                token_queue.put(f"Error: {str(e)}")
                token_queue.put(None)

        # Start processing in a separate thread
        thread = threading.Thread(target=process_query)
        thread.start()

        # Stream tokens as they become available
        while True:
            token = token_queue.get()
            if token is None:  # End of stream
                break
            yield token

    return Response(generate_response(), content_type='text/plain', mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
