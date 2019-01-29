from django.shortcuts import render, HttpResponseRedirect
import pyrebase
from django.conf import settings
from django.contrib import auth
from django.core.files.storage import FileSystemStorage

from expense_module.imageToText import *
from django.conf import settings

import datetime


'''
    to do list:
        - seperate the database module from the receipt processing module. 
        - write modules for updating the json file (done)


'''


# User Receipt Operations
def add_new_expense(request):
    try: 
        user_details = {
            'user_id': request.session['user_id'],
            'firstName': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['firstName'],
            'lastname': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['lastName']
        }
    except:
        return HttpResponseRedirect('/')
    
    print (user_details)
    if request.method == 'POST' and request.FILES['imageFile']:
        myfile = request.FILES['imageFile']
        fs = FileSystemStorage()
        filename = user_details['user_id'] + '-' + myfile.name
        filename = fs.save(filename, myfile)
        #uploaded_file_url = fs.url(filename)
        request.session['image_url'] = filename
        return HttpResponseRedirect('processReceipt')
    return render(request, 'expense_module/addNewExpense.html', context={'userDetails': user_details})

def process_receipt(request):

    try: 
        user_details = {
            'user_id': request.session['user_id'],
            'firstName': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['firstName'],
            'lastname': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['lastName']
        }
    except:
        return HttpResponseRedirect('/')        
        
    
    if request.method == 'POST':       
        # Note: Firebase Doesn't allow access to user_id.receipt
        
        firebase_receipt_data = settings.FIREBASE_DATABASE.child('user_receipts').child(user_details['user_id']).child(request.POST.get('receiptId')).get().val()
        
        if firebase_receipt_data == None:
            # Building the json
            items = {}
            # Final receipt json
            receipt = {
                'vendor': request.POST.get('vendor'),
                'receipt_id': request.POST.get('receiptId'),
                'purchase_date': request.POST.get('purchaseDate'),
                'purchase_time': request.POST.get('purchaseTime'),
                'total': request.POST.get('total'),
                'no_items': request.POST.get('numItems')
            }
            # Category wise expenditure
            expenditure = {}
            

            for item in request.session['sku_codes']:
                category = request.POST.get(item + '-category')
                
                if category in items:
                    expenditure[category] += float(request.POST.get(item + '-Price'))
                    items[category][item] = [
                        request.POST.get(item + '-Name'), 
                        request.POST.get(item + '-Price'),
                        request.POST.get(item + '-Quantity')   
                    ]
                else:
                    items[category] = {}
                    expenditure[category] = float(request.POST.get(item + '-Price'))
                    items[category][item] = [
                        request.POST.get(item + '-Name'), 
                        request.POST.get(item + '-Price'),
                        request.POST.get(item + '-Quantity')                    
                    ]

            receipt['products'] = items
            
            firebase_receipt_data = receipt
            settings.FIREBASE_DATABASE.child('user_receipts').child(user_details['user_id']).child(receipt['receipt_id']).set(receipt)
            # Writing the receipt into Firebase


            # Writing User Expenditure Legend into Firebase
            user_expenditure = settings.FIREBASE_DATABASE.child('user_expenditure_legend').child(user_details['user_id']).get().val()
            if user_expenditure == None:
                user_expenditure = {
                    'total': float(receipt['total']),
                    'category_total': expenditure
                }
                settings.FIREBASE_DATABASE.child('user_expenditure_legend').child(user_details['user_id']).set(user_expenditure)
            else: 
                user_expenditure['total'] += float(receipt['total'])
                for key, value in expenditure.items():
                    if key in user_expenditure['category_total']:
                        user_expenditure['category_total'][key] += value
                    else:
                        user_expenditure['category_total'][key] = value
                settings.FIREBASE_DATABASE.child('user_expenditure_legend').child(user_details['user_id']).set(user_expenditure)

                            
            
            # Writing User Expenditure into Firebase
            # Processing Date
            purchase_date = receipt['purchase_date']
            purchase_date = purchase_date.split('/')
            t = datetime.date(int(purchase_date[0]), int(purchase_date[1]), int(purchase_date[2]))
            key = str((t.day - 1) // 7 + 1)
            year = str(t.year).lstrip('0')
            month = str(t.month).lstrip('0')

            # Hierachy user_expenditure: { year: { month: { week: { list }}}}
            weekly_expenditure = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).get().val()
            yearly_expenditure = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).get().val()
            year_set_param = False


            # Setting Weekly Expenditure
            if weekly_expenditure == None:
                weekly_expenditure = {
                    'category_total': expenditure,
                    'receipts': [
                    receipt['receipt_id']
                    ],
                    'vendors': {
                        receipt['vendor']: float(receipt['total'])
                    }
                }    
                settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).set(weekly_expenditure)
                if yearly_expenditure == None:
                    year_set_param = True
                    yearly_expenditure = {
                        'category_total': expenditure,
                        'vendors': {
                            receipt['vendor']: float(receipt['total'])
                        }
                    }
                    settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).update(yearly_expenditure)
            else:
                category_total = weekly_expenditure['category_total']
                receipt_log = weekly_expenditure['receipts']
                receipt_log.append(receipt['receipt_id'])
                weekly_expenditure['vendors'][receipt['vendor']] += float(receipt['total'])
                for expenditure_key, value in expenditure.items():
                    if expenditure_key in category_total:
                        category_total[expenditure_key] += value
                    else:
                        category_total[expenditure_key] = value
                
                settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).set(weekly_expenditure)
            
            # Setting Monthly Expenditure
            monthly_expenditure = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).get().val()
            
            if 'category_total' not in monthly_expenditure:
                monthly_expenditure['category_total'] = {}

            if 'vendors' not in monthly_expenditure:
                monthly_expenditure['vendors'] = {
                    receipt['vendor']: 0
                }

            # Category Split-up
            category_total = monthly_expenditure['category_total']
            for expenditure_key, value in expenditure.items():
                if expenditure_key in category_total:
                    category_total[expenditure_key] += value
                else:
                    category_total[expenditure_key] = value
            
            monthly_expenditure['category_total'] = category_total
            
            # Vendor Split-up
            vendor_total = monthly_expenditure['vendors']
            vendor_total[receipt['vendor']] += float(receipt['total'])

            monthly_expenditure['vendors'] = vendor_total
            settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).set(monthly_expenditure)
            
            '''
                Note: User yearly_expenditure[1] to get rid of None in the dict.
            '''
            if not year_set_param:            
                # Setting Yearly Expenditure
                yearly_expenditure = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).get().val()
            
                # Category Split-up
                category_total = yearly_expenditure['category_total']
                for expenditure_key, value in expenditure.items():
                    if expenditure_key in category_total:
                        category_total[expenditure_key] += value
                    else:
                        category_total[expenditure_key] = value
                
                # Vendor Split-up
                vendor_total = yearly_expenditure['vendors']
                vendor_total[receipt['vendor']] += float(receipt['total'])
                settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).update({
                    'category_total': category_total, 
                    'vendors': vendor_total
                })
                
            # Updating the json file
            update_product_details(receipt)


        else:
            message = 'receipt already exists'
        
        return HttpResponseRedirect('/userHome/')
    else:        
        image_path = settings.MEDIA_ROOT + '/' + request.session['image_url']

        receipt_id, receipt_details, sku_codes, receipt_items = getText(image_path, user_details['user_id'])

        # Setting session variables with the receipt details
        request.session['sku_codes'] = sku_codes
        request.session['receipt_id'] = receipt_id
        request.session['receipt_details'] = receipt_details

        return render(request, 'expense_module/viewExpenses.html', context={
            'userDetails': user_details, 
            'receiptId': receipt_id,
            'receiptDetails': receipt_details, 
            'receiptItems': receipt_items,
            'sku_codes': sku_codes,
        })
    
def view_receipt(request, receipt_id):
    try: 
        user_details = {
            'user_id': request.session['user_id'],
            'firstName': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['firstName'],
            'lastname': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['lastName']
        }
    except:
        return HttpResponseRedirect('/')        
    receipt_details = settings.FIREBASE_DATABASE.child('user_receipts').child(user_details['user_id']).child(receipt_id).get().val()

    return render(request, 'expense_module/viewReceipts.html', context = {
        'userDetails': user_details,
        'receipt': receipt_details
    })

def delete_receipt(request, receipt_id):
    try: 
        user_details = {
            'user_id': request.session['user_id'],
            'firstName': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['firstName'],
            'lastname': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['lastName']
        }
    except:
        return HttpResponseRedirect('/')        
    
    
    receipt_details = settings.FIREBASE_DATABASE.child('user_receipts').child(user_details['user_id']).child(receipt_id).get().val()

    if receipt_details == None:
        return render(request, 'userHome.html', context={
            'messageError': 'Receipt Not Found'
        })

    category_sum = {
    }

    for category, items in receipt_details['products'].items():
        for sku, details in items.items():
            if category not in category_sum:
                category_sum[category] = float(details[1])
            else:
                category_sum[category] += float(details[1])

    print (category_sum)

    purchase_date = receipt_details['purchase_date']
    purchase_date = purchase_date.split('/')
    t = datetime.date(int(purchase_date[0]), int(purchase_date[1]), int(purchase_date[2]))
    key = str((t.day - 1) // 7 + 1)
    year = str(t.year).lstrip('0')
    month = str(t.month).lstrip('0')

    # Weekly log
    weekly_expenditure_category = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).child('category_total').get().val()
    weekly_expenditure_vendors = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).child('vendors').get().val()
    weekly_expenditure_receipts = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).child('receipts').get().val()

    # Monthly Log
    monthly_expenditure_category = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child('category_total').get().val()
    monthly_expenditure_vendors = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child('vendors').get().val()
    
    # Yearly Log
    yearly_expenditure_category = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child('category_total').get().val()
    yearly_expenditure_vendors = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child('vendors').get().val()
    

    print ('weekly before: ', weekly_expenditure_category, '\n', weekly_expenditure_vendors, '\n', weekly_expenditure_receipts,'\n')
    print ('monthly before: ', weekly_expenditure_category, '\n', weekly_expenditure_vendors, '\n')
    print ('yearly before: ', yearly_expenditure_category, '\n', yearly_expenditure_vendors, '\n')


    for category, total in category_sum.items():
        weekly_expenditure_category[category] -= float(total)
        monthly_expenditure_category[category] -= float(total)
        yearly_expenditure_category[category] -= float(total)
    
    weekly_expenditure_vendors[receipt_details['vendor']] -= float(receipt_details['total'])
    weekly_expenditure_receipts.remove(receipt_details['receipt_id'])

    monthly_expenditure_vendors[receipt_details['vendor']] -= float(receipt_details['total'])

    yearly_expenditure_vendors[receipt_details['vendor']] -= float(receipt_details['total'])


    print ('weekly after: ', weekly_expenditure_category, '\n', weekly_expenditure_vendors, '\n', weekly_expenditure_receipts, '\n')
    print ('monthly after: ', monthly_expenditure_category, '\n', monthly_expenditure_vendors, '\n')
    print ('yearly after: ', yearly_expenditure_category, '\n', yearly_expenditure_vendors, '\n')


    # Setting Values

    # Weekly
    settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).child('category_total').set(weekly_expenditure_category)
    settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).child('vendors').set(weekly_expenditure_vendors)
    settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child(key).child('receipts').set(weekly_expenditure_receipts)


    # Monthly
    settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child('vendors').set(monthly_expenditure_category)
    settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child(month).child('vendors').set(monthly_expenditure_vendors)

    # Yearly
    settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child('category_total').set(yearly_expenditure_category)
    settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year).child('vendors').set(yearly_expenditure_vendors)
    
    # Removing Receipt
    settings.FIREBASE_DATABASE.child('user_receipts').child(user_details['user_id']).child(receipt_id).remove()
    return HttpResponseRedirect('/userHome')

'''
    Utility functions
'''

# Update Product Details
def update_product_details(receipt):
    print ('update product details')
    directory = os.getcwd()
    json_file_path = directory + '/expense_module/product_lookup.json'


    json_file = open(json_file_path, 'r')
    product_details_dict = json.load(json_file)

    # Categories of the products {hierachy is categories: {sku_code: {}} }
    for category, record in receipt['products'].items():
        for key, value in record.items():
            if key not in product_details_dict:
                item_dump = {
                    'name': value[0], 
                    'category': category
                }
                if '.' not in value[2]:
                    item_dump['price'] = float(value[1]) / float(value[2])
                    item_dump['price'] = float("{0:.2f}".format(item_dump['price'])) 
                product_details_dict[key] = item_dump

    
    json_file_path = directory + '/expense_module/product_lookup.json'
    json_file = open(json_file_path, 'w')
    json.dump(product_details_dict, json_file)


def test(request): 
    if request.method == 'POST':
        user_details = {
            'user_id': request.session['user_id'],
            'firstName': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['firstName'],
            'lastname': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['lastName']
        }

        
        
        
        # Note: Firebase Doesn't allow access to user_id.receipt
    
        # Building the json
        items = {}
        # Final receipt json
        receipt = {
            'vendor': request.POST.get('vendor'),
            'receipt_id': request.POST.get('receiptId'),
            'purchase_date': request.POST.get('purchaseDate'),
            'purchase_time': request.POST.get('purchaseTime'),
            'total': request.POST.get('total'),
            'no_items': request.POST.get('numItems')
        }
        # Category wise expenditure
        expenditure = {}
        

        for item in request.session['sku_codes']:
            category = request.POST.get(item + '-category')
            
            if category in items:
                expenditure[category] += float(request.POST.get(item + '-Price'))
                items[category][item] = [
                    request.POST.get(item + '-Name'), 
                    request.POST.get(item + '-Price'),
                    request.POST.get(item + '-Quantity')   
                ]
            else:
                items[category] = {}
                expenditure[category] = float(request.POST.get(item + '-Price'))
                items[category][item] = [
                    request.POST.get(item + '-Name'), 
                    request.POST.get(item + '-Price'),
                    request.POST.get(item + '-Quantity')                    
                ]

        receipt['products'] = items
        
        
        # Updating the json file
        update_product_details(receipt)
        
        
        image_path = '/Users/bhavish96.n/Documents/Projects/Django/expense_track/media/PeMoF8SoW5ZePPiWUsQVgVKHMC53-img6.png'
        receipt_id, receipt_details, sku_codes, receipt_items = getText(image_path, user_details['user_id'])

        # Setting session variables with the receipt details
        request.session['sku_codes'] = sku_codes
        request.session['receipt_id'] = receipt_id
        request.session['receipt_details'] = receipt_details

        return render(request, 'expense_module/viewExpenses.html', context={
            'userDetails': user_details, 
            'receiptId': receipt_id,
            'receiptDetails': receipt_details, 
            'receiptItems': receipt_items,
            'sku_codes': sku_codes,
        })
    else: 
        user_details = {
            'user_id': request.session['user_id'],
            'firstName': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['firstName'],
            'lastname': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['lastName']
        }
        image_path = '/Users/bhavish96.n/Documents/Projects/Django/expense_track/media/PeMoF8SoW5ZePPiWUsQVgVKHMC53-img6.png'
        receipt_id, receipt_details, sku_codes, receipt_items = getText(image_path, user_details['user_id'])

       

        # Setting session variables with the receipt details
        request.session['sku_codes'] = sku_codes
        request.session['receipt_id'] = receipt_id
        request.session['receipt_details'] = receipt_details


        return render(request, 'expense_module/viewExpenses.html', context={
            'userDetails': user_details, 
            'receiptId': receipt_id,
            'receiptDetails': receipt_details, 
            'receiptItems': receipt_items,
            'sku_codes': sku_codes,
        })

 
    





'''
    try: 
        user_details = {
            'user_id': request.session['user_id'],
            'firstName': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['firstName'],
            'lastname': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['lastName']
        }

        return render(request, 'expense_module/viewExpenses.html', context={'userDetails': user_details})
    except:
        return HttpResponseRedirect('/')
'''