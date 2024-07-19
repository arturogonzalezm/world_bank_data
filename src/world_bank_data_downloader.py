"""
This module contains the WorldBankDataDownloader class which is used to download data from the World Bank API.
"""

import os
import time
import json
import requests


class WorldBankDataDownloader:
    def __init__(self):
        """
        Initialize the WorldBankDataDownloader with the base URL, country codes, and indicator codes.
        :return: None
        :rtype: None
        """
        self.base_url = 'http://api.worldbank.org/v2'
        self.country_codes = self.get_country_codes()
        self.indicator_codes = self.get_indicators()

    def get_country_codes(self):
        """
        Get the list of all country codes.
        :return: List of country codes.
        :rtype: list
        """
        url = f'{self.base_url}/country?format=json&per_page=300'
        response = requests.get(url)
        if response.status_code == 200:
            countries = response.json()[1]
            country_codes = [country['id'] for country in countries]
            return country_codes
        else:
            print("Failed to fetch country codes")
            return []

    def get_indicators(self):
        """
        Get the list of all indicators.
        :return: List of indicator codes.
        :rtype: list
        """
        url = f'{self.base_url}/indicator?format=json&per_page=1000'
        response = requests.get(url)
        if response.status_code == 200:
            indicators = response.json()[1]
            indicator_codes = [indicator['id'] for indicator in indicators]
            return indicator_codes
        else:
            print("Failed to fetch indicators")
            return []

    def fetch_data(self, country_code, indicator_code):
        """
        Fetch data for a given country code and indicator.
        :param country_code: The country code.
        :param indicator_code: The indicator code.
        :type country_code: str
        """
        page = 1
        all_pages_data = []
        while True:
            url = f'{self.base_url}/country/{country_code}/indicator/{indicator_code}?format=json&per_page=1000&page={page}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if len(data) < 2 or not data[1]:  # Check if data is not empty and has the expected structure
                    break
                all_pages_data.extend(data[1])
                if data[0]['page'] >= data[0]['pages']:
                    break
                page += 1
                time.sleep(1)  # Be polite with the API
            else:
                print(f"Failed to fetch data for country {country_code} and indicator {indicator_code} on page {page}")
                break
        return all_pages_data

    def download_all_data(self):
        """
        Download data for all indicators and country codes.
        :return: A dictionary containing the data for all country codes and indicator codes.
        :rtype: dict
        """
        all_data = {}

        for country_code in self.country_codes:
            for indicator_code in self.indicator_codes:
                print(f"Fetching data for country {country_code} and indicator {indicator_code}")
                data = self.fetch_data(country_code, indicator_code)
                if data:
                    all_data[(country_code, indicator_code)] = data

        return all_data

    @staticmethod
    def save_data_to_file(data, filename='data/raw/world_bank_data.json'):
        """
        Save the data to a JSON file.
        :param data: The data to save.
        :param filename: The filename to save the data to.
        :return: None
        :rtype: None
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Convert the dictionary keys to strings
        serializable_data = {str(key): value for key, value in data.items()}

        with open(filename, 'w') as f:
            json.dump(serializable_data, f)
        print(f"Data saved to {filename}")

    @staticmethod
    def load_data_from_file(filename='../data/raw/world_bank_data.json'):
        """
        Load the data from a JSON file.
        :param filename: The filename to load the data from.
        :return: The loaded data.
        :rtype: dict
        """
        with open(filename, 'r') as f:
            data = json.load(f)

        # Convert the keys back to tuples
        deserialized_data = {eval(key): value for key, value in data.items()}
        return deserialized_data
