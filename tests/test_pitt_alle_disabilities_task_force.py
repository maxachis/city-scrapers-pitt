from datetime import datetime
from os.path import dirname, join

import pytest

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.pitt_alle_disabilities_task_force import (
    PittAlleDisabilitiesSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "pitt_alle_disabilities_task_force.html"),
    url="https://pittsburghpa.gov/dcp/events",
)
spider = PittAlleDisabilitiesSpider()

freezer = freeze_time("2020-11-15")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
print(parsed_items)

freezer.stop()


def test_description():
    assert (
        "The City-County Task Force on Disabilities is moving virtual!"
        in parsed_items[0]["description"]
    )


def test_title():
    assert parsed_items[0]["title"] == "City-County Task Force on Disabilities Meetings"


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 11, 16, 14, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "pitt_alle_disabilities_task_force/202011161400/x/city_county_task_force_on_disabilities_meetings"
    )


def test_status():
    assert parsed_items[0]["status"] == "Tentative"


def test_location():
    assert parsed_items[0]["location"] is None


def test_source():
    assert parsed_items[0]["source"] == "https://pittsburghpa.gov/dcp/events"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://us02web.zoom.us/j/83666489136",
            "title": "City-County Task Force on Disabilities Meetings",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == "Committee"


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
