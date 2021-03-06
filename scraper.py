import os
os.environ["SCRAPERWIKI_DATABASE_NAME"] = "sqlite:///data.sqlite"

import scraperwiki
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime

applications_url = 'https://www.goldenplains.vic.gov.au/residents/my-home/planning-applications-currently-advertised'
html = scraperwiki.scrape(applications_url)
page = BeautifulSoup(html, 'html.parser')

for div in page.find_all('div', class_='accordion'):
  record = {
    'council_reference': div.find('h4').getText().split()[1],
    'info_url': applications_url,
    'date_scraped': date.today().isoformat()
  }
  for div2 in div.find_all('div', class_='pan-content'):
    if div2.find('span', string='Description:'):
      record['description'] = div2.find('p').get_text()
    elif div2.find('span', string='Application Location:'):
      record['address'] = div2.find('p').getText().split(', ', 1)[1] + ' VIC'
    elif div2.find('span', string='Advertising Starts:'):
      start_date = div2.find('span', class_='date-display-single')
      if start_date:
        record['on_notice_from'] = datetime.strptime(start_date.getText(), '%d/%m/%Y').date().isoformat()
    elif div2.find('span', string='The Planning Department will not make a decision before:'):
      end_date = div2.find('span', class_='date-display-single')
      if end_date:
        record['on_notice_to'] = datetime.strptime(end_date.getText(), '%d/%m/%Y').date().isoformat()

  scraperwiki.sqlite.save(unique_keys=['council_reference'], data=record, table_name="data")
