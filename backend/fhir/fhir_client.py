import requests

def get_patient_bundle(base_url: str, access_token: str, patient_id: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/fhir+json"}

    patient_url = f"{base_url.rstrip('/')}/Patient/{patient_id}"
    allergy_url = f"{base_url.rstrip('/')}/AllergyIntolerance?patient={patient_id}"
    problems_url = f"{base_url.rstrip('/')}/Condition?patient={patient_id}"

    p = requests.get(patient_url, headers=headers, timeout=30)
    a = requests.get(allergy_url, headers=headers, timeout=30)
    c = requests.get(problems_url, headers=headers, timeout=30)

    # Raise if any failed
    p.raise_for_status()
    a.raise_for_status()
    c.raise_for_status()

    return {
        "Patient": p.json(),
        "AllergyIntolerance": a.json(),
        "Condition": c.json()
    }
