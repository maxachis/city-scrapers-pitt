import scrapy
import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

LOCATION_XPATH = (
    "//td[count(//table/thead/tr/th[.='Location & Time']/preceding-sibling::th)+1]/p"
)
SCHEDULE_XPATH = (
    "//td[count(//table/thead/tr/th[.='Schedule']/preceding-sibling::th)+2]/p/text()"
)
TIME_XPATH = "//p[contains(.,'All meetings start at')]/text()"


class AlleRedevelopmentAuthoritySpider(CityScrapersSpider):
    name = "alle_redevelopment_authority"
    agency = "Redevelopment Authority of Allegheny County (RAAC)"
    timezone = "America/New_York"
    url = "https://www.alleghenycounty.us/economic-development/authorities/meetings-reports/raac/meetings.aspx"

    start_urls = [url]

    def parse(self, response):
        self.logger.info("Parsing " + self.agency + "...")
        location = self._parse_location(response)
        time = self._parse_time(response)
        dates = response.xpath(SCHEDULE_XPATH).getall()
        for i in range(len(dates)):
            meeting = Meeting(
                title=self.agency + " Board Meeting",
                description="",
                classification=BOARD,
                start=self._parse_datetime(dates[i], time),
                # end=self._parse_datetime(raw_date, start_and_end[1]),
                all_day=False,
                # time_notes=self._parse_time_notes(),
                location=location,
                links=response.url,
                source=response.url,
                status=self._parse_status(dates[i]),
            )
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_location(self, response):
        """Parse location information"""
        address = response.xpath(LOCATION_XPATH).get(1)
        address = re.sub("(\<br\>)", "\n", address)
        address = re.sub("(\<\/*p\>|\\xa0)", "", address)
        return {
            "address": address,
            "name": "",
        }

    def _parse_datetime(self, date, time):
        date = re.sub("(\-|Cancelled|\*|\,)", "", date).strip()
        dt_string = date + " " + time.strip()
        formatString = "%B %d %Y %I:%M %p"
        dt = datetime.strptime(dt_string, formatString)
        return dt

    def _parse_status(self, date):
        if "cancelled" in date.lower():
            return "CANCELLED"
        else:
            return "TENTATIVE"

    def _parse_time(self, response):
        time = response.xpath(TIME_XPATH).get(1)
        time = re.sub("^(.*)(?=\d\d\:\d\d)", "", time)
        time = re.sub("(\\xa0)", " ", time)
        return time
