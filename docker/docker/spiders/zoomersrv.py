import scrapy

from ..items import Rv_Details


class ZoomersrvSpider(scrapy.Spider):
    name = 'zoomersrv'
    allowed_domains = ['www.zoomersrviowa.com']
    start_urls = ['https://www.zoomersrviowa.com/rv-search?s=true']

    page = 2

    def parse(self, response):

        rv_urls = response.xpath(
            "//div[@class='h3 unit-title']/a/@href").getall()

        for url in rv_urls:
            new_url = "https://www.zoomersrviowa.com" + url
            yield scrapy.Request(url=new_url, callback=self.parse_rest)

        next_page = response.xpath(
            "//ul[@class='pagination']/li[last()-1]/a/text()").get()
        if next_page:
            last_page = int(next_page)
            while self.page in range(2, last_page + 1):
                url = f"https://www.zoomersrviowa.com/rv-search?s=true&page={self.page}"
                yield scrapy.Request(url=url, callback=self.parse)
                self.page += 1

    def parse_rest(self, response):

        rv_details = Rv_Details()
        rv_details["vendor_name"] = "Zoomers RV"
        rv_details['vendor_website'] = self.allowed_domains[0]
        
        rv_details['rv_url'] = response.url

        rv_details['rv_title'] = response.xpath(
            "normalize-space(//div[@class='col-xs-12 col-xl-10 col-xl-offset-1']/h1/text())").get()

        rv_details['sale_price'] = response.xpath(
            "//ul[@class='price-info']/li[@class='sale-price-wrapper']/span[@class='sale-price-text']/text()").get()

        if not rv_details['sale_price']:
            rv_details['sale_price'] = response.xpath(
                "//div[@class='PriceInfo']/span[@class='SalesPriceText']/text()").get()

        rv_details['retail_price'] = response.xpath(
            "//ul[@class='price-info']/li[@class='reg-price-wrapper']/span[@class='reg-price-text']/text()").get()

        if rv_details['retail_price'] is not None:
            rv_details['retail_price'] = rv_details['retail_price'].split(".")[
                0]

        if rv_details['sale_price'] is not None:
            rv_details['sale_price'] = rv_details['sale_price'].split(".")[0]

        rv_details['discount'] = response.xpath(
            "//ul[@class='price-info']/li[@class='you-save-wrapper']/span[@class='you-save-text']/text()").get()

        rv_details['monthly_price'] = response.xpath(
            "//div[@class='payments-around-container']/span[@class='payment-text']/text()").get()

        if rv_details['discount'] is not None:
            rv_details['discount'] = rv_details['discount'].split(".")[0]

        if rv_details['monthly_price'] is not None:
            rv_details['monthly_price'] = rv_details['monthly_price'].replace(
                " /mo.", "")

        sale_price_call = response.xpath(
            "//ul[@class='price-info']/li[@class='no-price-wrapper']/span[@class='no-price']/text()").get()

        rv_details["sale_price_call"] = False
        if sale_price_call is not None:
            rv_details["sale_price_call"] = True

        rv_details['best_price_call_no'] = response.xpath(
            "//ul[@class='top-header-location-container list-unstyled']/li/a/@title").get()

        rv_details['rv_availability_status'] = True

        rv_details['stock_no'] = response.xpath(
            "//div[@class='unit-stock-number-wrapper']/span[@class='stock-number-text']/text()").get()

        rv_details['location'] = response.xpath(
            "normalize-space(//div[@class='unit-location-wrapper']/span[@class='unit-location-text']/text()[2])").get()

        rv_details['rv_length'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecLength specs-desc']/text()").get()

        rv_details['rv_ext_width'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecExtWidth specs-desc']/text()").get()

        rv_details['rv_ext_height'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecExtHeight specs-desc']/text()").get()

        rv_details['rv_class'] = response.xpath(
            "//div[@class='unit-stock-info-wrapper']/div/span[@class='rv-type-label']/text()").get()

        rv_details['rv_sleeps'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecSleeps specs-desc']/text()").get()

        rv_details['rv_slide_outs'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecSlideCount specs-desc']/text()").get()

        rv_details['rv_interior_color'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecInteriorColor specs-desc']/text()").get()

        rv_details['rv_exterior_color'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecExteriorColor specs-desc']/text()").get()

        rv_details['rv_gross_weight'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecGrossWeight specs-desc']/text()").get()

        rv_details['rv_hitch_weight'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecHitchWeight specs-desc']/text()").get()

        rv_details['rv_dry_weight'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='SpecDryWeight specs-desc']/text()").get()

        rv_details['rv_vin'] = response.xpath(
            "//table[@class='table specs-table']/tbody/tr/td[@class='Specvin specs-desc']/text()").get()

        yield rv_details