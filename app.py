from flask import Flask, send_file
import os
app = Flask(__name__)
@app.route('/image')
def serve_image():
    image_path = 'ast_graph.png'
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    else:
        return "Image not found", 404
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)