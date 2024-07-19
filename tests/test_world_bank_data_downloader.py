"""
This module contains unit tests for the WorldBankDataDownloader class.
"""

import pytest
import os
import json

from requests.models import Response
from unittest.mock import patch

from src.world_bank_data_downloader import WorldBankDataDownloader


@pytest.fixture
def downloader():
    return WorldBankDataDownloader()


def mocked_requests_get(url, timeout=None):
    """
    This function will serve as a mock for requests.get
    """
    response = Response()
    if 'country?format=json' in url:
        response.status_code = 200
        response._content = b'''
        [
            {"page":1,"pages":1,"per_page":"300","total":2},
            [
                {"id":"ABW","iso2Code":"AW","name":"Aruba","region":{"id":"LCN","iso2code":"LAC","value":"Latin America & Caribbean"},"adminregion":{"id":"","iso2code":"","value":""},"incomeLevel":{"id":"HIC","iso2code":"HIC","value":"High income"},"lendingType":{"id":"IBD","iso2code":"IBD","value":"IBRD"},"capitalCity":"Oranjestad","longitude":"-70.0167","latitude":"12.5167"},
                {"id":"USA","iso2Code":"US","name":"United States","region":{"id":"NAC","iso2code":"NAC","value":"North America"},"adminregion":{"id":"","iso2code":"","value":""},"incomeLevel":{"id":"HIC","iso2code":"HIC","value":"High income"},"lendingType":{"id":"IBD","iso2code":"IBD","value":"IBRD"},"capitalCity":"Washington D.C.","longitude":"-77.0369","latitude":"38.8951"}
            ]
        ]
        '''
    elif 'indicator?format=json' in url:
        response.status_code = 200
        response._content = b'''
        [
            {"page":1,"pages":1,"per_page":"1000","total":2},
            [
                {"id":"SP.POP.TOTL","name":"Population, total","unit":"","source":{"id":"2","value":"World Development Indicators"},"sourceNote":"Total population is based on the de facto definition of population, which counts all residents regardless of legal status or citizenship.","sourceOrganization":"(1) United Nations Population Division. World Population Prospects: 2019 Revision. (2) Census reports and other statistical publications from national statistical offices, (3) Eurostat: Demographic Statistics, (4) Secretariat of the Pacific Community: Statistics and Demography Programme, and (5) U.S. Census Bureau: International Database.","topics":[]},
                {"id":"NY.GDP.MKTP.CD","name":"GDP (current US$)","unit":"","source":{"id":"2","value":"World Development Indicators"},"sourceNote":"GDP at purchaser's prices is the sum of gross value added by all resident producers in the economy plus any product taxes and minus any subsidies not included in the value of the products. It is calculated without making deductions for depreciation of fabricated assets or for depletion and degradation of natural resources. Data are in current U.S. dollars.","sourceOrganization":"World Bank national accounts data, and OECD National Accounts data files.","topics":[]}
            ]
        ]
        '''
    else:
        response.status_code = 200
        response._content = b'''
        [
            {"page":1,"pages":1,"per_page":"1000","total":1},
            [
                {"indicator": {"id": "SP.POP.TOTL"}, "country": {"id": "ABW"}, "value": "106314", "decimal": "0", "date": "2021"},
                {"indicator": {"id": "NY.GDP.MKTP.CD"}, "country": {"id": "USA"}, "value": "21433224600000", "decimal": "0", "date": "2021"}
            ]
        ]
        '''
    return response


@patch('requests.get', side_effect=mocked_requests_get)
def test_get_country_codes(mock_get, downloader):
    """
    This function tests the get_country_codes method of WorldBankDataDownloader.
    """
    country_codes = downloader.get_country_codes()
    assert country_codes == ["ABW", "USA"]


@patch('requests.get', side_effect=mocked_requests_get)
def test_get_indicators(mock_get, downloader):
    """
    This function tests the get_indicators method of WorldBankDataDownloader.
    """
    indicator_codes = downloader.get_indicators()
    assert indicator_codes == ["SP.POP.TOTL", "NY.GDP.MKTP.CD"]


@patch('requests.get', side_effect=mocked_requests_get)
def test_fetch_data(mock_get, downloader):
    """
    This function tests the fetch_data method of WorldBankDataDownloader.
    """
    data = downloader.fetch_data("ABW", "SP.POP.TOTL")
    assert len(data) > 0
    assert data[0]['country']['id'] == "ABW"
    assert data[0]['indicator']['id'] == "SP.POP.TOTL"


@patch('requests.get', side_effect=mocked_requests_get)
def test_download_all_data(mock_get, downloader):
    """
    This function tests the download_all_data method of WorldBankDataDownloader.
    """
    all_data = downloader.download_all_data()
    assert len(all_data) > 0
    assert ("ABW", "SP.POP.TOTL") in all_data
    assert ("USA", "NY.GDP.MKTP.CD") in all_data


def test_save_data_to_file(downloader):
    """
    This function tests the save_data_to_file method of WorldBankDataDownloader.
    """
    data = {("AUS", "SP.POP.TOTL"): [
        {"country": {"id": "AUS"}, "indicator": {"id": "SP.POP.TOTL"}, "value": "106314", "decimal": "0",
         "date": "2021"}]}
    filename = 'data/raw/test_world_bank_data.json'
    downloader.save_data_to_file(data, filename)
    assert os.path.exists(filename)

    with open(filename, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    assert loaded_data == {"('AUS', 'SP.POP.TOTL')": [
        {"country": {"id": "AUS"}, "indicator": {"id": "SP.POP.TOTL"}, "value": "106314", "decimal": "0",
         "date": "2021"}]}

    # Clean up
    os.remove(filename)


def test_load_data_from_file(downloader):
    """
    This function tests the load_data_from_file method of WorldBankDataDownloader.
    """
    data = {("AUS", "SP.POP.TOTL"): [
        {"country": {"id": "AUS"}, "indicator": {"id": "SP.POP.TOTL"}, "value": "106314", "decimal": "0",
         "date": "2021"}]}
    filename = 'data/raw/test_world_bank_data.json'
    downloader.save_data_to_file(data, filename)

    loaded_data = downloader.load_data_from_file(filename)
    assert loaded_data == data

    # Clean up
    os.remove(filename)


if __name__ == "__main__":
    pytest.main()
