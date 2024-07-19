"""
This module contains a class for downloading data from the World Bank API.
"""

import os
import time
import json
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential


class WorldBankDataDownloader:
    """Class for downloading data from the World Bank API."""

    def __init__(self):
        """
        Initialize the WorldBankDataDownloader with the base URL, country codes, and indicator codes.
        """
        self.base_url = 'http://api.worldbank.org/v2'
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

    def download_all_data(self):
        """
        Download data for all indicators and country codes.
        :return: A dictionary containing the data for all country codes and indicator codes.
        """
        all_data = {}
        total_requests = len(self.country_codes) * len(self.indicator_codes)
        completed_requests = 0

        for country_code in self.country_codes:
            for indicator_code in self.indicator_codes:
                completed_requests += 1
                progress = (completed_requests / total_requests) * 100
                logging.info(
                    f"Progress: {progress:.2f}% - Fetching data for country {country_code} and indicator {indicator_code}")

                data = self.fetch_data(country_code, indicator_code)
                if data:
                    all_data[(country_code, indicator_code)] = data

                time.sleep(0.5)  # Add a 0.5-second delay between requests to avoid rate limiting

        return all_data

    @staticmethod
    def save_data_to_file(data, filename='../data/raw/world_bank_data.json'):
        """
        Save the data to a JSON file.
        :param data: The data to save.
        :param filename: The filename to save the data to.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        serializable_data = {str(key): value for key, value in data.items()}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)
        logging.info(f"Data saved to {filename}")

    @staticmethod
    def load_data_from_file(filename='../data/raw/world_bank_data.json'):
        """
        Load the data from a JSON file.
        :param filename: The filename to load the data from.
        :return: The loaded data.
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        deserialized_data = {eval(key): value for key, value in data.items()}
        return deserialized_data
