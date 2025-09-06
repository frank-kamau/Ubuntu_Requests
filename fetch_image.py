#!/usr/bin/env python3
"""
fetch_image.py

Downloads an image from a provided URL and saves it inside a local
'Fetched_Images' directory.

Features:
- Prompts the user for an image URL.
- Creates Fetched_Images/ if it doesn't exist.
- Downloads using requests with streaming.
- Checks HTTP errors and common network errors.
- Extracts filename from URL or generates one based on Content-Type.
- Avoids overwriting by adding suffixes if necessary.
- Implements graceful error handling and user-friendly messages.

Ubuntu Principles implemented:
- Community: connects to web resources (fetches images).
- Respect: handles errors gracefully; won't crash on common issues.
- Sharing: stores images in a single folder ready to share.
- Practicality: a simple useful tool for fetching resources.

Requirements:
- Python 3.6+
- requests
"""
import os
import re
import uuid
import mimetypes
import urllib.parse
import requests
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError

FETCH_DIR = "Fetched_Images"
CHUNK_SIZE = 8192  # bytes


def sanitize_filename(name: str) -> str:
    """Return a safe filename by replacing unsafe characters."""
    # Keep letters, numbers, dot, underscore and hyphen.
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return safe.strip("._-") or "file"


def filename_from_url(url: str) -> str or None: # type: ignore
    """Extract filename from URL path, if present."""
    parsed = urllib.parse.urlparse(url)
    base = os.path.basename(parsed.path)
    if base:
        return sanitize_filename(base)
    return None


def extension_from_content_type(content_type: str) -> str:
    """
    Guess an extension from Content-Type header (e.g., 'image/jpeg' -> '.jpg').
    Returns empty string if unknown.
    """
    if not content_type:
        return ""
    # Split off charset if present
    main_type = content_type.split(";")[0].strip().lower()
    ext = mimetypes.guess_extension(main_type)
    if ext:
        return ext
    # fallback: if it starts with 'image/', use last part
    if main_type.startswith("image/"):
        return "." + main_type.split("/", 1)[1]
    return ""


def unique_filepath(directory: str, filename: str) -> str:
    """
    If filename exists in directory, append _1, _2, ... before extension.
    Returns full path.
    """
    base, ext = os.path.splitext(filename)
    candidate = filename
    i = 1
    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{base}_{i}{ext}"
        i += 1
    return os.path.join(directory, candidate)


def generate_filename(ext: str = "") -> str:
    """Generate a random filename using uuid and optional extension."""
    name = f"image_{uuid.uuid4().hex}"
    if ext and not ext.startswith("."):
        ext = "." + ext
    return name + (ext or "")


def download_image(url: str, output_path: str, timeout: int = 10) -> None:
    """
    Download the given URL and save to output_path in binary chunks.
    Raises exceptions on errors (HTTPError, RequestException, OSError).
    """
    with requests.get(url, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()  # raise HTTPError for bad HTTP status
        # Optionally check content-type to ensure it's an image
        content_type = resp.headers.get("Content-Type", "")
        if not content_type.lower().startswith("image/"):
            # Not necessarily fatal; warn the user but allow saving if they confirm.
            print(f"Warning: Retrieved content-type is '{content_type}' (not an image).")

        # Write in binary mode
        with open(output_path, "wb") as out_file:
            for chunk in resp.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive chunks
                    out_file.write(chunk)


def main():
    print("=== Fetch Image Tool (Ubuntu_Requests) ===\n")
    try:
        url = input("Enter the image URL (or press Enter to quit): ").strip()
        if not url:
            print("No URL provided. Exiting.")
            return

        # Create directory (exists_ok True)
        os.makedirs(FETCH_DIR, exist_ok=True)

        # Try to derive a filename from the URL
        filename = filename_from_url(url)
        chosen_ext = ""

        # Make a HEAD request first to inspect headers (not supported by all servers)
        try:
            head = requests.head(url, allow_redirects=True, timeout=8)
            head.raise_for_status()
            content_type = head.headers.get("Content-Type", "")
            chosen_ext = extension_from_content_type(content_type)
        except (RequestException, Exception):
            # It's fine if HEAD fails; we'll handle when doing GET
            chosen_ext = ""

        # If URL path gave a filename, ensure it has extension; else attempt to add extension
        if filename:
            # If filename has no extension, attempt to add one from content-type
            if "." not in filename and chosen_ext:
                filename = filename + chosen_ext
        else:
            # No filename in URL; generate one using content type if known
            filename = generate_filename(chosen_ext)

        # Sanitize and ensure uniqueness
        filename = sanitize_filename(filename)
        output_path = unique_filepath(FETCH_DIR, filename)

        # Confirm before download
        print(f"\nSaving to: {output_path}")
        confirm = input("Proceed to download? (Y/n): ").strip().lower()
        if confirm == "n":
            print("Cancelled by user.")
            return

        # Download
        try:
            download_image(url, output_path)
            print(f"\nDownloaded successfully: {output_path}")
        except HTTPError as he:
            print(f"HTTP error occurred while fetching the image: {he}")
        except Timeout:
            print("Error: The request timed out. Please try again or check your connection.")
        except ConnectionError:
            print("Error: A connection error occurred. Check your internet connection and the URL.")
        except RequestException as rexc:
            print(f"Network error: {rexc}")
        except OSError as os_err:
            print(f"File error while saving: {os_err}")
        except Exception as exc:
            print(f"An unexpected error occurred: {exc}")

    except KeyboardInterrupt:
        print("\nOperation interrupted by user. Goodbye.")


if __name__ == "__main__":
    main()
