[![codecov](https://codecov.io/gh/arturogonzalezm/world_bank_data/graph/badge.svg?token=cW9uPbPSUD)](https://codecov.io/gh/arturogonzalezm/world_bank_data)
[![PyLint](https://github.com/arturogonzalezm/world_bank_data/actions/workflows/workflow.yml/badge.svg)](https://github.com/arturogonzalezm/world_bank_data/actions/workflows/workflow.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

# World Bank Data Downloader

This project provides a Python 3.12 class `WorldBankDataDownloader` for downloading data from the World Bank API. It includes functionality to fetch country codes, indicator codes, and data for specific country-indicator pairs.

## Setup

Follow these steps to set up your development environment:

1. **Clone the repository**
   ```
   git clone https://github.com/arturogonzalezm/world_bank_data.git
   cd world-bank-data-downloader
   ```

2. **Create a virtual environment**
   - For Unix or MacOS:
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - For Windows:
     ```
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. **Upgrade pip**
   ```
   pip install --upgrade pip
   ```

4. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt` file, you can create one with the following content:
   ```
    requests==2.32.3
    pytest==8.2.2
    coverage==7.6.0
    pytest-cov==5.0.0
    tenacity==8.5.0
   ```
   Then run the install command above.

## Class Structure

The `WorldBankDataDownloader` class is structured as follows:

```mermaid
classDiagram
    class WorldBankDataDownloader {
        +base_url : str
        +country_codes : list
        +indicator_codes : list
        +__init__()
        +get_country_codes() : list
        +get_indicators() : list
        +fetch_data(country_code: str, indicator_code: str) : list
        +download_all_data() : dict
        +save_data_to_file(data: dict, filename: str)
        +load_data_from_file(filename: str) : dict
    }
```

## Key Features

1. **Retry Mechanism**: Uses the `tenacity` library to implement retry logic for API requests.
2. **Pagination Handling**: Manages paginated responses from the World Bank API.
3. **Rate Limiting**: Implements delays between requests to avoid overwhelming the API.
4. **Error Handling**: Robust error handling for API requests and data processing.
5. **Data Persistence**: Methods to save and load data to/from JSON files.

## Sequence Diagram

The following sequence diagram illustrates the main interactions of the `WorldBankDataDownloader` class:

```mermaid
sequenceDiagram
    participant Client
    participant WBD as WorldBankDataDownloader
    participant API as World Bank API
    participant FileSystem

    Client->>WBD: create()
    WBD->>API: Fetch country codes
    WBD->>API: Fetch indicator codes
    Client->>WBD: download_all_data()
    loop for each country and indicator
        WBD->>API: Fetch data
    end
    Client->>WBD: save_data_to_file(data)
    WBD->>FileSystem: Write JSON
    Client->>WBD: load_data_from_file()
    FileSystem-->>WBD: Read JSON
    WBD-->>Client: Return data
```

## Flowchart

This flowchart outlines the main process of the `WorldBankDataDownloader`:

```mermaid
graph TD
    A[Start] --> B[Initialize WorldBankDataDownloader]
    B --> C[Fetch country codes]
    C --> D[Fetch indicator codes]
    D --> E[Download all data]
    E --> F{For each country and indicator}
    F --> G[Fetch data]
    G --> H{More pairs?}
    H -->|Yes| F
    H -->|No| I[Save data to file]
    I --> J[End]

    K[Load data from file] --> L[Read and deserialize JSON]
    L --> M[Return data]
```

## Usage

Here's a basic example of how to use the `WorldBankDataDownloader`:

```python
downloader = WorldBankDataDownloader()
all_data = downloader.download_all_data()
downloader.save_data_to_file(all_data, 'data/world_bank_data.json')
```

## Unit Tests

The project includes a comprehensive suite of unit tests using pytest. The test structure is as follows:

```mermaid
graph TD
    A[Setup Fixtures] --> B[Test Initialization]
    A --> C[Test API Methods]
    A --> D[Test Data Processing]
    A --> E[Test File I/O]
    A --> F[Test Error Handling]
    
    C --> C1[Test get_country_codes]
    C --> C2[Test get_indicators]
    C --> C3[Test fetch_data]
    
    D --> D1[Test download_all_data]
    
    E --> E1[Test save_data_to_file]
    E --> E2[Test load_data_from_file]
    
    F --> F1[Test API Error Scenarios]
```

### Test Coverage

The unit tests cover:

1. Class initialization
2. API interaction methods (with mocked responses)
3. Data processing logic
4. File I/O operations
5. Error handling scenarios

### Running the Tests

To run the tests:

1. Ensure you're in your virtual environment
2. Run the command: `pytest test_world_bank_data_downloader.py`

## Dependencies

- requests (for making HTTP requests)
- tenacity (for retry logic)
- pytest (for running tests)
- pytest-cov (for test coverage)
- coverage (for test coverage)

## Notes

- The World Bank API has rate limits. The class implements a basic delay between requests, but for large-scale data fetching, you may need to implement more sophisticated rate limiting.
- Always check the World Bank API documentation for the most up-to-date information on endpoints and usage guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
