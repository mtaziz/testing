import scrapy


class Rv_Details(scrapy.Item):
    vendor_name = scrapy.Field()
    vendor_website = scrapy.Field()

    rv_title = scrapy.Field()
    rv_year = scrapy.Field()
    rv_brand = scrapy.Field()
    rv_makes = scrapy.Field()

    retail_price = scrapy.Field()
    sale_price = scrapy.Field()
    sale_price_call = scrapy.Field()
    best_price_call = scrapy.Field()
    best_price_call_no = scrapy.Field()
    stock_no = scrapy.Field()
    location = scrapy.Field()
    rv_class = scrapy.Field()
    monthly_price = scrapy.Field()
    monthly_price_disclaimer = scrapy.Field()
    discount = scrapy.Field()
    rv_url = scrapy.Field()
    rv_vin = scrapy.Field()
    rv_transmission = scrapy.Field()
    rv_availability_status = scrapy.Field()
    rv_engine = scrapy.Field()
    rv_cylinders = scrapy.Field()
    rv_length = scrapy.Field()
    rv_gvwr = scrapy.Field()
    rv_sleeps = scrapy.Field()
    rv_dimensions = scrapy.Field()
    rv_slide_outs = scrapy.Field()
    rv_floor_plan = scrapy.Field()
    rv_weight = scrapy.Field()
    rv_width = scrapy.Field()
    rv_mileage = scrapy.Field()
    rv_dry_weight = scrapy.Field()
    rv_fuel_type = scrapy.Field()
    rv_interior_color = scrapy.Field()
    order_no = scrapy.Field()
    rv_exterior_color = scrapy.Field()
    rv_ext_width = scrapy.Field()
    rv_ext_height = scrapy.Field()
    rv_gross_weight = scrapy.Field()
    rv_model = scrapy.Field()
    rv_trim = scrapy.Field()
    rv_make = scrapy.Field()
    rv_hitch_weight = scrapy.Field()
    rv_fuel_capacity = scrapy.Field()
    rv_manufacturer = scrapy.Field()
