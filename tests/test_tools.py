import pytest
import os
import sys

sys.path.append(os.path.abspath("../tools"))
sys.path.append(os.path.abspath(".."))
from tools.get_weather import get_weather
from tools.check_versailles_availability import check_versailles_availability
from tools.search_train import search_train
from tools.book_airbnb import book_airbnb


def test_weather_tool():
    result = get_weather("Versailles")
    assert "Versailles" in result


def test_versailles_availability():
    result = check_versailles_availability("2025-10-01")
    assert isinstance(result, str)


def test_search_train():
    result = search_train("Paris", "Versailles")
    assert isinstance(result, list) or isinstance(result, str)


def test_book_airbnb():
    result = book_airbnb("listing123")
    assert "confirmée" in result
