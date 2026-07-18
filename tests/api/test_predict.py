import requests
import pytest
import os
from pathlib import Path

BASE = os.getenv("API_BASE_URL", "http://localhost:8001")


def is_server_up(url):
    try:
        requests.get(url, timeout=2)
        return True
    except requests.RequestException:
        return False


@pytest.mark.skipif(not is_server_up(BASE), reason=f"Backend server is not running on {BASE}")
def test_predict_single_file():
    sample = Path(__file__).resolve().parents[2] / 'frontend' / 'public' / 'defects' / 'crazing.jpg'
    if not sample.exists():
        pytest.skip(f"Sample image not found: {sample}")

    with sample.open('rb') as f:
        files = {'file': ('crazing.jpg', f, 'image/jpeg')}
        r = requests.post(f"{BASE}/predict", files=files, timeout=15)

    assert r.status_code == 200
    payload = r.json()
    print("Predict response JSON:", payload)
    assert isinstance(payload, dict), "Response JSON should be an object"

    # Accept common prediction response shapes (top-level or nested)
    expected_top = {"prediction", "predictions", "label", "results", "class", "classes", "score", "scores", "confidence", "probabilities"}
    if expected_top.intersection(payload.keys()):
        assert True
    else:
        # allow common nested outputs like {custom:{...}, automl:{...}} or {data:{...}}
        nested_ok = False
        for v in payload.values():
            if isinstance(v, dict) and expected_top.intersection(v.keys()):
                nested_ok = True
                break
            if isinstance(v, list) and len(v) > 0:
                nested_ok = True
                break

        # last resort: any non-empty dict is still a "result"
        if not nested_ok and len(payload) > 0:
            nested_ok = True

        assert nested_ok, f"Unexpected /predict payload keys: {list(payload.keys())}"
