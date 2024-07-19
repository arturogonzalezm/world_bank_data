"""
This is the main file to run the WorldBankDataDownloader.
"""
from src.world_bank_data_downloader import WorldBankDataDownloader


def main():
    """
    Main function to download all data from the World Bank API.
    :return: None
    :rtype: None
    """
    downloader = WorldBankDataDownloader()
    all_data = downloader.download_all_data()
    downloader.save_data_to_file(all_data)


if __name__ == "__main__":
    main()
