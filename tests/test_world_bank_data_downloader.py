"""
Unit tests for the WorldBankDataDownloader class.
"""
import pytest
import json
import requests
from unittest.mock import patch, MagicMock

from src.world_bank_data_downloader import WorldBankDataDownloader


@pytest.fixture
def downloader():
    """
    Fixture to create a WorldBankDataDownloader instance.
    :return: A WorldBankDataDownloader instance.
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
    mock.raise_for_status.return_value = None
    return mock


def test_init(downloader):
    """
    Test the initialization of the WorldBankDataDownloader class.
    :param downloader: A WorldBankDataDownloader instance.
    :return: None
    :rtype: None
    """
    assert downloader.base_url == 'http://api.worldbank.org/v2'
    assert isinstance(downloader.country_codes, list)
    assert isinstance(downloader.indicator_codes, list)


@patch('requests.get')
def test_get_country_codes(mock_get, downloader, mock_response):
    """
    Test the get_country_codes method.
    :param mock_get: A mock of the requests.get function.
    :param downloader: A WorldBankDataDownloader instance.
    :param mock_response: A mock response object.
    :return: None
    :rtype: None
    """
    mock_get.return_value = mock_response
    country_codes = downloader.get_country_codes()
    assert country_codes == ['USA', 'GBR']
    mock_get.assert_called_once_with(f'{downloader.base_url}/country?format=json&per_page=300', timeout=30)


@patch('requests.get')
def test_get_indicators(mock_get, downloader, mock_response):
    """
    Test the get_indicators method.
    :param mock_get: A mock of the requests.get function.
    :param downloader: A WorldBankDataDownloader instance.
    :param mock_response: A mock response object.
    :return: None
    :rtype: None
    """
    mock_get.return_value = mock_response
    indicators = downloader.get_indicators()
    assert indicators == ['USA', 'GBR']  # Using the same mock response for simplicity
    mock_get.assert_called_once_with(f'{downloader.base_url}/indicator?format=json&per_page=1000', timeout=30)


@patch('requests.get')
def test_fetch_data(mock_get, downloader, mock_response):
    """
    Test the fetch_data method.
    :param mock_get: A mock of the requests.get function.
    :param downloader: A WorldBankDataDownloader instance.
    :param mock_response: A mock response object.
    :return: None
    :rtype: None
    """
    mock_get.return_value = mock_response
    data = downloader.fetch_data('USA', 'GDP')
    assert data == [{"id": "USA", "name": "United States"}, {"id": "GBR", "name": "United Kingdom"}]
    mock_get.assert_called_once_with(
        f'{downloader.base_url}/country/USA/indicator/GDP?format=json&per_page=1000&page=1',
        timeout=30
    )


@patch.object(WorldBankDataDownloader, 'fetch_data')
def test_download_all_data(mock_fetch_data, downloader):
    """
    Test the download_all_data method.
    :param mock_fetch_data: A mock of the fetch_data method.
    :param downloader: A WorldBankDataDownloader instance.
    :return: None
    :rtype: None
    """
    mock_fetch_data.return_value = [{"year": 2020, "value": 100}]
    downloader.country_codes = ['USA', 'GBR']
    downloader.indicator_codes = ['GDP', 'POP']

    all_data = downloader.download_all_data()

    assert len(all_data) == 4  # 2 countries * 2 indicators
    assert all_data[('USA', 'GDP')] == [{"year": 2020, "value": 100}]
    assert mock_fetch_data.call_count == 4


def test_save_data_to_file(tmp_path, downloader):
    """
    Test the save_data_to_file method.
    :param tmp_path: A temporary directory.
    :param downloader: A WorldBankDataDownloader instance.
    :return: None
    :rtype: None
    """
    data = {('USA', 'GDP'): [{"year": 2020, "value": 100}]}
    filename = tmp_path / "test_data.json"

    downloader.save_data_to_file(data, filename)

    assert filename.exists()
    with open(filename, 'r') as f:
        saved_data = json.load(f)
    assert saved_data == {"('USA', 'GDP')": [{"year": 2020, "value": 100}]}


def test_load_data_from_file(tmp_path, downloader):
    """
    Test the load_data_from_file method.
    :param tmp_path: A temporary directory.
    :param downloader: A WorldBankDataDownloader instance.
    :return: None
    :rtype: None
    """
    data = {"('USA', 'GDP')": [{"year": 2020, "value": 100}]}
    filename = tmp_path / "test_data.json"
    with open(filename, 'w') as f:
        json.dump(data, f)

    loaded_data = downloader.load_data_from_file(filename)

    assert loaded_data == {('USA', 'GDP'): [{"year": 2020, "value": 100}]}


@patch('requests.get')
def test_get_country_codes_error(mock_get, downloader):
    """
    Test the get_country_codes method when an error occurs.
    :param mock_get: A mock of the requests.get function.
    :param downloader: A WorldBankDataDownloader instance.
    :return: None
    :rtype: None
    """
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    country_codes = downloader.get_country_codes()
    assert country_codes == []


@patch('requests.get')
def test_get_indicators_error(mock_get, downloader):
    """
    Test the get_indicators method when an error occurs.
    :param mock_get: A mock of the requests.get function.
    :param downloader: A WorldBankDataDownloader instance.
    :return: None
    :rtype: None
    """
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    indicators = downloader.get_indicators()
    assert indicators == []


@patch('requests.get')
def test_fetch_data_error(mock_get, downloader):
    """
    Test the fetch_data method when an error occurs.
    :param mock_get: A mock of the requests.get function.
    :param downloader: A WorldBankDataDownloader instance.
    :return: None
    :rtype: None
    """
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    data = downloader.fetch_data('USA', 'GDP')
    assert data == []


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
