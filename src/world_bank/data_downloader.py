"""
This module contains the WorldBankDataDownloader class, which is used to download data from the World Bank API.
"""
import os
import time
import json
import logging
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.singleton_logger import SingletonLogger


class WorldBankDataDownloader:
    """Class for downloading data from the World Bank API."""

    def __init__(self):
        """
        Initialize the WorldBankDataDownloader with the base URL, country codes, and indicator codes.
        """
        self.base_url = 'http://api.worldbank.org/v2'
        self.logger = SingletonLogger().get_logger()
        self.country_codes = self.get_country_codes()
        self.indicator_codes = self.get_indicators()
        logging.basicConfig(level=logging.INFO)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_country_codes(self):
        """
        Get the list of all country codes.
        :return: List of country codes.
        """
        url = f'{self.base_url}/country?format=json&per_page=300'
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            countries = response.json()[1]
            return [country['id'] for country in countries]
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching country codes: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_indicators(self):
        """
        Get the list of all indicators.
        :return: List of indicator codes.
        """
        url = f'{self.base_url}/indicator?format=json&per_page=1000'
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            indicators = response.json()[1]
            return [indicator['id'] for indicator in indicators]
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching indicators: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_data(self, country_code, indicator_code):
        """
        Fetch data for a given country code and indicator.
        :param country_code: The country code.
        :param indicator_code: The indicator code.
        :return: List of data for the given country code and indicator.
        """
        page = 1
        all_pages_data = []
        while True:
            url = (
                f'{self.base_url}/country/{country_code}/indicator/{indicator_code}'
                f'?format=json&per_page=1000&page={page}'
            )
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                if len(data) < 2 or not data[1]:
                    break
                all_pages_data.extend(data[1])
                if data[0]['page'] >= data[0]['pages']:
                    break
                page += 1
                time.sleep(1)  # Be polite with the API
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching data for country {country_code} and indicator {indicator_code}: {e}")
                break
        return all_pages_data

    def fetch_data_concurrently(self, country_code, indicator_codes, max_workers=10):
        """
        Fetch data concurrently for a given country code and a list of indicator codes.
        :param country_code: The country code.
        :param indicator_codes: The list of indicator codes.
        :param max_workers: The maximum number of threads to use.
        :return: A dictionary containing the data for the given country code and indicator codes.
        """
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_indicator = {executor.submit(self.fetch_data, country_code, indicator_code): indicator_code for
                                   indicator_code in indicator_codes}
            for future in as_completed(future_to_indicator):
                indicator_code = future_to_indicator[future]
                try:
                    data = future.result()
                    if data:
                        results[indicator_code] = data
                except Exception as e:
                    logging.error(f"Error fetching data for indicator {indicator_code}: {e}")
        return results

    @staticmethod
    def save_data_to_file(data, filename='../data/raw/world_bank_data_optimised.json'):
        """
        Save the data to a JSON file.
        :param data: The data to save.
        :param filename: The filename to save the data to.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # Use a delimiter that is safe and won't appear in the keys
        serializable_data = {"__DELIM__".join(key): value for key, value in data.items()}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)
        logging.info(f"Data saved to {filename}")

    @staticmethod
    def load_data_from_file(filename='../data/raw/world_bank_data_optimised.json'):
        """
        Load the data from a JSON file.
        :param filename: The filename to load the data from.
        :return: The loaded data.
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Use the same delimiter to split the keys back into tuples
        deserialized_data = {tuple(key.split("__DELIM__")): value for key, value in data.items()}
        return deserialized_data
