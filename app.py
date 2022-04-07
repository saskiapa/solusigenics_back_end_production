from flask import Flask, request
from flask_cors import CORS
import handler

app = Flask(__name__)
CORS(app)


@app.route('/get_video_by_disease')
def get_video_by_disease():
    query = request.args.get('query')
    return handler.get_video_by_disease(query)


@app.route('/search/<disease>/<query>')
def search(disease, query):
    return handler.search(disease, query)


@app.route('/get_play_url_by_id/<id>')
def get_play_url_by_id(id):
    source = request.args.get('source')
    return handler.get_play_url_by_id(id, source)


@app.route('/get_videos_detail', methods = ['POST', 'GET'])
def get_video_detail():
    body = request.json
    return handler.get_videos_detail(body)


@app.route('/get_video_recommendation', methods = ['POST', 'GET'])
def get_video_recommendation():
    body = request.json
    return handler.get_video_recommendation(body)


if __name__ == "__main__":
    app.run()
