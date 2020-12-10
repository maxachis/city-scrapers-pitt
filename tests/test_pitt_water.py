from datetime import datetime
from os.path import dirname, join

import pytest

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.pitt_water import PittWaterSpider

test_response = file_response(
    join(dirname(__file__), "files", "pitt_water.html"),
    url="https://www.pgh2o.com/news-events/events-meetings",
)

spider = PittWaterSpider()

freezer = freeze_time("2020-12-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_description():
    assert parsed_items[0]["description"] == ""


def test_title():
    assert parsed_items[0]["title"] == "December 2020 Board Meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 12, 18, 10, 00)


def test_end():
    assert parsed_items[0]["end"] == datetime(2020, 12, 18, 12, 00)


def test_status():
    assert parsed_items[0]["status"] == "Tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "address": " 1200 Penn Avenue Pittsburgh, PA 15222",
        "name": "",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "https://www.pgh2o.com/news-events/events-meetings"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "/news-events/events-meetings/2020-12-18-december-2020-board-meeting",
            "title": "December 2020 Board Meeting",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == "Board"


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
