import json
import os
import re
from urllib.parse import urlparse
import requests

# Input and Output file configurations
INPUT_JSON = "tvs.json"
OUTPUT_JSON = "tv.json"
OUTPUT_DIR = "m3u8"

# Ensure the directory to store m3u8 files exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Custom headers optimized for the stream servers provided
HEADERS = {
    "Origin": "https://iscreen.com.bd",
    "Referer": "https://iscreen.com.bd/",
    "Accept-Encoding": "gzip",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; 2201117TG Build/TKQ1.221114.001)",
    "Connection": "Keep-Alive",
}


def sanitize_filename(name):
    """Converts a channel name into a safe, clean filename."""
    name = name.lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9__\-]", "", name) + ".m3u8"


def download_m3u8(url, filepath):
    """Downloads the m3u8 content and writes it locally."""
    try:
        # Dynamically set the Host header based on the target URL
        parsed_url = urlparse(url)
        headers = HEADERS.copy()
        headers["Host"] = parsed_url.netloc

        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(True, f"Successfully downloaded: {filepath}")
            return True
        else:
            print(
                False,
                f"Failed to download {url}. Status code: {response.status_code}",
            )
            return False
    except Exception as e:
        print(False, f"Error processing {url}: {e}")
        return False


def main():
    # 1. Load the original channels
    if not os.path.exists(INPUT_JSON):
        print(f"Error: {INPUT_JSON} not found in the current directory.")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        channels = json.load(f)

    updated_channels = []

    # 2. Iterate and download streams
    for channel in channels:
        name = channel.get("name")
        logo = channel.get("logo")
        stream_url = channel.get("streamUrl")

        print(f"Processing: {name}...")

        filename = sanitize_filename(name)
        local_filepath = os.path.join(OUTPUT_DIR, filename)

        # Download the file
        success = download_m3u8(stream_url, local_filepath)

        if success:
            # Format the stream path for your future GitHub repository structure
            # Example: ./m3u8/brazil_vs_morocco.m3u8
            github_stream_path = f"./{OUTPUT_DIR}/{filename}"
        else:
            # Fallback to original URL if the download fails
            github_stream_path = stream_url

        # Build the new channel object
        updated_channels.append(
            {"name": name, "logo": logo, "streamUrl": github_stream_path}
        )

    # 3. Save the new tv.json file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(updated_channels, f, indent=2, ensure_ascii=False)

    print(f"\nTask Complete! New configuration saved to '{OUTPUT_JSON}'")


if __name__ == "__main__":
    main()
    