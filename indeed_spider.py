import scrapy
import re
from urllib.parse import quote
from scrapy.selector.unified import Selector
from scrapy.http import Response
from html2text import html2text


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
            yield scrapy.Request(url=self.__url(i), callback=self._parse)

    def _parse(self, response: scrapy.http.Response):
        for job_summary in response.css(".row"):
            full_description_link = job_summary.css('h2 a::attr("href")').get()
            yield response.follow(full_description_link, callback=self._parse_job_description)

    def _parse_job_description(self, r: Response):
        yield {
            'title': self._get_job_title(r),
            'company': self._get_company_name(r),
            'location': self._get_location(r),
            'description': self._get_description(r),
            'link': r.url
        }

    @staticmethod
    def _get_description(r: Response) -> str:
        html_descriptions = r.css('.jobsearch-JobComponent-description').extract()
        html_description = html2text(''.join(html_descriptions).strip())
        return html_description

    @staticmethod
    def _get_company_name(r: Response) -> str:
        return r.css('.jobsearch-InlineCompanyRating div::text').get().strip()

    @staticmethod
    def _get_location(r: Response) -> str:
        return r.css('.jobsearch-InlineCompanyRating > div::text').getall()[-1]

    @staticmethod
    def _get_job_title(r: Response) -> str:
        return r.css('h3::text').get()
