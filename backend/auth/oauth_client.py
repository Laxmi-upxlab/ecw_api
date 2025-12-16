import base64
import requests
import urllib.parse

def build_authorize_url(
    authorization_endpoint: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    aud: str,
    state: str,
    code_challenge: str,
) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "aud": aud,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{authorization_endpoint}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"


def exchange_code_for_token(
    token_endpoint: str,
    code: str,
    redirect_uri: str,
    code_verifier: str,
    client_id: str,
    client_secret: str,
) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {basic}"}

    resp = requests.post(token_endpoint, data=data, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(
    token_endpoint: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> dict:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {basic}"}

    resp = requests.post(token_endpoint, data=data, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()
