"""
Unit tests for the WorldBankDataDownloader class.
"""
import os
import sys
import pytest

from unittest.mock import patch, MagicMock, call
from concurrent.futures import Future

from src.world_bank.data_downloader import WorldBankDataDownloader

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def downloader():
    """
    Fixture to create an instance of the WorldBankDataDownloader class.
    :return: An instance of the WorldBankDataDownloader class.
    :rtype: WorldBankDataDownloader
    """
    return WorldBankDataDownloader()


@pytest.fixture
def mock_response():
    """
    Fixture to create a mock response object.
    :return: A mock response object.
    :rtype: MagicMock
    """
    mock = MagicMock()
    mock.json.return_value = [
        {"page": 1, "pages": 1, "per_page": 50, "total": 2},
        [
            {"id": "USA", "name": "United States"},
            {"id": "GBR", "name": "United Kingdom"}
        ]
    ]
    return mock


def test_init(downloader):
    """
    Test the __init__ method of the WorldBankDataDownloader class.
    :param downloader: An instance of the WorldBankDataDownloader class.
    :return: None
    :rtype: None
    """
    assert downloader.base_url == 'http://api.worldbank.org/v2'
    assert isinstance(downloader.country_codes, list)
    assert isinstance(downloader.indicator_codes, list)


@patch('src.world_bank.data_downloader.requests.get')
def test_get_country_codes(mock_get, downloader, mock_response):
    """
    Test the get_country_codes method of the WorldBankDataDownloader class.
    :param mock_get: A mock of the requests.get function.
    :param downloader: An instance of the WorldBankDataDownloader class.
    :param mock_response: A mock response object.
    :return: None
    :rtype: None
    """
    mock_get.return_value = mock_response
    country_codes = downloader.get_country_codes()
    assert country_codes == ['USA', 'GBR']
    mock_get.assert_called_once_with(
        'http://api.worldbank.org/v2/country?format=json&per_page=300',
        timeout=30
    )


@patch('src.world_bank.data_downloader.requests.get')
def test_get_indicators(mock_get, downloader, mock_response):
    """
    Test the get_indicators method of the WorldBankDataDownloader class.
    :param mock_get: A mock of the requests.get function.
    :param downloader: An instance of the WorldBankDataDownloader class.
    :param mock_response: A mock response object.
    :return: None
    :rtype: None
    """
    mock_response.json.return_value = [
        {"page": 1, "pages": 1, "per_page": 50, "total": 2},
        [
            {"id": "SP.POP.TOTL", "name": "Population, total"},
            {"id": "NY.GDP.MKTP.CD", "name": "GDP (current US$)"}
        ]
    ]
    mock_get.return_value = mock_response
    indicators = downloader.get_indicators()
    assert indicators == ['SP.POP.TOTL', 'NY.GDP.MKTP.CD']
    mock_get.assert_called_once_with(
        'http://api.worldbank.org/v2/indicator?format=json&per_page=1000',
        timeout=30
    )


@patch('src.world_bank.data_downloader.requests.get')
def test_fetch_data(mock_get, downloader):
    """
    Test the fetch_data method of the WorldBankDataDownloader class.
    :param mock_get: A mock of the requests.get function.
    :param downloader: An instance of the WorldBankDataDownloader class.
    :return: None
    :rtype: None
    """
    mock_responses = [
        MagicMock(json=lambda: [
            {"page": 1, "pages": 2, "per_page": 1, "total": 2},
            [{"year": "2020", "value": "100"}]
        ]),
        MagicMock(json=lambda: [
            {"page": 2, "pages": 2, "per_page": 1, "total": 2},
            [{"year": "2019", "value": "90"}]
        ])
    ]
    mock_get.side_effect = mock_responses

    data = downloader.fetch_data('USA', 'SP.POP.TOTL')
    assert data == [
        {"year": "2020", "value": "100"},
        {"year": "2019", "value": "90"}
    ]
    assert mock_get.call_count == 2


@patch('src.world_bank.data_downloader.ThreadPoolExecutor')
def test_fetch_data_concurrently(mock_executor, downloader):
    """
    Test the fetch_data_concurrently method of the WorldBankDataDownloader class.
    :param mock_executor: A mock of the ThreadPoolExecutor class.
    :param downloader: An instance of the WorldBankDataDownloader class.
    :return: None
    :rtype: None
    """
    # Set up mock data
    mock_data_1 = [{"year": "2020", "value": "100"}]
    mock_data_2 = [{"year": "2020", "value": "200"}]

    # Set up mock futures
    mock_future_1 = Future()
    mock_future_1.set_result(mock_data_1)
    mock_future_2 = Future()
    mock_future_2.set_result(mock_data_2)

    # Set up mock executor
    mock_executor_instance = MagicMock()
    mock_executor_instance.submit.side_effect = [mock_future_1, mock_future_2]
    mock_executor.return_value.__enter__.return_value = mock_executor_instance

    # Call the method
    result = downloader.fetch_data_concurrently('USA', ['SP.POP.TOTL', 'NY.GDP.MKTP.CD'])

    # Print the result for debugging
    print(f"Result: {result}")

    # Assert the results
    assert result == {
        'SP.POP.TOTL': mock_data_1,
        'NY.GDP.MKTP.CD': mock_data_2
    }

    # Assert that executor.submit was called with correct arguments
    calls = [
        call(downloader.fetch_data, 'USA', 'SP.POP.TOTL'),
        call(downloader.fetch_data, 'USA', 'NY.GDP.MKTP.CD')
    ]
    assert mock_executor_instance.submit.call_count == 2
    mock_executor_instance.submit.assert_has_calls(calls, any_order=True)

    # Assert that ThreadPoolExecutor was used
    mock_executor.assert_called_once()


def test_save_and_load_data(downloader, tmp_path):
    """
    Test the save_data_to_file and load_data_from_file methods of the WorldBankDataDownloader class.
    :param downloader: An instance of the WorldBankDataDownloader class.
    :param tmp_path: A temporary directory path.
    :return: None
    :rtype: None
    """
    test_data = {
        'USA': {
            'SP.POP.TOTL': [{"year": "2020", "value": "100"}]
        },
        'GBR': {
            'NY.GDP.MKTP.CD': [{"year": "2020", "value": "1000"}]
        }
    }
    filename = tmp_path / "test_data.json"

    downloader.save_data_to_file(test_data, filename)
    loaded_data = downloader.load_data_from_file(filename)

    assert loaded_data == test_data, f"Loaded data {loaded_data} does not match test data {test_data}"

    # Additional test to ensure the structure is correct
    assert isinstance(loaded_data, dict), "Loaded data should be a dictionary"
    assert all(isinstance(country_data, dict) for country_data in loaded_data.values()), "Each country's data should be a dictionary"
    assert all(isinstance(indicator_data, list) for country_data in loaded_data.values() for indicator_data in country_data.values()), "Each indicator's data should be a list"


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
