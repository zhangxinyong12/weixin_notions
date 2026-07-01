import json
import os
import time
import zipfile
from pathlib import Path

import requests


BASE = Path(__file__).resolve().parent
PDF_PATH = BASE / "招商银行交易流水(申请时间2026年06月03日16时39分42秒).pdf"
OUT_DIR = BASE / "mineru_招商银行交易流水_20260603"
STATUS_PATH = OUT_DIR / "mineru_status.json"
ZIP_PATH = OUT_DIR / "mineru_result.zip"
EXTRACT_DIR = OUT_DIR / "extracted"

API_BASE = "https://mineru.net/api/v4"


def require_token():
    token = os.environ.get("MINERU_API_TOKEN", "").strip()
    if not token:
        raise SystemExit("MINERU_API_TOKEN is required")
    return token


def headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


def save_status(payload):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def submit_and_upload(token):
    data = {
        "files": [
            {
                "name": PDF_PATH.name,
                "data_id": "cmb_statement_20260603",
            }
        ],
        "model_version": os.environ.get("MINERU_MODEL_VERSION", "pipeline"),
        "language": "ch",
        "enable_table": True,
        "enable_formula": False,
    }
    res = requests.post(f"{API_BASE}/file-urls/batch", headers=headers(token), json=data, timeout=30)
    res.raise_for_status()
    payload = res.json()
    save_status({"submit": payload})
    if payload.get("code") != 0:
        raise RuntimeError(f"upload url request failed: {payload}")

    batch_id = payload["data"]["batch_id"]
    upload_url = payload["data"]["file_urls"][0]
    with PDF_PATH.open("rb") as f:
        put_res = requests.put(upload_url, data=f, timeout=120)
    if put_res.status_code != 200:
        raise RuntimeError(f"file upload failed: HTTP {put_res.status_code} {put_res.text[:500]}")
    return batch_id, payload


def poll_result(token, batch_id, timeout_seconds=900, interval_seconds=8):
    deadline = time.time() + timeout_seconds
    last_payload = None
    while time.time() < deadline:
        res = requests.get(
            f"{API_BASE}/extract-results/batch/{batch_id}",
            headers=headers(token),
            timeout=30,
        )
        res.raise_for_status()
        payload = res.json()
        last_payload = payload
        save_status({"batch_id": batch_id, "result": payload})
        if payload.get("code") != 0:
            raise RuntimeError(f"poll failed: {payload}")

        results = payload.get("data", {}).get("extract_result", [])
        if results:
            state = results[0].get("state")
            print(f"state={state}", flush=True)
            if state == "done":
                return payload
            if state == "failed":
                raise RuntimeError(f"extract failed: {results[0]}")
        time.sleep(interval_seconds)

    raise TimeoutError(f"MinerU polling timed out. Last payload: {last_payload}")


def download_and_extract(result_payload):
    result = result_payload["data"]["extract_result"][0]
    zip_url = result["full_zip_url"]
    res = requests.get(zip_url, timeout=120)
    res.raise_for_status()
    ZIP_PATH.write_bytes(res.content)

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extractall(EXTRACT_DIR)

    files = sorted(str(p.relative_to(OUT_DIR)) for p in OUT_DIR.rglob("*") if p.is_file())
    manifest = {
        "source_pdf": str(PDF_PATH),
        "batch_id": result_payload["data"]["batch_id"],
        "full_zip_url": zip_url,
        "files": files,
    }
    (OUT_DIR / "mineru_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def main():
    token = require_token()
    batch_id, submit_payload = submit_and_upload(token)
    print(f"batch_id={batch_id}", flush=True)
    result_payload = poll_result(token, batch_id)
    manifest = download_and_extract(result_payload)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
