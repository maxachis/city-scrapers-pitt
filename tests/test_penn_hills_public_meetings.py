from datetime import datetime
from os.path import dirname, join

import pytest

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.penn_hills_public_meetings import PennHillsSpider

test_response = file_response(
    join(dirname(__file__), "files", "penn_hills_public_meetings.html"),
    url="https://savvycitizenapp.com/Community/140",
)
test_sub_response = file_response(
    join(dirname(__file__), "files", "penn_hills/2020_11_18_Zoning_Hearing_Board.html"),
    url="https://savvycitizenapp.com/Community/140",
)
spider = PennHillsSpider()

freezer = freeze_time("2020-11-19")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

# Due to the unique nature of this spider of having to parse links within the first link
# This spider tests the basic "parse" method first, and then the "parse_sub_link" method


def test_response_url():
    # Tests that spider properly identifies and assembles href link in first calendar entry on page
    assert parsed_items[0].url == "https://savvycitizenapp.com/o/29901"


subLinkURL = "penn_hills/2020_11_18_Zoning_Hearing_Board.html"
subLinkResult = [item for item in spider.parse_sub_link(test_sub_response)]

# The following tests the attributes from the sub_link's response
def test_title():
    assert subLinkResult[0]["title"] == "Zoning Hearing Board"


def test_description():
    assert subLinkResult[0]["description"] == ""


def test_start():
    assert subLinkResult[0]["start"] == datetime(2020, 11, 18, 19, 0)


def test_end():
    assert subLinkResult[0]["end"] == datetime(2020, 11, 18, 20, 30)


def test_id():
    assert (
        subLinkResult[0]["id"]
        == "penn_hills_public_meetings/202011181900/x/zoning_hearing_board"
    )


def test_status():
    assert subLinkResult[0]["status"] == "Tentative"


def test_location():
    assert subLinkResult[0]["location"] == {
        "name": ("Municipal Building",),
        "address": ("102 Duff Rd, Penn Hills, PA 15235",),
    }


def test_source():
    assert subLinkResult[0]["source"] == "https://savvycitizenapp.com/Community/140"


def test_links():
    assert subLinkResult[0]["links"] == [
        {
            "href": "https://savvycitizenapp.com/Community/140",
            "title": "Zoning Hearing Board",
        }
    ]


def test_classification():
    assert subLinkResult[0]["classification"] == "Commission"


@pytest.mark.parametrize("item", subLinkResult)
def test_all_day(item):
    assert item["all_day"] is False
