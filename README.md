# Blockchain Log Scanner

This project is a FastAPI-based application that scans blockchain logs, processes the data, and provides statistics through an API.

## Features

- Scans blockchain logs from a specified start block to the latest block
- Processes log data to extract transaction hashes, node addresses, and amounts
- Provides API endpoints for statistics and rescanning
- Saves progress and results to a local file for persistence

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/blockchain-log-scanner.git
   cd blockchain-log-scanner
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```
   python run.py
   ```
   This will start the FastAPI server on `http://localhost:8000`.

2. The application will automatically start scanning blockchain logs upon startup.

3. Access the API:
   - View API documentation: `http://localhost:8000/docs`
   - Get statistics: `GET http://localhost:8000/statistics`
   - Trigger a rescan: `GET http://localhost:8000/rescan`

## API Endpoints

- `/statistics`: Returns the current statistics of scanned logs.
- `/rescan`: Triggers a new scan from the latest block.

## Configuration

You can modify the following parameters in `app/scanner.py`:
- `block_interval`: Number of blocks to scan in each iteration (default: 1000)
- `results_file`: Name of the file to store scan results (default: "scan_results.json")

## Notes

- The first scan may take some time as it starts from 10000 blocks before the latest block.
- Scan results are saved to a local file (`scan_results.json` by default) and loaded on subsequent runs.
- Ensure the application has write permissions in the directory it's running from.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.