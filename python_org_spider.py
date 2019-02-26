import scrapy
import re
from urllib.parse import quote
from scrapy.selector.unified import Selector
from scrapy.http import Response
from typing import List
from html2text import html2text


class PythonOrgSpider(scrapy.Spider):
    name = "python_org"
    start_urls = ['https://www.python.org/jobs/location/telecommute/']

    def parse(self, response: Response):
        for page in self._get_pages(response):
            yield response.follow(page, callback=self._parse_job_list)

    def _parse_job_list(self, response: Response):
        for job_link in self._get_job_link(response):
            yield response.follow(job_link, callback=self._parse_job_description)

    def _parse_job_description(self, r: Response):
        yield {
            'title': self._get_job_title(r),
            'company': self._get_company_name(r),
            'location': self._get_location(r),
            'description': self._get_description(r),
            'link': r.url
        }

    @staticmethod
    def _get_location(r: Response):
        return r.css('.listing-location a::text').get()

    @staticmethod
    def _get_description(r: Response):
        html_description = ''.join(r.css('.job-description').extract()).strip()
        return html2text(html_description)

    @staticmethod
    def _get_job_title(r: Response):
        return r.css('.company-name::text').get().strip()

    @staticmethod
    def _get_company_name(r: Response):
        company_data_section = r.css('.company-name')
        if not company_data_section:
            return None
        texts = company_data_section[0].css('::text').getall()
        return texts[-1].strip()


    @staticmethod
    def _get_job_link(response: Response) -> List[str]:
        return response.css('h2.listing-company > span.listing-company-name a::attr("href")').getall()

    @staticmethod
    def _get_pages(response: Response) -> List[str]:
        pages: List[str] = response.css('.pagination li a::attr("href")').getall()
        filtered_pages = list(filter(lambda x: len(x) > 0, pages))
        if not filtered_pages:
            return [response.url]
        return filtered_pages[:3]