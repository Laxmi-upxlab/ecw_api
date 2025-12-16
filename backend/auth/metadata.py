import requests

SMART_OAUTH_URIS = "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris"

def discover_oauth_endpoints(fhir_base_url: str) -> dict:
    fhir_base_url = fhir_base_url.rstrip("/")
    metadata_url = f"{fhir_base_url}/metadata?_format=json"

    resp = requests.get(metadata_url, timeout=30)
    resp.raise_for_status()
    cs = resp.json()

    auth_url = None
    token_url = None

    for rest in cs.get("rest", []):
        security = rest.get("security", {})
        for ext in security.get("extension", []):
            if ext.get("url") == SMART_OAUTH_URIS or "oauth-uris" in (ext.get("url") or ""):
                for inner in ext.get("extension", []):
                    if inner.get("url") == "authorize":
                        auth_url = inner.get("valueUri") or inner.get("valueUrl")
                    if inner.get("url") == "token":
                        token_url = inner.get("valueUri") or inner.get("valueUrl")

    return {"authorization_endpoint": auth_url, "token_endpoint": token_url, "raw": cs}
