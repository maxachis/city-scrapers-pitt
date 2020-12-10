import scrapy
import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

# TODO
# Add location scraper to get address at <p id="location-inline">. Use _parse_location()

monthAndDayPattern = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
monthAndDayPattern += "|January|February|March|April|May|June|July"
monthAndDayPattern += "|August|September|October|November|December"
monthAndDayPattern += ")\S* (\d+)"
yearPattern = "\d\d\d\d"
timePattern = "(\d{1,2}|\d{1,2}\:\d\d)\s*([A|a|P|p]m)"
fromPattern = "from " + timePattern
toPattern = "to " + timePattern


class PittWaterSpider(CityScrapersSpider):
    name = "pitt_water"
    agency = "Pittsburgh Water and Sewer Authority"
    timezone = "America/New_York"
    url = "https://www.pgh2o.com/news-events/events-meetings"

    start_urls = [url]

    def parse(self, response):
        self.logger.info("Parsing " + self.agency + "...")
        location = self._parse_location(response)
        events = response.xpath("//*[@class='event-details']/h3/span/text()").getall()
        raw_dates = response.xpath(
            "//*[@class='event-details']/div[@class='date']/text()[contains(.,'day')]"
        ).getall()
        starts_and_ends = response.xpath(
            "//*[@class='event-details']/div[@class='time']/text()[contains(.,'-')]"
        ).getall()
        for i in range(len(events)):
            raw_date = raw_dates[i]
            start_and_end = starts_and_ends[i]
            raw_date = raw_date.replace("\n", "").replace(",", "").strip()
            start_and_end = start_and_end.replace("\n", "").strip()
            start_and_end = re.split("-", start_and_end)
            meeting = Meeting(
                title=events[i],
                description=self._parse_description(),
                classification=BOARD,
                start=self._parse_datetime(raw_date, start_and_end[0]),
                end=self._parse_datetime(raw_date, start_and_end[1]),
                all_day=False,
                time_notes=self._parse_time_notes(),
                location=location,
                links=self._parse_links(response, i, events[i]),
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
        return "Mt Lebanon Commission Meeting"

    def _parse_description(self):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_datetime(self, date, time):
        """Parse start datetime as a naive datetime object."""
        dt_string = date.strip() + " " + time.strip()
        formatString = "%A %b %d %Y %I:%M %p"
        dt = datetime.strptime(dt_string, formatString)
        return dt

    def _parse_time_notes(self):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, response, index):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, response):
        """Parse location information"""
        loc_str = response.xpath("//*[@class='location-inline']/text()").getall()
        address = loc_str[0] + loc_str[1].replace("\n", " ")
        """Seems like the meeting is always in the same place given the info in the Agenda PDFs."""
        return {
            "address": address,
            "name": "",
        }

    def _parse_links(self, response, index, title):
        """Parse or generate links."""
        href = response.xpath("//*[@class='event-details']/parent::a/@href").get(index)
        title = title
        return [{"href": href, "title": title}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
