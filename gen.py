import json
import os
import re
from urllib.parse import urlparse
import requests

# Input and Output configurations
INPUT_JSON = "tvs.json"
OUTPUT_JSON = "tv.json"
OUTPUT_DIR = "m3u8"

# Ensure local folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define your GitHub raw base URL exactly as requested
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/anbuinfosec/ott-scraper/refs/heads/main/m3u8"

HEADERS = {
    "Origin": "https://iscreen.com.bd",
    "Referer": "https://iscreen.com.bd/",
    "Accept-Encoding": "gzip",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; 2201117TG Build/TKQ1.221114.001)",
    "Connection": "Keep-Alive",
}

def sanitize_filename(name):
    """Converts channel name into a clean filename."""
    name = name.lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9__\-]", "", name) + ".m3u8"

def download_m3u8(url, filepath):
    """Downloads the m3u8 playlist file locally."""
    try:
        parsed_url = urlparse(url)
        headers = HEADERS.copy()
        headers["Host"] = parsed_url.netloc

        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Downloaded: {filepath}")
            return True
        else:
            print(f"Failed to download {url}. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error handling {url}: {e}")
        return False

def main():
    if not os.path.exists(INPUT_JSON):
        print(f"Error: {INPUT_JSON} not found.")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        channels = json.load(f)

    updated_channels = []

    for channel in channels:
        name = channel.get("name")
        logo = channel.get("logo")
        stream_url = channel.get("streamUrl")

        print(f"Processing: {name}")
        filename = sanitize_filename(name)
        local_filepath = os.path.join(OUTPUT_DIR, filename)

        # Download the file locally for GitHub actions to track
        success = download_m3u8(stream_url, local_filepath)

        if success:
            # Construct the absolute public GitHub URL
            # Example: https://raw.githubusercontent.com/anbuinfosec/ott-scraper/refs/heads/main/m3u8/australia_vs_turkiye.m3u8
            final_stream_url = f"{GITHUB_RAW_BASE}/{filename}"
        else:
            final_stream_url = stream_url

        updated_channels.append({
            "name": name,
            "logo": logo,
            "streamUrl": final_stream_url
        })

    # Save the polished output map
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(updated_channels, f, indent=2, ensure_ascii=False)

    print(f"\nSaved absolute URLs mapping to '{OUTPUT_JSON}'")

if __name__ == "__main__":
    main()
