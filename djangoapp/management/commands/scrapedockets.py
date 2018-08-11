from django.core.management.base import BaseCommand
from Integration.djangoapp.models import Case

import requests
import lxml
from lxml import html
import time, datetime

class Command(BaseCommand):
    help = 'Scrapes the sites for new dockets'

    def handle(self, *args, **options):
        self.stdout.write('\nScraping started at %s\n' % str(datetime.datetime.now()))

        courts = {'Minneapolis': 'http://www.mnd.uscourts.gov/calendars/mpls/index.html', 'St. Paul': 'http://www.mnd.uscourts.gov/calendars/stp/index.html', 'Duluth': 'http://www.mnd.uscourts.gov/calendars/dul/index.html', 'Fergus Falls & Bemidji': 'http://www.mnd.uscourts.gov/calendars/ff/index.html'}

        for court, url in courts.iteritems():
            self.stdout.write('Scraping url: %s\n' % url)
            r = requests.get(url)
            root = lxml.html.fromstring(r.content)
            # Find the correct table element, skip the first row
            for tr in root.cssselect('table[cellpadding=1] tr')[1:]:
                tds = tr.cssselect('td')
                start = tds[1].text_content().strip()
                end = tds[2].text_content().strip()
                description = tds[3].text_content().strip()
                convertedStart = convertTime(start)
                convertedEnd = convertTime(end)
                dbStart = datetime.datetime.fromtimestamp(convertedStart)
                dbEnd = datetime.datetime.fromtimestamp(convertedEnd)

                if not Case.objects.filter(start=dbStart, end=dbEnd, court=court, description=description):
                    c = Case(start=dbStart, end=dbEnd, court=court[:60], description=description[:1024])
                    c.save()

now = time.gmtime(time.time())

def convertTime(t):
    """Converts times in format HH:MMPM into seconds from epoch (but in CST)"""
    convertedTime = time.strptime(t + ' ' + str(now.tm_mon) + ' ' + str(now.tm_mday) + ' ' + str(now.tm_year), "%I:%M%p %m %d %Y")
    return time.mktime(convertedTime)
    # This used to add 5 * 60 * 60 to compensate for CST