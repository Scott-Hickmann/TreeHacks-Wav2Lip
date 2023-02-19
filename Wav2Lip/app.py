from flask import Flask, request, send_file, after_this_request
from flask_cors import CORS
import numpy as np
import scipy
import subprocess
import shortuuid
import platform
import uuid
import os
from inference import infer

app = Flask(__name__)
CORS(app)

@app.route('/animate', methods=["POST"])
def animate():
    name = request.args['name']
    # audio = request.json['audio']
    audio_file = f'temp/audio-{shortuuid.uuid()}.wav'
    f = open(audio_file, 'wb')
    f.write(request.get_data("audio_data"))
    f.close()
    result_file = f"results/{name}.mp4"
    infer(face=f'input/{name}.mp4', audiofile=audio_file, outfile=result_file)
    subprocess.call(f'rm -f {audio_file}', shell=platform.system() != 'Windows')
    data = ""
    @after_this_request
    def remove_file(response):
        try:
            os.remove(result_file)
        except Exception as error:
            app.logger.error("Error removing or closing downloaded file handle", error)
        return response
    return send_file(result_file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)

# curl -X POST http://0.0.0.0:8081/animate -H 'Content-Type: application/json' -d '{"name":"rachelCarson"}'
# curl -X POST https://treehacks-gpu.stanfordmoonshot.club/animate -H 'Content-Type: application/json' -d '{"name":"rachelCarson"}'
# curl -X GET "https://treehacks-gpu.stanfordmoonshot.club/animate?name=rachelCarson"
# gunicorn --certfile "/etc/letsencrypt/live/treehacks-gpu.stanfordmoonshot.club/cert.pem" --keyfile "/etc/letsencrypt/live/treehacks-gpu.stanfordmoonshot.club/privkey.pem" --bind 0.0.0.0:443 app:app --log-level debug