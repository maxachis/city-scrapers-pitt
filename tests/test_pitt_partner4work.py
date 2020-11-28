from datetime import datetime
from os.path import dirname, join

import pytest

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.pitt_partner4work import PittPartner4WorkSpider

test_response = file_response(
    join(dirname(__file__), "files", "pitt_partner4work.html"),
    url="https://www.partner4work.org/about/board-meetings",
)
spider = PittPartner4WorkSpider()

freezer = freeze_time("2020-11-28")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
print(parsed_items)

freezer.stop()


def test_description():
    assert (
        "Advanced registration is requested. Register at info@partner4work.org"
        in parsed_items[0]["description"]
    )


def test_title():
    assert (
        parsed_items[0]["title"] == "Partner4Work Workforce Development Board Meeting"
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 12, 11, 8, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2020, 12, 11, 9, 30)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "pitt_partner4work/202012110830/x/partner4work_workforce_development_board_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "Tentative"


def test_location():
    assert parsed_items[0]["location"] is None


def test_source():
    assert (
        parsed_items[0]["source"] == "https://www.partner4work.org/about/board-meetings"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.partner4work.org/about/board-meetings",
            "title": "Partner4Work Workforce Development Board Meeting",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == "Board"


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
