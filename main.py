"""
This is the main file to run the WorldBankDataDownloader.
"""
from src.utils.singleton_logger import SingletonLogger
from src.world_bank.data_downloader import WorldBankDataDownloader


def main():
    """
    Main function to download data from the World Bank API.
    :return: None
    :rtype: None
    """
    # Set up logging
    logger = SingletonLogger().get_logger()

    # Initialize the downloader
    downloader = WorldBankDataDownloader()

    # Get all country codes and indicator codes
    country_codes = downloader.country_codes
    indicator_codes = downloader.indicator_codes

    # Download data for all countries and indicators
    all_data = {}
    for country_code in country_codes:
        logger.info(f"Downloading data for country: {country_code}")
        country_data = downloader.fetch_data_concurrently(country_code, indicator_codes)
        all_data[country_code] = country_data

    # Save the data to a file
    downloader.save_data_to_file(all_data)

    logger.info("Data download and save completed.")


if __name__ == "__main__":
    main()
