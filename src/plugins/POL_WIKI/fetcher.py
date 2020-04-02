import logging
from pandas import DataFrame
from collections import OrderedDict

from utils.fetcher_abstract import AbstractFetcher
from .utils import to_number, extract_data_table, fetch_html_tables_from_wiki

__all__ = ('PolandWikiFetcher',)

logger = logging.getLogger(__name__)


class PolandWikiFetcher(AbstractFetcher):
    LOAD_PLUGIN = True

    def update_total_cases(self, data: DataFrame):
        logger.info("Processing total number of cases in Poland")

        total_deaths = 0
        for index, row in data.iterrows():
            item = OrderedDict(row)
            total_deaths = total_deaths + to_number(item['Official deaths daily'])

            self.db.upsert_data(
                date=item['Date'],
                country='Poland',
                countrycode='POL',
                adm_area_1='',
                tested=to_number(item['Quarantined']),
                quarantined=to_number(item['Tested (total)']),
                confirmed=to_number(item['Confirmed']),
                dead=total_deaths,
                recovered=to_number(item['Recovered']),
                source='POL_WIKI'
            )

    def update_confirmed_cases(self, data: DataFrame):
        logger.info("Processing new confirmed cases in Poland per voivodeship")

        for index, row in data.iterrows():
            item = OrderedDict(row)

            for (voivodeship_name, voivodeship_confirmed) in row.iteritems():
                if voivodeship_name in ['Date', 'Poland daily', 'Poland total']:
                    continue
                if to_number(voivodeship_confirmed) == 0:
                    continue

                self.db.upsert_data(
                    date=item['Date'],
                    country='Poland',
                    countrycode='POL',
                    adm_area_1=voivodeship_name,
                    confirmed=to_number(voivodeship_confirmed),
                    source='POL_WIKI'
                )

    def update_deaths_by_voivodeship(self, data: DataFrame):
        logger.info("Processing deaths in Poland by voivodeship")

        for index, row in data.iterrows():
            item = OrderedDict(row)

            for (voivodeship_name, voivodeship_deaths) in row.iteritems():
                if voivodeship_name in ['Date', 'Poland daily', 'Poland total']:
                    continue
                if to_number(voivodeship_deaths) == 0:
                    continue

                self.db.upsert_data(
                    date=item['Date'],
                    country='Poland',
                    countrycode='POL',
                    adm_area_1=voivodeship_name,
                    dead=to_number(voivodeship_deaths),
                    source='POL_WIKI'
                )

    def run(self):
        url = 'https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Poland'
        html_data = fetch_html_tables_from_wiki(url)
        self.update_total_cases(
            data=extract_data_table(html_data, text="timeline in Poland"))
        self.update_confirmed_cases(
            data=extract_data_table(html_data, text="New confirmed cases"))
        self.update_deaths_by_voivodeship(
            data=extract_data_table(html_data, text="deaths in Poland by voivodeship")
        )