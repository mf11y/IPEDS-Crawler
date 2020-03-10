import scrapy
from scrapy import Selector
import json
import time


class IPEDSSpider(scrapy.Spider):
    name = 'IPEDS-viewstate'
    start_urls = ['https://nces.ed.gov/ipeds/datacenter/login.aspx?gotoReportId=7']
    download_delay = 1.5

    def parse(self, response):
        yield scrapy.Request(
            url='https://nces.ed.gov/ipeds/datacenter/login.aspx?gotoReportId=7',
            callback=self.secondpage
        )

    def secondpage(self, response):
        yield scrapy.Request(
            url='https://nces.ed.gov/ipeds/datacenter/loginRedirector2.aspx',
            cookies={'DATACENTER_FLAGSTABLE': 'Institutional Characteristics 2018-19',
                     'DATACENTER_MAINTABLE': 'HD2018',
                     'DATACENTER_PermitLevel': '1',
                     'DATACENTER_SessionGuid': 'a4b365ac-5eef-43da-8f77-5b845a1485f8',
                     'DATACENTER_currentYear': '2018',
                     'DATACENTER_sessionStart': '3/4/2020 12:22:47 PM',
                     'DATACENTER_universe': 'main_table_1',
                     '_ga': 'GA1.3.1678560337.1583342530',
                     '_gat_GSA_ENOR0': '1',
                     '_gat_GSA_ENOR1': '1',
                     '_gid': 'GA1.2.1176194740.1583342530',
                     'fromIpeds': 'true'},
            callback=self.thirdpage,
        )

    def thirdpage(self, response):
        yield scrapy.FormRequest(
            url='https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx',
            formdata={
                'ctl00$contentPlaceHolder$ddlYears': '-1',
                'ddlSurveys': '-1',
                'ctl00$contentPlaceHolder$ibtnContinue.x': '35',
                'ctl00$contentPlaceHolder$ibtnContinue.y': '7',
                '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first(),
                '__VIEWSTATEGENERATOR': response.css('input#__VIEWSTATEGENERATOR::attr(value)').extract_first(),
                '__EVENTVALIDATION': response.css('input#__EVENTVALIDATION::attr(value)').extract_first()
            },
            callback=self.result,
        )

    def result(self, response):
        htm = response.selector.xpath('//table[@id="contentPlaceHolder_tblResult"]/tr').getall()
        infodict = dict()
        for row in htm:
            year = str(Selector(text=row).xpath('//td[1]/text()').get()).strip()
            survey = str(Selector(text=row).xpath('//td[2]/text()').get()).strip()
            title = str(Selector(text=row).xpath('//td[3]/text()').get()).strip()
            stata_link = str(Selector(text=row).xpath('//td[5]/a/@href').get()).strip()
            stata_program_link = str(Selector(text=row).xpath('//td[6]/a[3]/@href').get()).strip()
            dictionary = str(Selector(text=row).xpath('//td[7]/a/@href').get()).strip()
            entry = [stata_link, stata_program_link, dictionary]

            if year != "None":

                if survey in infodict:
                    if title in infodict[survey]:
                        infodict[survey][title][year] = entry
                    else:
                        infodict[survey][title] = {year: entry}
                else:
                    infodict[survey] = {title: {year: entry}}

        print(infodict)
        y = json.dumps(infodict)
        with open('ipeds.json', 'w') as fp:
            fp.write(y)

