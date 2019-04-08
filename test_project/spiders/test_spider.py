# -*- coding: utf-8 -*-
import scrapy
import urllib2
import logging
from test_project.items import TestItem

class TestSpider(scrapy.Spider):
    name = "test_spider"

    def start_requests(self):
        urls = [
            "https://www.bhphotovideo.com/c/product/1427329-REG/dell_aw17r5_7390slv_pca_alienware_17_17_3_r5.html",
            "https://www.bhphotovideo.com/c/product/1411003-REG/huawei_53010caj_hwd_nb_matebook_x.html",
            "https://www.bhphotovideo.com/c/product/1423741-REG/apple_mr942ll_a_15_4_macbook_pro_with.html",
            "https://www.bhphotovideo.com/c/product/1435132-REG/dell_i3180_a361gry_inspiron_11_3000_3180.html",
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        logging.info("Getting item details of " + response.url)
        brand = self.getBrand(response)
        model = self.getModel(response)
        img_urls = self.getImages(response)

        my_item = TestItem()
        my_item['url'] = response.url
        my_item['brand'] = brand
        my_item['model'] = model
        my_item['img_urls'] = list(dict.fromkeys(img_urls)) ##remove duplicatess

        logging.info("Yielding item...")
        yield my_item


    def getBrand(self, response):
        temp = response.xpath("//span[@itemprop='brand']/text()").extract_first()
        return temp if temp else self.getModel(response).split(' ')[0]

    def getYear(self, model):
        return model[model.find('(20'): model.find('(20') + 6] if model.find('(20') != -1 else None

    def getModel(self, response):
        model = response.xpath("//span[@itemprop='name']/text()").extract_first().strip().encode('utf-8')
        return model.strip() if model else model

    def getImages(self, response):
        """
        Returns:
        - {list} Lateral images URLs
        """
        ## this one extracts small images
        lst = response.xpath("//div[@class='image-thumbs js-imageThumbs js-close']/a/img/@data-src").extract()
        if len(lst) == 0:
            lst = response.xpath("//div[@class='image-thumbs js-imageThumbs js-close']/a/img/@src").extract()
        # logging.info("lst imgs len: " + str(len(lst)))
        """
        Now we need to get the bigger images, there're 2 scenarios here
        First pic usually looks like this:
        small:
        https://static.bhphoto.com/images/smallimages/1535638860000_1431885.jpg
        bigger:
        https://static.bhphoto.com/images/images500x500/1535638860000_1431885.jpg

        The rest look like this
        small:
        https://static.bhphoto.com/images/multiple_images/thumbnails/1535638523000_IMG_1056764.jpg
        bigger:
        https://static.bhphoto.com/images/multiple_images/images500x500/1535638523000_IMG_1056764.jpg
        """
        img_urls = []
        for item in lst:
            temp_item = item
            temp_list = temp_item.split('/')
            temp_list[-2] = 'images500x500'
            image_url = '/'.join(temp_list)
            img_urls.append(image_url)
        img_urls = list(dict.fromkeys(img_urls)) ##remove duplicates
        ## add the main picture to the beginning
        main_img = response.xpath("//img[@id='mainImage']/@src").extract_first()
        logging.info("Trying to insert main url")
        if not main_img:
            logging.warning("Could not find main image")
        else:
            ## remove main image from old list
            found = False
            for i in range(0, len(img_urls)):
                # get last part:
                code = img_urls[i].split('/')[-1].replace('.jpg', '')
                if code in main_img:
                    found = True
                    break
            if found:
                logging.info("Found old main img")
                img_urls.pop(i)
                img_urls.insert(0, main_img)
                logging.info("Printing as list")
                logging.info(img_urls)
                logging.info("Printing each one")
                for im in img_urls:
                    logging.info(im)
                logging.info("Inserted main url")
            else:
                logging.info("Could not find main url")
        return img_urls
