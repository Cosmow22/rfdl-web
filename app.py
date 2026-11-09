from flask import Flask, render_template, request, Response, url_for
from rfdl import *


def generate_file(media_url: str):
    with requests.get(media_url, stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=8192):
            yield chunk


app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    is_htmx_post = request.method == "POST"
    user_url = request.form.get("input-link") if is_htmx_post else request.args.get("link")
    
    # Simple affichage de la page
    if not user_url:
        return render_template("index.html")

    # Lien invalide : message d'erreur (200 pour que htmx le swap)
    if not INPUT_URL_PATTERN.match(user_url):
        return """
            <span class="error-fade" hx-on::load="setTimeout(() => this.remove(), 5000)">
            ⚠️ Le lien n'est pas correct ! ⚠️
            </span>
        """

    # Lien valide via htmx : on redirige le navigateur vers le GET qui télécharge
    if is_htmx_post:
        return Response("", headers={"HX-Redirect": url_for("index", link=user_url)})

    # Lien valide en GET : téléchargement réel
    media_url = get_podcast_api_url(user_url)
    filename = get_podcast_name(user_url, media_url)
    return Response(
        generate_file(media_url),
        mimetype="audio/mpeg",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

if __name__ == "__main__":
    app.run(debug=True)