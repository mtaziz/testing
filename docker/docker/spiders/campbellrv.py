import scrapy

from ..items import Rv_Details


class CampbellrvSpider(scrapy.Spider):
    name = 'campbellrv'
    allowed_domains = ['www.campbellrv.com']
    start_urls = ['https://www.campbellrv.com/rv-search?s=true']

    page = 2

    def parse(self, response):

        rv_urls = response.xpath(
            "//div[@class='unit-title-wrapper grid-mode']/div[@class='h3 unit-title']/a/@href"
        ).getall()

        for url in rv_urls:
            new_url = "https://www.campbellrv.com" + url
            yield scrapy.Request(url=new_url, callback=self.parse_rest)

        last_page = int(
            response.xpath(
                "//ul[@class='pagination']/li[last()-1]/a/text()").get())
        while self.page in range(2, last_page + 1):
            url = f"https://www.campbellrv.com/rv-search?s=true&page={self.page}"
            yield scrapy.Request(url=url, callback=self.parse)
            self.page += 1

    def parse_rest(self, response):

        rv_details = Rv_Details()
        rv_details["vendor_name"] = "Campbell RV"
        rv_details['vendor_website'] = self.allowed_domains[0]
        
        rv_details['rv_url'] = response.url

        rv_details['rv_title'] = response.xpath(
            "//div[@class='container']//h1/text()").get()

        rv_details['sale_price'] = response.xpath(
            "//ul[@class='price-info']/li[@class='sale-price-wrapper']/span[2]/text()"
        ).get()

        rv_details['retail_price'] = response.xpath(
            "//ul[@class='price-info']/li[@class='reg-price-wrapper']/span[2]/text()"
        ).get()

        if rv_details['retail_price'] is not None:
            rv_details['retail_price'] = rv_details['retail_price'].split(
                ".")[0]

        if rv_details['sale_price'] is not None:
            rv_details['sale_price'] = rv_details['sale_price'].split(".")[0]

        rv_details['discount'] = response.xpath(
            "//ul[@class='price-info']/li[@class='you-save-wrapper']/span[2]/text()"
        ).get()

        if rv_details['retail_price'] == '':
            rv_details['retail_price'] = None

        if rv_details['sale_price'] == '':
            rv_details['sale_price'] = None

        if rv_details['discount'] == '':
            rv_details['discount'] = None

        rv_details['monthly_price'] = response.xpath(
            "//div[@class='payments-around-container']/span[@class='payment-text']/text()"
        ).get()

        if rv_details['monthly_price']:
            rv_details['monthly_price'] = rv_details['monthly_price'].replace(
                " /mo.", "")

        if rv_details['monthly_price'] == '':
            rv_details['monthly_price'] = None

        rv_details['best_price_call'] = False
        best_price_call = response.xpath(
            "//a[@class='btn btn-primary btn-glp']/text()").get()
        if best_price_call:
            rv_details['best_price_call'] = True

        best_price_call_no = response.xpath(
            "//div[@class='phone']/a/text()").get()
        if best_price_call_no:
            rv_details['best_price_call_no'] = best_price_call_no

        rv_details['stock_no'] = response.xpath(
            "//div[@class='unit-stock-info-wrapper']/div[@class='unit-stock-number-wrapper']/span[2]/text()"
        ).get()

        rv_details['location'] = response.xpath(
            "normalize-space(//div[@class='unit-stock-info-wrapper']/div[@class='unit-location-wrapper']/span/text()[2])"
        ).get()

        rv_details['rv_vin'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='Specvin specs-desc']/text()"
        ).get()

        rv_details['rv_length'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecLength specs-desc']/text()"
        ).get()

        rv_details['rv_ext_width'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecExtWidth specs-desc']/text()"
        ).get()

        rv_details['rv_ext_height'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecExtHeight specs-desc']/text()"
        ).get()

        rv_details['rv_interior_color'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecInteriorColor specs-label']/text()"
        ).get()

        rv_details['rv_exterior_color'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecExteriorColor specs-desc']/text()"
        ).get()

        rv_details['rv_class'] = response.xpath(
            "//div[@class='unit-stock-info-wrapper']/div[@class='unit-rv-type-wrapper']//span/text()"
        ).get()

        rv_details['rv_sleeps'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecSleeps specs-desc']/text()"
        ).get()

        rv_details['rv_slide_outs'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecSlideCount specs-desc']/text()"
        ).get()

        rv_details['rv_gross_weight'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecGrossWeight specs-desc']/text()"
        ).get()

        rv_details['rv_dry_weight'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecDryWeight specs-desc']/text()"
        ).get()

        rv_details['rv_hitch_weight'] = response.xpath(
            "//table[@class='table specs-table']//tr/td[@class='SpecHitchWeight specs-desc']/text()"
        ).get()

        rv_details['rv_availability_status'] = True

        yield rv_details