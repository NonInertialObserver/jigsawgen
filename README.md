# JigsawGen

JigsawGen is a small local web app for generating and playing draggable jigsaw puzzles from your own images.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Repository: <https://github.com/NonInertialObserver/jigsawgen>

## Features

- Upload an image and generate jigsaw puzzle pieces locally.
- Choose puzzle rows and columns from 2 to 10.
- Adjust the jigsaw tab size.
- Drag pieces on the browser-based play area.
- Pieces snap into place when they are close to the correct position.
- Automatically opens the game page when the program starts.
- Provides a **Close Software** button in the page to stop the local Flask server.

## Requirements

- Python 3.10 or newer is recommended.
- Dependencies listed in `requirements.txt`:
  - Flask
  - Pillow

## Installation

Clone the repository:

```bash
git clone https://github.com/NonInertialObserver/jigsawgen.git
cd jigsawgen
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the app:

```bash
python main.pyw
```

The browser should open automatically at:

```text
http://127.0.0.1:5000/
```

Then:

1. Choose an image.
2. Set rows, columns, and tab size.
3. Click **生成并开始**.
4. Drag pieces into the board area.
5. Click **关闭软件** when you want to stop the local server.

> Note: browsers may prevent a web page from closing its own tab automatically. When closing the software, the page will show a message telling you that it is safe to close the page manually. If the browser allows it, the page will also try to close itself.

## Supported image formats

- PNG
- JPG / JPEG
- WEBP
- BMP

The maximum upload size is currently 16 MB.

## Project structure

```text
jigsawgen/
├── index.html        # Browser UI and puzzle interaction logic
├── main.pyw          # Flask app entry point
├── split.py          # Puzzle piece splitting and edge generation logic
├── requirements.txt  # Python dependencies
├── asserts/          # Application assets
└── LICENSE
```

## Packaging notes

The repository contains `main.spec`, which can be used as a starting point for packaging the app with PyInstaller.

Generated puzzle images and uploads are stored under `temp/` during runtime.

## Icon attribution

The application icon is from [Material Icons](https://fonts.google.com/icons).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
