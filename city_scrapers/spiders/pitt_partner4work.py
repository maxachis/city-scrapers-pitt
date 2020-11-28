import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

# Start and end times not currently listed on Partner4Work website
# However, a copy of their meeting minutes on line listed a recent meeting as being at 8:30 AM and ending at 9:30 AM
START_TIME = "08:30 AM"
END_TIME = "09:30 AM"
DESCRIPTION = "Advanced registration is requested. Register at info@partner4work.org"

monthDayYearPattern = "(January|February|March|April|May|June|July"
monthDayYearPattern += "|August|September|October|November|December"
monthDayYearPattern += ")\S* (\d+),\S* \d{4}"


class PittPartner4WorkSpider(CityScrapersSpider):
    name = "pitt_partner4work"
    agency = "Partner4Work Workforce Development Board"
    timezone = "America/New_York"
    url = "https://www.partner4work.org/about/board-meetings"
    start_urls = [url]

    def parse(self, response):
        self.logger.info("PARSING " + self.name + "...")
        xpath = "//h3/text()[contains(.,'Board Meetings')]/following::ul/li"
        events = response.xpath(xpath).getall()
        for i in range(len(events)):
            date = self.get_date(events[i])
            if date != None:
                meeting = Meeting(
                    title=self._parse_title(),
                    description=DESCRIPTION,
                    classification=self._parse_classification(),
                    start=self._parse_start(date),
                    end=self._parse_end(date),
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
        return self.agency + " Meeting"

    def _parse_description(self, response):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, eventStr):
        """Parse start datetime as a naive datetime object."""
        eventStr = eventStr.strip().replace(",", "")
        eventStr = eventStr + " " + START_TIME
        formatString = "%B %d %Y %I:%M %p"
        start = datetime.strptime(eventStr, formatString)
        return start

    def _parse_end(self, eventStr):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        eventStr = eventStr.strip().replace(",", "")
        eventStr = eventStr + " " + END_TIME
        formatString = "%B %d %Y %I:%M %p"
        start = datetime.strptime(eventStr, formatString)
        return start

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
        title = self.agency + " Meeting"
        return [{"href": self.url, "title": title}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def get_date(self, eventStr):
        print("READING: " + eventStr)
        result = re.search(monthDayYearPattern, eventStr)
        if result != None:
            return result.group(0)
        else:
            return None
