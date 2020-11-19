# Developer's Note: Though the URL listed in the URL attribute of the spider
#  is to the SavvyCitizen App, the event page for the municipality's website is
#  below: https://pennhills.org/upcoming-events/. The SavvyCitizen page is used
#  because it is easier to crawl.

import scrapy
import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

ADDRESS = ("102 Duff Rd, Penn Hills, PA 15235",)
LOCATION_NAME = ("Municipal Building",)

monthAndDayPattern = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
monthAndDayPattern += "|January|February|March|April|May|June|July"
monthAndDayPattern += "|August|September|October|November|December"
monthAndDayPattern += ")\S* (\d+)"
yearPattern = "\d\d\d\d"
timePattern = "(\d{1,2}|\d{1,2}\:\d\d)\s*([A|a|P|p]m)"
fromPattern = "from " + timePattern
toPattern = "to " + timePattern

# Iterate through list, go to each link, run the spider once.
class PennHillsSpider(CityScrapersSpider):
    name = "penn_hills_public_meetings"
    agency = "Penn Hills Municipality"
    timezone = "America/New_York"
    url = "https://savvycitizenapp.com/Community/140"

    start_urls = [url]

    def parse(self, response):
        self.logger.info("Parsing Penn Hills...")
        # The below parses the main link for sub-links which must in turn be checked.
        subLinks = response.xpath("//*[@class='agenda-day']/div/a/@href").getall()
        for subLink in subLinks:
            subLinkUrl = "https://savvycitizenapp.com" + subLink
            yield scrapy.Request(subLinkUrl, callback=self.parse_sub_link)

    # Make secondary spider with subLinkUrl
    def parse_sub_link(self, response):
        self.logger.info("Parsing sub link " + response.url + "...")
        title = self._parse_title(response)
        meeting = Meeting(
            title=title,
            description=self._parse_description(),
            classification=self._parse_classification(),
            start=self._parse_start(response),
            end=self._parse_end(response),
            all_day=False,
            location=self._parse_location(),
            links=self._parse_links(response, title),
            source=self._parse_source(response),
            status=self._parse_status(),
        )
        meeting["id"] = self._get_id(meeting)
        yield meeting

    def _parse_status(self):
        return "Tentative"

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        return response.xpath("/html/body/div/div/div/h1/text()").getall()[0]

    def _parse_description(self):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, response):
        """Parse start datetime as a naive datetime object."""
        start = ""
        if response.xpath("//*[@class='info']/tr/th/text()").getall()[1] == "When":
            rawTime = response.xpath("//*[@class='info']/tr/td/text()").getall()[1]
            year = re.search(yearPattern, rawTime).group(0)
            monthAndDay = self.getMonthAndDay(rawTime)
            timeStr = self.getTime(fromPattern, rawTime)
            start += year + " " + monthAndDay + " " + timeStr
            if len(timeStr) > 5:
                formatString = "%Y %B %d %I:%M %p"
            else:
                formatString = "%Y %B %d %I %p"
            start = datetime.strptime(start, formatString)
        return start

    def _parse_end(self, response):
        """Parse end datetime as a naive datetime object."""
        end = ""
        if response.xpath("//*[@class='info']/tr/th/text()").getall()[1] == "When":
            rawTime = response.xpath("//*[@class='info']/tr/td/text()").getall()[1]
            year = re.search(yearPattern, rawTime).group(0)
            monthAndDay = self.getMonthAndDay(rawTime)
            timeStr = self.getTime(toPattern, rawTime)
            end += year + " " + monthAndDay + " " + timeStr
            if len(timeStr) > 5:
                formatString = "%Y %B %d %I:%M %p"
            else:
                formatString = "%Y %B %d %I %p"
            end = datetime.strptime(end, formatString)
        return end

    def _parse_time_notes(self, response, index):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, response, index):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self):
        """Seems like the meeting is always in the same place given the info in the Agenda PDFs."""
        return {
            "address": ADDRESS,
            "name": LOCATION_NAME,
        }

    def _parse_links(self, response, title):
        """Parse or generate links."""
        return [{"href": response.url, "title": title}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def getTime(self, toFromPattern, rawTime):
        """Retrieves time in AM/PM format."""
        # Retrieves numerical time in HH:MM format
        timeNum = re.search(toFromPattern, rawTime).group(1)
        # Because strptime %I must be in 0-padded format, add 0 if hour is single digit
        if len(timeNum) == 1 or len(timeNum) == 4:
            timeNum = "0" + timeNum
        timeAMPM = re.search(toFromPattern, rawTime).group(2)
        return timeNum + " " + timeAMPM.upper()

    def getMonthAndDay(self, rawTime):
        month = re.search(monthAndDayPattern, rawTime).group(1)
        # If abbreviation, convert to full-length month name (for strptime %B format)
        if len(month) == 3:
            month = datetime.strptime(month.lower(), "%b").strftime("%B")
        day = re.search(monthAndDayPattern, rawTime).group(2)
        # Because striptime %d must be in 0-padded format, add 0 if day is single digit
        if len(day) == 1:
            day = "0" + day
        return month + " " + day
