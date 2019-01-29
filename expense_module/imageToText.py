import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('PS')
import matplotlib.pyplot as plt
import cv2
import pytesseract as pt
import re
import json
import datetime
import time
import json
import os
from django.conf import settings

directory = os.getcwd()
json_file_path = directory + '/expense_module/product_lookup.json'



json_file = open(json_file_path, 'r')
product_details_dict = json.load(json_file)

'''

product_details_dict = {
    "007874200192": {
        "name": "Sam's Choice Italia Spaghetti with Tomato Basil Sauce Meal Kit",
        "price": 1.86,
        "category": "Food"
    },
    "007874223735": {
        "name": "Great Value Steamable Mixed Vegetables",
        "price": 0.84,
        "category": "Vegetables"
    },
    "007373117001": {
        "name": "Mission Organics Whole Wheat Tortillas",
        "price": 2.54,
        "category": "Food"
    },
    "004667501350": {
        "name": "YoCrunch Oreo Cookies N' Cream Lowfat Yogurt",
        "price": 1.72,
        "category": "Snacks"
    },
    "007615033230": {
        "name": "ACT II Xtreme Butter Microwave Popcorn",
        "price": 3.98,
        "category": "Snacks"
    },
    "002200015586": {
        "name": "Orbit, Sugar Free Peppermint Chewing Gum",
        "price": 1.98,
        "category": "Snacks"
    },
    "002840058928": {
        "name": "Fritos Corn Chips, Chili Cheese, 9.25 Oz", 
        "price": 2.98, 
        "category": "Snacks"
    },
    "003800014371": {
        "name": "Kellogg's Special K Breakfast Cereal, Red Berries",
        "price": 3.88,
        "category": "Food"
    },
    "007874227614": {
        "name": "Great Value Original Potato Chips Party Size!",
        "price": 2.08,
        "category": "Snacks"
    },
    "004900005011": {
        "name": "Diet Coke Bottle, 2 Liter",
        "price": 1.25,
        "category": "Drink"
    },
    "004900005014": {
        "name": "Coca-Cola Zero Sugar Cola 2L Bottle", 
        "price": 1.25, 
        "category": "Drink"
    },
    "002500004086": {
        "name": "Simply Lemonade with Strawberry, 52 Fl. Oz.",
        "price": 2.34,
        "category": "Drink"
    },
    "001864301475": {
        "name": "Mainstays Plastic Hangers Black, 10 Count",
        "price": 1.17,
        "category": "Household"
    },
    "085058200200": {
        "name": "Fresh Strawberries, 1 lb",
        "price": 1.98,
        "category": "Fruits"
    },
    "007225003706": {
        "name": "Nature's Own® Honey Wheat Bread 20 oz. Bag",
        "price": 2.88,
        "category": "Food"
    },
    "084295910005": {
        "name": "Better Homes & Gardens Weston Mug",
        "price": 2.96,
        "category": "Utensils"
    },
    "005404867501": {
        "name": "Sliced Mushrooms, 8 oz",
        "price": 1.58,
        "category": "Vegetables"
    },
    "084027613047": {
        "name": "Contigo SnapSeal Byron 20 Oz Stainless-Steel Travel Mug, Black",
        "price": 14.72,
        "category": "Utensils"
    },
    "007874223226": {
        "name": "Sam's Choice Italia Penne with Mushroom Sauce Meal Kit",
        "price": 1.97,
        "category": "Food"
    },
    "004400003221": {
        "name": "Nabisco Chips Ahoy! Chunky Chocolate Chunk Cookies",
        "price": 2.56,
        "category": "Snacks"
    },
    "076125311657": {
        "name": "Mens Aw Ss Quick Dry Blue Cove L",
        "price": 6.88,
        "category": "apparels"
    },
    "001820025006": {
        "name": "Bud Ice Beer, 25 fl oz",
        "price": 1.5,
        "category": "Liquor"
    },
    "007289000478": {
        "name": "Heineken Lager Beer, 22 fl oz bottle",
        "price": 2.5,
        "category": "Liquor"
    },
    "750301951901": {
        "name": "Fresh Strawberries, 2 lb",
        "price": 3.78,
        "category": "Fruits"
    },
    "007278512511": {
        "name": "Germ X Advanced Hand Sanitizer Original Scent, 12 fl oz",
        "price": 2.66,
        "category": "Personal Needs"
    },
    "068113102607": {
        "name": "Great Value Lemon Scent Disinfecting Wipes, 35 count, 10 oz",
        "price": 1.83,
        "category": "Personal Needs"
    },
    "004900006104": {
        "name": "Coca-Cola Zero Mini-Cans, 7.5 fl oz, 6 Pack",
        "price": 2.58,
        "category": "Drink"
    },
    "007874209234": {
        "name": "Freshness Guaranteed Chocolate Chunk Cookies, 14 oz, 12 Count",
        "price": 2.87,
        "category": "Snacks"
    },
    "081288701583": {
        "name": "JLab Audio JBuds Pro Premium in-ear Earbuds with Mic, Guaranteed Fit, GUARANTEED FOR LIFE - Black", 
        "price": 9.88,
        "category": "Electronics"
    }, 
    "003400017500": {
        "name": "Hershey's Special Dark Mildly Sweet Chocolate with Almonds Extra Large Bar, 4 Oz",
        "price": 1.34, 
        "category": "Confection"
    },
    "000954203169": {
        "name": "Mclane Company Lindt Exc 78prc Cocoa Bar", 
        "price": 2.68, 
        "category": "Confection"
    }, 
    "068113107980": {
        "name": "Marketside Baklav", 
        "price": 1.0, 
        "category": "Snacks"
    }, 
    "002430004106": {
        "name": "Little Debbie Snacks Cosmic Brownies With Chocolate Chip Candy, 6ct", 
        "price": 1.50, 
        "category": "Snacks"
    },
    "003500076232": {
        "name": "Colgate Total Advanced Whitening Toothpaste, 5.8 Oz", 
        "price": 3.96, 
        "category": "Personal Needs"
    },
    "007203001353": {
        "name": "Entenmann's Little Bites Chocolate Chip Mini Muffins made with Real Chocolate, 5 pouches", 
        "price": 2.98, 
        "category": "Snacks"
    }, 
    "007418244572": {
        "name": "Softsoap Liquid Hand Soap, Fresh Citrus - 11.25 fl oz", 
        "price": 1.46,
        "category": "Personal Needs"
    }, 
    "001111112518": {
        "name": "Dove Gentle Exfoliating Body Wash, 22 oz", 
        "price": 5.94, 
        "category": "Personal Needs"
    }, 
    "068113124926": {
        "name": "Equate Nectarine Smoothie Hand Sanitizer, 3 fl oz", 
        "price": 0.96, 
        "category": "Personal Needs"
    }, 
    "004400003219": {
        "name": "Chips Ahoy! Cookies, Original, 13 Oz", 
        "price": 2.56,
        "category": "Snacks"
    },
    "002840020126": {
        "name": "Lay's Limon Flavored Potato Chips, 7.75 oz Bag", 
        "price": 2.48, 
        "category": "Snacks"
    }, 
    "005200020842": {
        "name": "Gatorade Thirst Quencher Fierce Sports Drink, Grape, 20 Fl Oz, 8 Count", 
        "price": 4.98, 
        "category": "Drink"
    }
}

'''


class process_image:
    
    def __init__(self, *args, **kwargs):        
        # Loading images and ploting it (converting to RGB from BGR)
        self.image =  cv2.cvtColor(cv2.imread(args[0]), cv2.COLOR_BGR2RGB)

    # Border Removal    
    def process_image(self):       
        # Edge detection (stores in self.canny_edges)
        self.detect_edges(200, 250)

        # Close gaps between edges (double page clouse => rectangle kernel)
        edges_image = cv2.morphologyEx(self.canny_edges, cv2.MORPH_CLOSE, np.ones((5, 11)))
        self.find_page_contours(edges_image, self.resize(self.image))
        
        # Recalculate to original scale
        self.contours = self.contours.dot(self.image.shape[0] / 800)
        self.cropped_image = self.transform_perspective(self.contours)

        
    def find_page_contours(self, edges, img):
        # Determining the corner points of the page contour
        
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Determining the contours with maximum area in the image
        height = edges.shape[0]
        width = edges.shape[1]
        MIN_COUNTOUR_AREA = height * width * 0.5
        MAX_COUNTOUR_AREA = (width - 10) * (height - 10)

        max_area = MIN_COUNTOUR_AREA
        page_contour = np.array([[0, 0],
                                [0, height-5],
                                [width-5, height-5],
                                [width-5, 0]])

        for cnt in contours:
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)

            # Page has 4 corners and it is convex
            if (len(approx) == 4 and
                    cv2.isContourConvex(approx) and
                    max_area < cv2.contourArea(approx) < MAX_COUNTOUR_AREA):
                
                max_area = cv2.contourArea(approx)
                page_contour = approx[:, 0]

        # Sort corners and offset them
        page_contour = self.vertices_sort(page_contour)
        self.contours = self.contour_offset(page_contour, (-5, -5))


    def transform_perspective(self, s_points):
        # Transforms the image from the starting points to the target points
        # Euclidean distance - calculate maximum height and width
        height = max(np.linalg.norm(s_points[0] - s_points[1]),
                    np.linalg.norm(s_points[2] - s_points[3]))
        width = max(np.linalg.norm(s_points[1] - s_points[2]),
                    np.linalg.norm(s_points[3] - s_points[0]))
        
        # Create target points
        t_points = np.array(
            [
                [0, 0],
                [0, height],
                [width, height],
                [width, 0]
            ], 
            np.float32
        )
        
        # getPerspectiveTransform() needs float32
        if s_points.dtype != np.float32:
            s_points = s_points.astype(np.float32)
        
        M = cv2.getPerspectiveTransform(s_points, t_points) 
        return cv2.warpPerspective(self.image, M, (int(width), int(height)))
    
    def detect_edges(self, min_val, max_val):
        # Detects the edges in the image with the help of Canny

        # Convert the image to Grayscale for easy processing
        img = cv2.cvtColor(self.resize(self.image), cv2.COLOR_BGR2GRAY)

        # Bilateral filter (blurs the image while retaining the edges)
        img = cv2.bilateralFilter(img, 9, 75, 75)
        # Adaptive thresholding
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 4)
        
        # Median Blur (the value of the center pixel is replaced by the average of the sorrounding pixels)
        img = cv2.medianBlur(img, 11)

        # Pad the image with 5px of black pixels
        img = cv2.copyMakeBorder(img, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        
        self.canny_edges = cv2.Canny(img, min_val, max_val)

    # Helper function
    def resize(self, img, height=800):
        # Resizes the image to the given height
        rat = height / img.shape[0]
        return cv2.resize(img, (int(rat * img.shape[1]), height))

    def vertices_sort(slf, vertices):
        # Sorts the 4 vertices of the page borders according to their order!
        # Assumption: x+y is minimum at the top-left corner and maximum at the 
        # top right corner

        diff = np.diff(vertices, axis=1)
        summ = vertices.sum(axis=1)
        return np.array(
            [
                vertices[np.argmin(summ)],
                vertices[np.argmax(diff)],
                vertices[np.argmax(summ)],
                vertices[np.argmin(diff)]
            ]
        )

    def contour_offset(self, cnt, offset):
        # Offsets the obtained contours by 5px due to padding
        cnt += offset
        cnt[cnt < 0] = 0
        return cnt


    def get_image(self):
        # Returns the cropped image
        return self.cropped_image

class detect_text:
    def __init__(self, *args, **kwargs):
        # Loading images converting it to grayscale
        self.image =  cv2.cvtColor(args[0], cv2.COLOR_BGR2GRAY)

        # Purchase parameters
        self.items_purchased = 0
        self.store_type = ''
        self.items = []
        self.payload = {}
        self.sku_codes = []
        self.transaction_id = ''
        #self.payload['items'] = []        
    
    def get_text(self):
        height, width= self.image.shape
        img = self.image
        img = cv2.resize(img, (width * 2, height * 2))
        image = cv2.resize(self.image, (width * 2, height * 2))
        raw_text = pt.image_to_string(image)
        raw_text = raw_text.split('\n')
        
        self.get_items(raw_text)
        return self.transaction_id, self.payload, self.sku_codes, self.items
    


    def get_items(self, text_dump):
        items_dump = []
        voided_entry = False
        voided_index = []
        index = 0
        items = {}

        product_details = {
            'name': '', 
            'sku_code': '',
            'price': [-1], 
            'category': '',
            'quantity': [1]
        }

        for index in range(len(text_dump)):
            if 'voided' in text_dump[index].lower():
                voided_entry = True
                # do the processing here
                voided_index.append(re.findall(r'\d{12}', text_dump[index + 1]))
                
            if 'total' in text_dump[index].lower():
                self.payload['total'] = re.findall(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{0,3})', text_dump[index])

            if 'walmart' in text_dump[index].lower():
                self.payload['vendor'] = 'Walmart'

            if 'items sold' in text_dump[index].lower() or 'ttems sold' in text_dump[index].lower():
                self.payload['no_of_items'] = re.findall(r'\d+', text_dump[index])

            if re.search(r'\d{12}', text_dump[index]):
                if 'ref' not in text_dump[index].lower() \
                    and 'aid' not in text_dump[index].lower():
                    items_dump.append(text_dump[index])

            if 'lb' in text_dump[index].lower(): 
                previous_entry = items_dump.pop()
                previous_entry = previous_entry + ' produce'
                items_dump.append(previous_entry)
                items_dump.append(text_dump[index])
            
            if re.search(r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', text_dump[index]):
                purchase_date = re.findall(r'\d{2}/\d{2}/\d{2}', text_dump[index])[0]
                purchase_date = purchase_date.split('/')
                self.payload['purchase_date'] = [purchase_date[2] + '/' + purchase_date[0] + '/' + purchase_date[1]]
                self.payload['purchase_time'] = re.findall(r'\d{2}:\d{2}:\d{2}', text_dump[index])
            
            if 'tc#' in text_dump[index].lower() or '1c#' in text_dump[index].lower() or 'tc:' in text_dump[index].lower():
                if '#' in text_dump[index]:
                    transaction_id_dump = re.split(r'#', text_dump[index])
                elif ':' in text_dump[index]:
                    transaction_id_dump = re.split(r':', text_dump[index])
                self.transaction_id = transaction_id_dump[1].replace(' ', '')        
            
        index = 0

        # items_dump -> contains just the receipt item data
        while index < len(items_dump):
            sku_code = re.findall(r'\d{12}', items_dump[index])[0]   
            # Skip items that are voided
            if sku_code in voided_index:
                if 'produce' in row[1].lower():
                    index += 2
                else:
                    index += 1
                continue

            row = re.split(r'\d{12}', items_dump[index])

            product_details['sku_code'] = sku_code
            product_details['name'] = row[0]

            # For items which contain produce, the price and other details are present on line 2
            if 'produce' in row[1].lower():
                produce_dump = re.split(r'lb', items_dump[index + 1])
                
                result = re.sub('[^0-9]','.', produce_dump[0].split()[0])
                product_details['quantity'] = float(result)
                
                product_details['price'] = float(re.findall(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{0,3})', produce_dump[-1])[-1])
                product_details['price'] = float("{0:.2f}".format(product_details['price']))
                index += 1


            else :
                product_details['quantity'] = 1
                price = re.findall(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{0,3})', row[1])
                if len(price) > 0:
                    product_details['price'] = float(re.findall(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{0,3})', row[1])[0])
                    product_details['price'] = float("{0:.2f}".format(product_details['price']))
                else: 
                    product_details['price'] = float(0)
                

            # Correcting the wrong data with product lookup  
            if sku_code in product_details_dict: 
                product_reference = product_details_dict.get(sku_code)
                product_details['name'] = product_reference['name']
                if product_details['quantity'] == 1 and 'produce' not in row[1].lower():
                    if 'price' in product_reference and product_details['price'] != product_reference['price']:
                        product_details['price'] = product_reference['price']
                product_details['category'] = product_reference['category']
            else:
                product_details['category'] = 'default'

            # If item already exists, update the quantity and price 
            if product_details['sku_code'] in items:
                dict_record = items.get(product_details['sku_code'])
                dict_record[3] += 1
                dict_record[2] += float(dict_record[2])
                items[product_details['sku_code']] = dict_record
            # If does not exist, Insert the item
            else:
                self.sku_codes.append(product_details['sku_code'])
 
                items[product_details['sku_code']] = [
                    product_details['sku_code'],
                    product_details['name'], 
                    product_details['price'], 
                    product_details['quantity'],
                    product_details['category']
                ]
                
            product_details['price'] = [-1]
            product_details['quantity'] = [1]
            product_details['category'] = 'default'
            index += 1

        # Write the product details into a final payload
        for key, value in items.items():
            self.items.append(value)
        

def getText(path, user_id): 
    
    image_object = process_image(path)
    image_object.process_image()
    image = image_object.get_image()   
    # Padding the rows in the image
    t = []

    # Row Operations
    final_rows = []
    for i in range(image.shape[0]):
        t.append(np.sum(image[i]))
        
    MAX_ROW_VALUE = max(t) - (max(t) * 0.05)

    count = 0

    for i in range(len(t)):
        if t[i] >= MAX_ROW_VALUE:
            final_rows.append(image[i])
            final_rows.append(image[i])
        final_rows.append(image[i])

    final_image = np.array(final_rows)

    # OCR Operations
    ocr_object = detect_text(final_image)
    id, receipt_details, sku_codes, items = ocr_object.get_text()
    return id, receipt_details, sku_codes, items


def main():
   

    image_paths = [
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts/IMG_0802.jpeg', 
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts/IMG_0803.jpeg', 
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts/IMG_0804.jpeg', 
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts/IMG_0808.jpeg', 
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts/IMG_0809.jpeg', 
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts/IMG_0874.jpeg',
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts_walmart/img1.jpeg',
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts_walmart/img2.jpeg',
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts_walmart/img3.jpeg',
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts_walmart/img4.jpeg',
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts_walmart/img5.jpeg',
        '/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts_walmart/img6.jpeg',
        

    ]
    for item in image_paths:
        start = time.time()

        print (item, '\n\n')

        image_object = process_image(item)
        #image_object = process_image('/Users/bhavish96.n/Projects/Expense-Tracker/images/receipts/IMG_0874.jpeg')
        
        image_object.process_image()
        image = image_object.get_image()   
        

        
        # Padding the rows in the image
        t = []

        # Row Operations
        final_rows = []
        for i in range(image.shape[0]):
            t.append(np.sum(image[i]))
            
        MAX_ROW_VALUE = max(t) - (max(t) * 0.05)

        count = 0

        for i in range(len(t)):
            if t[i] >= MAX_ROW_VALUE:
                final_rows.append(image[i])
                final_rows.append(image[i])
            final_rows.append(image[i])

        final_image = np.array(final_rows)
        
        ocr_object = detect_text(final_image)
        id,  receipt_details, sku_codes, items = ocr_object.get_text()
        print ('Receipt Id:', id, '\n')
        print ('Items:', items, '\n')
        end = time.time()
        print('Runtime:', end - start, '\n\n')

if __name__ == '__main__':
    main()



