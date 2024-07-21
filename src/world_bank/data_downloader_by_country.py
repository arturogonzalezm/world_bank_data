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
    downloader.save_data_to_file({country_code: australia_data}, filename=filename)

    # Load the data from the file (for verification)
    loaded_data = downloader.load_data_from_file(filename=filename)

    # Print the loaded data (or a subset of it)
    for country, indicators in loaded_data.items():
        logger.info(f"Country: {country}")
        for indicator, data in indicators.items():
            logger.info(f"  Indicator: {indicator}")
            for entry in data[:3]:  # Print only the first 3 entries for brevity
                logger.info(f"    {entry}")
            logger.info("\n")


if __name__ == '__main__':
    extract()
