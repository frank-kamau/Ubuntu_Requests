# Ubuntu_Requests

A small tool that downloads an image from a provided URL and saves it to a directory named `Fetched_Images`. Built with practicality and robustness in mind.

## Features
- Prompts for a URL containing an image.
- Creates `Fetched_Images/` directory if it doesn't exist.
- Fetches the image using the `requests` library and saves it in binary mode.
- Derives a filename from the URL or generates a unique one (based on content-type).
- Avoids overwriting existing files by creating unique filenames.
- Handles common network and file errors gracefully.
- Aligns with Ubuntu principles: Community, Respect, Sharing, Practicality.

## Requirements
- Python 3.6+
- `requests` library

## Setup
1. Clone the repository (replace `<your-repo-url>` with the GitHub repo you create):
   ```bash
   git clone <your-repo-url>
   cd Ubuntu_Requests
