import os

class Config:
    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me")

    # eCW / SMART settings
    CLIENT_ID = "Vhc3_tvE5ZER8Or67MUoQodqY9Kt8sFmxYVLcGuFOeI"
    CLIENT_SECRET ="1Dcoh-_7TAKN4EZYVrhwxISLwRP4jGzM012W5SkThOmHaVC5GUQqzTP2nKCx6-PN"

    # Your FHIR base URL (issuer)
    FHIR_URL = os.getenv("ECW_FHIR_URL", "https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD")

    # Redirect must match EXACTLY in eCW dev portal
    REDIRECT_URI = os.getenv("ECW_REDIRECT_URI", "https://upxlabs-scribe.github.io/uscribe-client/")

    # Scopes (space separated)
    SCOPES = os.getenv("ECW_SCOPES", "openid fhirUser offline_access user/Patient.read")