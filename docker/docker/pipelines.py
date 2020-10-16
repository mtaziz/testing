"""
Required modules to run this file
"""
import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from unicodedata import normalize

import mysql.connector
import pandas as pd
from scrapy.exceptions import DropItem

from . import path, directory
from .makes_mappings import makes_mapping

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, 'rvp_crawlers/all_makes.xlsx')


class RVPipeline(object):
    """
    This class stores the scrapped data in database models
    """
    vendorName = ''
    flag = False
    mydb = None
    cursor = None
    start_time = None

    def open_spider(self, spider):
        """
        stores the starts database connection, spider status and spider logs info
        :param spider:
        """
        self.mydb = mysql.connector.connect(
            host="172.21.0.2",
            user="rvp_user",
            password="topway",
            database="rvp_db",
            charset='utf8',
            use_unicode=True)

        self.cursor = self.mydb.cursor(prepared=True)
        self.cursor = self.mydb.cursor(buffered=True)

        spider.logger.info('Spider opened: %s', spider.name)

        date = datetime.datetime.today()
        now = datetime.datetime.utcnow()
        self.start_time = now

        filename = f'{spider.name}.txt'
        log_file = os.path.join(path, filename)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        rotating_file_log = RotatingFileHandler(log_file, maxBytes=10485760,
                                                backupCount=1)
        rotating_file_log.setLevel(logging.ERROR)
        rotating_file_log.setFormatter(formatter)
        root_logger.addHandler(rotating_file_log)

        root_logger_1 = logging.getLogger()
        root_logger_1.setLevel(logging.DEBUG)
        formatter_1 = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        rotating_file_log_1 = RotatingFileHandler(log_file, maxBytes=10485760,
                                                  backupCount=1)
        rotating_file_log_1.setLevel(logging.INFO)
        rotating_file_log_1.setFormatter(formatter_1)
        root_logger_1.addHandler(rotating_file_log_1)

        query = "SELECT * FROM RV_Logs WHERE start_time = %s AND " \
                "scraper_name = %s"
        self.cursor.execute(query, (now, spider.name))

        rvlogs_id = self.cursor.fetchone()
        direc = directory + '/' + filename
        if rvlogs_id is None:  # if spider not in rvlogs
            query = "INSERT INTO RV_Logs (scraper_name, start_time, end_time, \
            status, data_count, error_count, updated_at, added_at, date, logs)" \
                    "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            args = (spider.name, now, now, 3, 0, 0, now, now, date, direc)
            self.cursor.execute(query, args)

        self.mydb.commit()

    def read_mappings(self, mapping):
        """
        read data from excel file and update knowledge base of rv_makes
        :param mapping:
        :return: list of keys
        """
        makes = pd.read_excel(file_path)
        makes = [make for make in makes['makes']]

        for m in makes:
            if m not in mapping:
                mapping[m] = []

        return list(mapping)

    def insert_makes(self, makes, date, now):
        """
        Insert rv_makes in to database table
        :param makes:
        :param date:
        :param now:
        :return: makes
        """
        makes = [make.lower() for make in makes]
        makes = list(set(makes))
        makes.sort()

        query = "SELECT * FROM RV_Makes"
        self.cursor.execute(query)

        rv_makes = self.cursor.fetchall()
        res = [make[3] for make in rv_makes] 
        
        for make in makes:
            if make not in res:
                query = "INSERT INTO RV_Makes (make, date, updated_at, " \
                        "added_at) VALUES(%s, %s, %s, %s)"
                args = (make, date, now, now)
                self.cursor.execute(query, args)

                rv_makes = self.cursor.lastrowid

        self.mydb.commit()
        return makes

    def process_item(self, item, spider):
        """
        Process the item, save item values in corresponding tables. Drop items if required data
        is missing
        :param item:
        :param spider:
        :return: item
        """
        date = datetime.datetime.today()
        now = datetime.datetime.now()
        vendor_id = None

        if not self.flag:
            makes = self.read_mappings(makes_mapping)
            insert_makes = self.insert_makes(makes, date, now)
            self.flag = True

        if item['vendor_name']:
            self.vendorName = item['vendor_name']
            vendor_website = item['vendor_website']

            query = "SELECT * FROM Vendors WHERE name = %s"
            self.cursor.execute(query, (self.vendorName,))

            vendor_id = self.cursor.fetchone()

            if vendor_id is None:  # if vendor not in DataBase
                query = "INSERT INTO Vendors (name, website, date, " \
                        "updated_at, added_at) " \
                        "VALUES(%s, %s, %s, %s, %s)"

                args = (self.vendorName, vendor_website, date, now, now)
                self.cursor.execute(query, args)

                vendor_id = self.cursor.lastrowid

            else:
                vendor_id = vendor_id[0]

            self.mydb.commit()

        else:
            raise DropItem("Missing Vendor Name %s" % item)

        if item.get('retail_price') or item.get('sale_price') or item.get(
                'sale_price_call'):

            if item.get('rv_title'):

                title = item['rv_title']

                splitted_title = title.strip().split(' ')
                rv_status = splitted_title[0]
                my_status = rv_status

                if rv_status.lower() == 'pre-owned' or rv_status.lower() == \
                        'preowned':
                    rv_status = 'Used'

                year = splitted_title[1]

                if rv_status.lower() == 'new' or rv_status.lower() == 'used':

                    if len(year) == 4 and year.isdigit():
                        rv_year = year
                        status = 0

                        rv_status = (rv_status.lower() + ' ')
                        updated_title = title.replace(my_status, '').replace(
                            rv_year, '').strip()

                        copy = updated_title.replace(',', ' ').replace('®', ' ').replace(
                            '=', ' ').replace("  ", " ").replace("?", " ").replace(
                            "**", " ").replace("*", " ").replace(". ", " ").replace(
                            '"', "").replace('(', '').replace(')', '').strip()

                        copy = copy.replace("!", ' ').replace("™", '').split(" - ")[
                            0].replace(" -", "").replace("`", " ")

                        copy = copy.replace("'", ' ').replace('"', ' ').replace("’", ' ').replace(
                            "+", ' ').replace('”', ' ').replace("′", " ").replace(
                            "’s", " ").replace("”", " ").replace("“", " ").replace(
                            '″', ' ').replace('  ', ' ').strip()

                        updated_title = copy

                        if my_status.lower() == 'new':
                            status = 1

                        elif my_status.lower() == 'used':
                            status = 2

                        query = "SELECT * FROM RV WHERE title = %s AND " \
                                "status= %s and year = %s"
                        args = (updated_title, status, rv_year)
                        self.cursor.execute(query, args)

                        rv_id = self.cursor.fetchall()

                        if len(rv_id) == 0:  # if RV not in DataBase
                            query = "INSERT INTO RV (vendor_id, title," \
                                    "status, year, date, updated_at, added_at)" \
                                    "VALUES(%s, %s, %s, %s, %s, %s, %s)"
                            args = (vendor_id, updated_title, status, rv_year, date, now, now)
                            self.cursor.execute(query, args)
                            rv_id = self.cursor.lastrowid

                        else:
                            rv_id = rv_id[0][0]

                        self.mydb.commit()

                        if item.get('sale_price_call'):
                            sale_price_call = item['sale_price_call']

                            if sale_price_call:
                                sale_price_call = 1
                        else:
                            sale_price_call = 0

                        if item.get('best_price_call'):
                            best_price_call = item['best_price_call']

                            if best_price_call:
                                best_price_call = 1
                        else:
                            best_price_call = 0

                        rv_url = item.get('rv_url')
                        location = item.get('location')
                        rv_length = item.get('rv_length')

                        if rv_length:
                            rv_length = rv_length.replace(u'u\2032', '').replace(u'u\2033',
                                                                                 '').replace(
                                'â€²', "'").replace('â€³', '"')
                            rv_length = normalize('NFKD', rv_length).encode('ascii', 'ignore')

                        retail_price = item.get('retail_price')
                        if retail_price:
                            retail_price = retail_price.replace('$', '').replace(',', '')

                            if retail_price == '':
                                retail_price = None

                        sale_price = item.get('sale_price')
                        if sale_price:
                            sale_price = sale_price.replace('$', '').replace(',', '')
                            if sale_price == '':
                                sale_price = None

                        monthly_price = item.get('monthly_price')
                        if monthly_price:
                            monthly_price = monthly_price.replace('$', '').replace(',', '')
                            if monthly_price == '':
                                monthly_price = None

                        discount = item.get('discount')
                        if discount:
                            discount = discount.replace('$', '').replace('-', '').replace(',', '')
                        if discount == '' or discount == ' ':
                            discount = None

                        stock_no = item.get('stock_no')
                        rv_vin = item.get('rv_vin')
                        best_price_call_no = item.get('best_price_call_no')
                        rv_class = item.get('rv_class')
                        monthly_price_disclaimer = item.get('monthly_price_disclaimer')
                        rv_transmission = item.get('rv_transmission')

                        if item.get('rv_availability_status'):
                            rv_availability_status = item.get('rv_availability_status')

                            if rv_availability_status:
                                rv_availability_status = 1
                        else:
                            rv_availability_status = 0

                        rv_engine = item.get('rv_engine')
                        rv_cylinders = item.get('rv_cylinders')
                        rv_gvwr = item.get('rv_gvwr')
                        rv_sleeps = item.get('rv_sleeps')
                        rv_dimensions = item.get('rv_dimensions', )
                        rv_slide_outs = item.get('rv_slide_outs')
                        rv_floor_plan = item.get('rv_floor_plan')
                        rv_weight = item.get('rv_weight')
                        rv_width = item.get('rv_width')
                        rv_mileage = item.get('rv_mileage')
                        rv_dry_weight = item.get('rv_dry_weight')
                        rv_fuel_type = item.get('rv_fuel_type')
                        rv_interior_color = item.get('rv_interior_color')
                        order_no = item.get('order_no')
                        rv_exterior_color = item.get('rv_exterior_color')
                        rv_ext_width = item.get('rv_ext_width')
                        rv_ext_height = item.get('rv_ext_height')
                        rv_gross_weight = item.get('rv_gross_weight')
                        rv_model = item.get('rv_model')
                        rv_trim = item.get('rv_trim')
                        rv_make = item.get('rv_make')
                        rv_hitch_weight = item.get('rv_hitch_weight')
                        rv_fuel_capacity = item.get('rv_fuel_capacity')
                        rv_manufacturer = item.get('rv_manufacturer')

                        query = '''INSERT INTO RV_Details (url, location, length, retail_price, 
                        sale_price, monthly_price,discount, min_price, max_price, average_price, 
                        stock_no, vin, sale_price_call, best_price_call, best_price_call_no, 
                        rv_class, monthly_price_disclaimer, rv_transmission, 
                        rv_availability_status, rv_engine, rv_cylinders, rv_gvwr, rv_sleeps, 
                        rv_dimensions, rv_slide_outs, rv_floor_plan, rv_weight, rv_width, 
                        rv_mileage, rv_dry_weight, rv_fuel_type, rv_interior_color, order_no, 
                        rv_exterior_color, rv_ext_width, rv_ext_height, rv_gross_weight, 
                        rv_model, rv_trim, rv_make, rv_hitch_weight, rv_fuel_capacity, 
                        rv_manufacturer, date, rv_id, added_at, updated_at) VALUES (%s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s)'''

                        values = (
                            rv_url, location, rv_length, retail_price, sale_price,
                            monthly_price, discount, None, None, None, stock_no,
                            rv_vin, sale_price_call, best_price_call,
                            best_price_call_no, rv_class, monthly_price_disclaimer,
                            rv_transmission, rv_availability_status, rv_engine,
                            rv_cylinders, rv_gvwr, rv_sleeps, rv_dimensions,
                            rv_slide_outs, rv_floor_plan, rv_weight, rv_width,
                            rv_mileage, rv_dry_weight, rv_fuel_type,
                            rv_interior_color, order_no, rv_exterior_color,
                            rv_ext_width, rv_ext_height, rv_gross_weight, rv_model,
                            rv_trim, rv_make, rv_hitch_weight, rv_fuel_capacity,
                            rv_manufacturer, date, rv_id, now, now)

                        self.cursor.execute(query, values)
                        self.mydb.commit()

                    else:
                        raise DropItem("Invalid RV Year %s" % item)

                else:
                    raise DropItem("Invalid RV Condition %s" % item)

            else:
                raise DropItem("Missing RV Title in %s" % item)

        else:
            raise DropItem("Missing RV Price in %s" % item)

        return item

    def close_spider(self, spider):
        """
        Update the spider status based on data scraped count and errors
        :param spider:
        """
        stats = spider.crawler.stats.get_stats()
        error = stats.get('log_count/ERROR', 0)
        scrapped_count = stats.get('item_scraped_count', 0)
        spider.logger.info('Spider closed: %s', spider.name)

        status = 0

        if error == 0 and scrapped_count > 0:
            status = 1

        elif error == 0 and scrapped_count == 0:
            status = 2

        elif (error > 0 and scrapped_count > 0) and (error < scrapped_count):
            status = 2

        elif (scrapped_count == 0 and error > 0) or (error > scrapped_count):
            status = 4

        query = "SELECT * FROM Vendors WHERE name = %s"
        self.cursor.execute(query, (self.vendorName,))
        vendor = self.cursor.fetchone()

        if not vendor:
            status = 4
            vendor = None

        if status == 1:
            rvlogs = "UPDATE RV_Logs SET vendor_id = %s, status = %s, error_count = %s, " \
                     "data_count = %s, end_time = %s, last_run= %s where scraper_name = %s and " \
                     "start_time = %s "
            val = (vendor[0], status, error, scrapped_count,
                   datetime.datetime.utcnow(), datetime.datetime.utcnow(),
                   spider.name, self.start_time)

            self.cursor.execute(rvlogs, val)

        else:
            if vendor:
                rvlogs = "UPDATE RV_Logs SET vendor_id = %s, status = %s, error_count = %s, " \
                         "data_count = %s, end_time = %s where scraper_name = %s and start_time " \
                         "= %s "
                val = (vendor[0], status, error, scrapped_count,
                       datetime.datetime.utcnow(), spider.name,
                       self.start_time)

                self.cursor.execute(rvlogs, val)

            else:
                rvlogs = "UPDATE RV_Logs SET vendor_id = %s, status = %s, error_count = %s, " \
                         "data_count = %s, end_time = %s where scraper_name = %s and start_time " \
                         "= %s "
                val = (vendor, status, error, scrapped_count,
                       datetime.datetime.utcnow(), spider.name,
                       self.start_time)

                self.cursor.execute(rvlogs, val)

        self.mydb.commit()

        self.cursor.close()
        self.mydb.close()
