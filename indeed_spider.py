import scrapy
import re
from urllib.parse import quote
from scrapy.selector.unified import Selector


class IndeedSpider(scrapy.Spider):
    name = 'indeed'

    @staticmethod
    def __url(page):
        url = f'https://www.indeed.com/jobs?q={quote("Remote Python")}'
        pagestr = ""
        if page != 0:
             pagestr = f"&start={page * 10}"
        return f"{url}{pagestr}"

    def start_requests(self):
        for i in range(0, 6):
            yield scrapy.Request(url=self.__url(i), callback=self.__parse)

    @staticmethod
    def _no_whitespaces(str):
        return re.sub(r"\s", "", str)

    def _parse_full_description(self, response: scrapy.http.Response, data: map):
        description_section = response.css('.jobsearch-JobComponent-description')
        description = description_section.css('::text').getall()
        if not description:
            description = description_section.css('div::text').getall()
        data['description'] = ''.join(description)
        if not data['company']:
            data['company'] = response.css('.jobsearch-InlineCompanyRating div::text').get()
        data['company'] = self._no_whitespaces(data['company'])
        data['link'] = response.url
        yield data

    def _parse_summary(self, response: scrapy.http.Response, summary: Selector):
        full_description_link = summary.css('h2 a::attr("href")').get()
        partial_data = {
            'title': summary.css('h2 a::attr("title")').get(),
            'company': summary.css('.company a::text').get(),
            'location': summary.css('.location::text').get()
        }

        def callback(r):
            return self._parse_full_description(r, partial_data)

        return response.follow(full_description_link, callback=callback)

    def __parse(self, response: scrapy.http.Response):
        for job_summary in response.css(".row"):
            yield self._parse_summary(response, job_summary)




