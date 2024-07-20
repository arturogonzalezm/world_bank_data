"""
This script downloads data from the World Bank API for a specific country (Australia in this case) and saves it to a file.
"""
from src.utils.singleton_logger import SingletonLogger
from src.world_bank.data_downloader import WorldBankDataDownloader


def extract():
    """
    Main function to download data from the World Bank API.
    :return: None
    :rtype: None
    """
    logger = SingletonLogger().get_logger()
    country_code = 'AUS'

    # Create an instance of the WorldBankDataDownloader
    downloader = WorldBankDataDownloader()

    # Get the list of all indicators
    indicators = downloader.get_indicators()

    # Fetch data for Australia (AUS) for all indicators concurrently
    australia_data = downloader.fetch_data_concurrently(country_code, indicators)

    # Save the data to a file
    filename = f'../data/raw/{country_code}_world_bank_data.json'
    downloader.save_data_to_file(australia_data, filename=filename)

    # Load the data from the file (for verification)
    loaded_data = downloader.load_data_from_file(filename=filename)

    # Print the loaded data (or a subset of it)
    for indicator, data in loaded_data.items():
        logger.info(f"Indicator: {indicator}")
        for entry in data:
            logger.info(entry)
        logger.info("\n")


if __name__ == '__main__':
    extract()
