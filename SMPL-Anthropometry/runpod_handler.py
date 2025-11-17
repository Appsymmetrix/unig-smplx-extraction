import os
import requests
import runpod

from inference import run_full_pipeline


def download_file(url, save_path):
    """Download remote .pkl into container."""
    response = requests.get(url, timeout=60)
    if response.status_code != 200:
        raise Exception(f"Failed to download file, status={response.status_code}")

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path


def handler(event):
    pkl_url = event["input"].get("pkl_url")
    height_cm = float(event["input"].get("height_cm", 170))

    if not pkl_url:
        return {"error": "Missing required argument: pkl_url"}

    # Download pkl to /tmp
    local_pkl_path = "/tmp/input.pkl"

    try:
        download_file(pkl_url, local_pkl_path)
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

    try:
        output = run_full_pipeline(local_pkl_path, height_cm)
    except Exception as e:
        return {"error": f"Pipeline failed: {str(e)}"}

    return {
        "status": "success",
        "input_height_cm": height_cm,
        "output": output
    }


runpod.serverless.start({"handler": handler})