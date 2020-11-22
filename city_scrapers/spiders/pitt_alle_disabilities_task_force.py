import re
from datetime import datetime

from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

# The ADA Events page, bizarrely, does not list the meeting times, as of 11/21.
# The November Agenda lists the start time as 2PM, so I have listed that as the default
START_TIME = "02 PM"


class PittAlleDisabilitiesSpider(CityScrapersSpider):
    name = "pitt_alle_disabilities_task_force"
    agency = "City-County Task Force on Disabilities"
    timezone = "America/New_York"
    url = "https://pittsburghpa.gov/dcp/events"
    start_urls = [url]

    def parse(self, response):
        self.logger.info("PARSING " + self.name + "...")
        xpath = "//*[@class='collapsing-content']/a[1]/text()[not(contains(.,'\r\n'))]"
        events = response.xpath(xpath).getall()
        xpath = (
            "//h1/text()[contains(.,'ADA Events')]/following::p[position() < 3]/text()"
        )
        description = response.xpath(xpath).get(0)
        for i in range(len(events)):
            if events[i].strip() != "":
                meeting = Meeting(
                    title=self._parse_title(),
                    description=description,
                    classification=self._parse_classification(),
                    start=self._parse_start(events[i]),
                    end=self._parse_end(),
                    all_day=False,
                    # time_notes=self._parse_time_notes(response, i),
                    location=self._parse_location(),
                    links=self._parse_links(),
                    source=self._parse_source(response),
                    status=self._parse_status(),
                )
                # meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def _parse_status(self):
        return "Tentative"

    def _parse_title(self):
        """Parse or generate meeting title."""
        return "City-County Task Force on Disabilities Meetings"

    def _parse_description(self, response):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self):
        """Parse or generate classification from allowed options."""
        return COMMITTEE

    def _parse_start(self, eventStr):
        """Parse start datetime as a naive datetime object."""
        eventStr = eventStr.strip().replace(",", "")
        eventStr = eventStr + " " + START_TIME
        formatString = "%A %B %d %Y %I %p"
        start = datetime.strptime(eventStr, formatString)
        return start

    def _parse_end(self):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self):
        """Seems like the meeting is always in the same place given the info in the Agenda PDFs."""
        return None

    def _parse_links(self):
        """Parse or generate links."""
        href = "https://us02web.zoom.us/j/83666489136"
        title = "City-County Task Force on Disabilities Meetings"
        return [{"href": href, "title": title}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
