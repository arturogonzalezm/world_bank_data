"""
This file contains the unit tests for the extract function in the data_downloader_by_country.py file.
"""
import pytest

from unittest.mock import patch, MagicMock

from src.world_bank.data_downloader_by_country import extract  # Update this import to match your actual file structure


@pytest.fixture
def mock_singleton_logger():
    """
    Fixture to mock the SingletonLogger class.
    :return:
    """
    with patch('src.world_bank.data_downloader_by_country.SingletonLogger') as mock_logger:
        mock_logger_instance = MagicMock()
        mock_logger.return_value.get_logger.return_value = mock_logger_instance
        yield mock_logger_instance


@pytest.fixture
def mock_world_bank_downloader():
    """
    Fixture to mock the WorldBankDataDownloader class.
    :return:
    """
    with patch('src.world_bank.data_downloader_by_country.WorldBankDataDownloader') as mock_downloader:
        mock_downloader_instance = MagicMock()
        mock_downloader.return_value = mock_downloader_instance
        yield mock_downloader_instance


def test_extract_function(mock_singleton_logger, mock_world_bank_downloader):
    """
    Test the extract function.
    :param mock_singleton_logger:
    :param mock_world_bank_downloader:
    :return:
    """
    # Arrange
    mock_indicators = ['indicator1', 'indicator2']
    mock_australia_data = {
        'indicator1': [{'year': 2020, 'value': 100}],
        'indicator2': [{'year': 2020, 'value': 200}]
    }
    mock_world_bank_downloader.get_indicators.return_value = mock_indicators
    mock_world_bank_downloader.fetch_data_concurrently.return_value = mock_australia_data
    mock_world_bank_downloader.load_data_from_file.return_value = mock_australia_data

    # Act
    extract()

    # Assert
    mock_world_bank_downloader.get_indicators.assert_called_once()
    mock_world_bank_downloader.fetch_data_concurrently.assert_called_once_with('AUS', mock_indicators)
    mock_world_bank_downloader.save_data_to_file.assert_called_once()
    mock_world_bank_downloader.load_data_from_file.assert_called_once()

    # Check if logger.info was called for each indicator and its data
    for indicator, data in mock_australia_data.items():
        mock_singleton_logger.info.assert_any_call(f"Indicator: {indicator}")
        for entry in data:
            mock_singleton_logger.info.assert_any_call(entry)
        mock_singleton_logger.info.assert_any_call("\n")


@pytest.mark.parametrize("exception_type", [Exception, ValueError, KeyError])
def test_extract_function_exception_handling(mock_singleton_logger, mock_world_bank_downloader, exception_type):
    """
    Test the extract function with different exception types.
    :param mock_singleton_logger:
    :param mock_world_bank_downloader:
    :param exception_type:
    :return:
    """
    # Arrange
    mock_world_bank_downloader.get_indicators.side_effect = exception_type("Test exception")

    # Act & Assert
    with pytest.raises(exception_type):
        extract()


def test_extract_function_empty_data(mock_singleton_logger, mock_world_bank_downloader):
    """
    Test the extract function when no data is returned.
    :param mock_singleton_logger:
    :param mock_world_bank_downloader:
    :return:
    """
    # Arrange
    mock_world_bank_downloader.get_indicators.return_value = []
    mock_world_bank_downloader.fetch_data_concurrently.return_value = {}
    mock_world_bank_downloader.load_data_from_file.return_value = {}

    # Act
    extract()

    # Assert
    mock_world_bank_downloader.save_data_to_file.assert_called_once_with({},
                                                                         filename='../data/raw/AUS_world_bank_data.json')
    assert not mock_singleton_logger.info.called


if __name__ == "__main__":
    pytest.main()
