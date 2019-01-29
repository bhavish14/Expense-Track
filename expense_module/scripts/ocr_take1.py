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

        # Padding 
        self.add_space_image()
        
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

    '''
        Helper function
    '''

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

    def add_space_image(self):
        # Padding the rows in the image
        t = []

        # Row Operations
        final_rows = []
        for i in range(self.cropped_image.shape[0]):
            t.append(np.sum(self.cropped_image[i]))
            
        MAX_ROW_VALUE = max(t) - (max(t) * 0.05)

        count = 0

        for i in range(len(t)):
            if t[i] >= MAX_ROW_VALUE:
                final_rows.append(self.cropped_image[i])
                final_rows.append(self.cropped_image[i])
            final_rows.append(self.cropped_image[i])

        self.final_image = np.array(final_rows)
        
        # Padding the image with white background for 50px
        self.final_image = cv2.copyMakeBorder(self.final_image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255])

        # Resizing the final image
        self.final_image = cv2.resize(self.final_image, None, fx=0.5, fy=0.5)


    def get_image(self):
        # Returns the cropped image
        return self.final_image

class walmart:
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
        config = ('-l eng --oem 1 --psm 3')

        raw_text = pt.image_to_string(image, config=config)
        raw_text = raw_text.split('\n')
        
        self.get_items(raw_text)
        return self.transaction_id, self.payload, self.sku_codes, self.items
    
    def process_text_dump(self, text_dump):
        
        '''
            Local Vble Init.
        '''
        voided_index = []
        items_dump = []
        index = 0

        '''
            Precondition: The text recognized from the OCR is assumed to be split on '\n'. No preprocessing done.
            
            Loop Action: 
                - Recognizes the voided index, if any and appends it to a seperate list,
                - Determines the total spendings for the bill and appends it to the payload dict of the class,
                - Vendor is appended to the payload dict,
                - # of items sold is also appended,
                - Determines the produce items and appends a 'produce' tag at the end, 
                - Date and time of the purchase is added to the dict
                - Receipt ID is recognized and added. 
                - Populates an item dump with the details of all the items
            Note: 
                - All relevant fields are retrieved with the anchor keywords.
                - Voided SKUs are retrieved with the keyword 'voided' in the text line. 
                - While detecting the items, a regex is used for detecting the 12 digit long SKU. But, AID and REF 
                  have the same digit lengths. 
                - Receipt ID is detected using a regex for five four digit numbers. 
        '''
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
            
            if re.search(r'(\d{2}/\d{2}/\d{2})', text_dump[index]):
                purchase_date = re.findall(r'\d{2}/\d{2}/\d{2}', text_dump[index])[0]
                purchase_date = purchase_date.split('/')
                self.payload['purchase_date'] = [purchase_date[2] + '/' + purchase_date[0] + '/' + purchase_date[1]]

            # Purchase Time Extraction
            if re.search(r'(\d{2}:\d{2}:\d{2})', text_dump[index]):
                self.payload['purchase_time'] = re.findall(r'\d{2}:\d{2}:\d{2}', text_dump[index])
            
            # Receipt ID Extraction
            if len(re.findall(r"(?<!\d)\d{4}(?!\d)", text_dump[index])) == 5:
                tc_dump = re.findall(r"(?<!\d)\d{4}(?!\d)", text_dump[index])
                self.transaction_id = ''.join(tc_dump)
        
        return items_dump, voided_index

    def get_item_details(self, items_dump, voided_index):
        '''
            Local Vble Init
        '''
        index = 0
        product_details = {
            'name': '', 
            'sku_code': '',
            'price': [-1], 
            'category': '',
            'quantity': [1]
        }
        items = {}

        '''
            Precondition: The items_dump must contain the list of all items that are extracted in process_text_dump.

            Loop Action: 
                - Extracts the SKU code of the product from the text and looks for it in voided index list. 
                    + If an entry exists, the entire row is skipped. (for produce, two rows are skipped)
                - Extract the item Price and quantity.
                - Lookup the extracted data either in API or the dict and replace incorrect data. 
                - Populate a items dict with cleaned item data.
            
            Note: 
                - When extracting the price and quantity, two cases have to be considered. 
                    + For Produce, price and quantity is on the second line. 
                    + For Others, it is in the same line. 
                - By default, product quantity of Non-Produce items are set to 1.
                - In product lookup, price is omitted for the produce.
        '''

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

            # Extract the SKU code of the Product
            row = re.split(r'\d{12}', items_dump[index])
            product_details['sku_code'] = sku_code
            product_details['name'] = row[0]

            # For items which contain produce, the price and other details are present on line 2
            if 'produce' in row[1].lower():
                produce_dump = re.split(r'lb', items_dump[index + 1])
                result = re.sub('[^0-9]','.', produce_dump[0].split()[0])
                # Extract the quantity and convert it to float
                product_details['quantity'] = float(result)
                # Extract the price and convert it to float
                product_details['price'] = float(re.findall(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{0,3})', produce_dump[-1])[-1])
                product_details['price'] = float("{0:.2f}".format(product_details['price']))
                index += 1
            # Non-Produce items
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

        return items


    def get_items(self, text_dump):
        index = 0

        # Receipt Details Extraction
        items_dump, voided_index = self.process_text_dump(text_dump)
                
        # Item Details Extraction
        items = self.get_item_details(items_dump, voided_index)

        # Write the product details into a final payload
        for key, value in items.items():
            self.items.append(value)
        

def getText(path, user_id): 
    
    # Preprocessing the image
    image_object = process_image(path)
    image_object.process_image()
    final_image = image_object.get_image()  

    # OCR Operations
    ocr_object = walmart(final_image)
    id, receipt_details, sku_codes, items = ocr_object.get_text()
    return id, receipt_details, sku_codes, items


def main():
   

    image_paths = [
        # Camera Receipts
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
        # Preprocessing the image
        image_object = process_image(item)
        image_object.process_image()
        final_image = image_object.get_image()  

        # OCR Operations
        ocr_object = walmart(final_image)
        id, receipt_details, sku_codes, items = ocr_object.get_text()
        end = time.time()
        print (
            'Image: ', item, '\n\n',
            'Receipt Id: ', id, '\n\n', 
            'Receipt Details: ', receipt_details, '\n\n',
            'Items: ', items, '\n\n', 
            'Runtime:', end - start, '\n\n'
        )

if __name__ == '__main__':
    main()





'''
    Commented Code
'''
# Receipt ID
'''
    Rewritting TC# recognition
'''

'''
if 'tc#' in text_dump[index].lower() or '1c#' in text_dump[index].lower() or 'tc:' in text_dump[index].lower():
    if '#' in text_dump[index]:
        transaction_id_dump = re.split(r'#', text_dump[index])
    elif ':' in text_dump[index]:
        transaction_id_dump = re.split(r':', text_dump[index])
    self.transaction_id = transaction_id_dump[1].replace(' ', '')        
'''

'''
    Main function
'''

'''start = time.time()

    print (item, '\n\n')

    image_object = process_image(item)       
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
    
    # Padding the image with white background for 50px
    final_image = cv2.copyMakeBorder(final_image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    # Resizing the final image
    final_image = cv2.resize(final_image, None, fx=0.5, fy=0.5)

    ocr_object = detect_text(final_image)        
    id,  receipt_details, sku_codes, items = ocr_object.get_text()

    print ('Receipt Id:', id, '\n')
    print ('Items:', items, '\n')
    end = time.time()
    print('Runtime:', end - start, '\n\n')
    print (receipt_details)
'''