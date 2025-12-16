from flask import Flask, request, redirect, session, jsonify
import time
import secrets

from auth.config import Config
from auth.metadata import discover_oauth_endpoints
from auth.pkce import generate_pkce_pair
from auth.oauth_client import build_authorize_url, exchange_code_for_token, refresh_access_token
from fhir.fhir_client import get_patient_bundle

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

# Discover endpoints once at startup
_endpoints = discover_oauth_endpoints(app.config["FHIR_URL"])
AUTH_URL = _endpoints["authorization_endpoint"]
TOKEN_URL = _endpoints["token_endpoint"]


@app.route("/")
def home():
    return '<a href="/launch">Launch ProSribeAI</a>'


@app.route("/launch")
def launch():
    code_verifier, code_challenge = generate_pkce_pair()
    session["code_verifier"] = code_verifier

    state = secrets.token_urlsafe(16)
    session["state"] = state

    auth_url = build_authorize_url(
        authorization_endpoint=AUTH_URL,
        client_id=app.config["CLIENT_ID"],
        redirect_uri=app.config["REDIRECT_URI"],
        scope=app.config["SCOPES"],
        aud=app.config["FHIR_URL"],
        state=state,
        code_challenge=code_challenge,
    )
    print("AUTH_URL:", AUTH_URL)
    print("TOKEN_URL:", TOKEN_URL)
    print("FHIR_URL:", app.config["FHIR_URL"])
    print("FULL AUTHORIZE URL:", auth_url)


    return redirect(auth_url)


@app.route("/callback")
def callback():
    # If eCW sends error
    if request.args.get("error"):
        return jsonify({
            "error": request.args.get("error"),
            "error_description": request.args.get("error_description"),
        }), 400

    if request.args.get("state") != session.get("state"):
        return jsonify({"error": "State mismatch"}), 400

    code = request.args.get("code")
    code_verifier = session.get("code_verifier")
    if not code or not code_verifier:
        return jsonify({"error": "Missing code or code_verifier"}), 400

    tokens = exchange_code_for_token(
        token_endpoint=TOKEN_URL,
        code=code,
        redirect_uri=app.config["REDIRECT_URI"],
        code_verifier=code_verifier,
        client_id=app.config["CLIENT_ID"],
        client_secret=app.config["CLIENT_SECRET"],
    )

    session["access_token"] = tokens.get("access_token")
    session["refresh_token"] = tokens.get("refresh_token")
    session["expires_at"] = time.time() + int(tokens.get("expires_in", 0))
    print("Callback code:", request.args.get("code"))
    print("Callback state:", request.args.get("state"))
    print("Token response:", tokens)



    return redirect("/fetch_data")


@app.route("/fetch_data")
def fetch_data():
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")
    expires_at = session.get("expires_at", 0)

    if not access_token:
        return jsonify({"error": "No access token. Launch again."}), 401

    # refresh if expired
    if time.time() > float(expires_at):
        if not refresh_token:
            return jsonify({"error": "Token expired and no refresh_token available"}), 401

        new_tokens = refresh_access_token(
            token_endpoint=TOKEN_URL,
            refresh_token=refresh_token,
            client_id=app.config["CLIENT_ID"],
            client_secret=app.config["CLIENT_SECRET"],
        )
        session["access_token"] = new_tokens.get("access_token")
        session["refresh_token"] = new_tokens.get("refresh_token", refresh_token)
        session["expires_at"] = time.time() + int(new_tokens.get("expires_in", 0))
        access_token = session["access_token"]

    patient_id = "Lt2IFR5Ah76n4d8TFP5gBJiCIKJuEyZG8Ek3KV3alFE"
    data = get_patient_bundle(app.config["FHIR_URL"], access_token, patient_id)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
