# nePyc

**nePyc** is a Python-based application designed to handle image data streaming, processing, and display. It includes
both a server for receiving images from clients and a GUI for presenting those images in a slideshow.

## Features

- **Server Component**:
    - Listens for incoming image data from clients over a network.
    - Validates and processes received image data.
    - Stores images for use in a random slideshow.

- **GUI Component**:
    - Displays a random slideshow of received images.
    - Resizes images dynamically to fit within specified dimensions.
    - Supports maintaining aspect ratios for a clean visual presentation.

- **Client Component**:
    - Sends images to the server with size metadata for reliable transmission.

## Project Structure

```
nePyc/
├── client/
│   └── ...  # Client-side functionality
├── common/
│   └── ...  # Common utilities and helpers
├── log_engine/
│   └── ...  # Custom logging infrastructure
├── server/
│   ├── __init__.py
│   ├── config.py    # Configuration for server settings
│   ├── gui.py       # GUI implementation for slideshow
│   └── server.py    # Main server logic
└── __init__.py
```

## Requirements

- Python 3.7+
- Dependencies listed in `pyproject.toml`.

### Key Libraries Used

- `socket`: For server-client communication.
- `Pillow`: For image processing and resizing.
- `tkinter`: For GUI creation and slideshow display.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd nePyc
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Run the server:
   ```bash
   poetry run python -m nepyc.server.server
   ```

4. (Optional) Run the client:
   ```bash
   poetry run python -m nepyc.client.client --image-path <path-to-image>
   ```

## Usage

### Server

The server listens for incoming connections and receives image data. It validates the images and stores them for use in
the slideshow.

### GUI

The slideshow GUI displays the images received by the server. Images are resized to fit within the window while
maintaining their aspect ratios.

### Client

The client sends images to the server. It prefixes each image with metadata about its size to ensure reliable
transmission.

## Configuration

Server configurations, such as host and port, are managed in `config.py`. Modify this file to update server settings.

## Example Workflow

1. Start the server:
   ```bash
   poetry run python -m nepyc.server.server
   ```

2. Use the client to send images:
   ```bash
   poetry run python -m nepyc.client.client --image-path <path-to-image>
   ```

3. Watch the GUI slideshow as images are processed and displayed.

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
