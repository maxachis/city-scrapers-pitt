from datetime import datetime
from os.path import dirname, join

import pytest

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.alle_redevelopment_authority import (
    AlleRedevelopmentAuthoritySpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "alle_redevelopment_authority.html"),
    url="https://www.alleghenycounty.us/economic-development/authorities/meetings-reports/raac/meetings.aspx",
)

spider = AlleRedevelopmentAuthoritySpider()

freezer = freeze_time("2020-12-12")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_description():
    assert parsed_items[0]["description"] == ""


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Redevelopment Authority of Allegheny County (RAAC) Board Meeting"
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 11, 20, 10, 30)


def test_status():
    assert parsed_items[0]["status"] == "CANCELLED"


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "Allegheny County Economic Development\nBoard Room, Suite 900\nChatham One, 112 Washington Place\nPittsburgh, PA 15219 ",
        "name": "",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.alleghenycounty.us/economic-development/authorities/meetings-reports/raac/meetings.aspx"
    )


def test_links():
    assert (
        parsed_items[0]["links"]
        == "https://www.alleghenycounty.us/economic-development/authorities/meetings-reports/raac/meetings.aspx"
    )


def test_classification():
    assert parsed_items[0]["classification"] == "Board"


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
