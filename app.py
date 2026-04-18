from flask import Flask, render_template, request, Response
from rfdl import *


def generate_file(media_url: str):
    with requests.get(media_url, stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=8192):
            yield chunk


app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        user_url = request.form["input-link"]
        if INPUT_URL_PATTERN.match(user_url):
            print("link is correct")
            media_url = get_podcast_api_url(user_url)
            filename = get_podcast_name(user_url, media_url)
            print(media_url)
            print(filename)
            return Response(
                generate_file(media_url),
                mimetype="audio/mpeg",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        else: 
            print("link is not correct")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)