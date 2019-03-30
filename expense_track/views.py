from django.shortcuts import render, HttpResponseRedirect
from django.conf import settings
import datetime

# Create your views here.
def home_page(request): 
    return render(request, 'home.html', context= {
        'sidebar': True
    })


# User Home
def user_home(request):
    try: 
        user_details = {
            'user_id': request.session['user_id'],
            'firstName': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['firstName'],
            'lastname': settings.FIREBASE_DATABASE.child('users').child(request.session['user_id']).child('details').get().val()['lastName']
        }
    except:
        return HttpResponseRedirect('/')
    

    # Variables

    expenditure_split_up = {
        'current_week': [],
        'previous_week': [],
        'current_month': [],
        'previous_month': [],
        'current_year': [],
        'previous_year': []
    }

    items_index = {
        'max_range': [],
        'year': [],
        'month': [], 
        'week': []
    }

    current_spending = []
    previous_spending = []

    firebase_receipts = settings.FIREBASE_DATABASE.child('user_receipts').child(user_details['user_id']).get().val()
    if firebase_receipts != None:
        user_receipts = []
        for key, value in firebase_receipts.items():
            
            user_receipts.append([
                key, 
                value['vendor'], 
                float("{0:.2f}".format(float(value['total']))), 
                value['purchase_date']
            ])

        # Generating key for current week
        now = datetime.datetime.now()
        year = int(now.strftime("%y"))
        month = int(now.strftime("%m"))
        day = int(now.strftime("%d"))

        week = datetime.date(year, month, day).isocalendar()[1]
        current_week = str(week)
        current_month = str(month)
        current_year = str(year)
        
        
        # Querying the Database
        expenditure_overview = settings.FIREBASE_DATABASE.child('user_expenditure_legend').child(user_details['user_id']).get().val()
        expenditure_overview['total'] = float("{0:.2f}".format(float(expenditure_overview['total'])))
        for key, value in expenditure_overview['category_total'].items():
            expenditure_overview['category_total'][key] = float("{0:.2f}".format(float(value)))        
        
        '''
            Week Operations 
        '''

        if week - 1 >= 1:
            previous_week = str(week - 1)
            month_previous_week = current_month
            year_previous_week = current_year
        else:
            previous_week = str(54)
            month_previous_week = str(12)
            year_previous_week = str(year - 1)

        # Current Week Spendings
        current_week = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(current_year).child(current_month).child(current_week).child('category_total').get().val()
        # Previous Week Spendings
        previous_week = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year_previous_week).child(month_previous_week).child(previous_week).child('category_total').get().val()
        
        if current_week == None:
            current_week = {}
        if previous_week == None:
            previous_week = {}
        
        week_index = set(current_week.keys() if current_week != None else ()).union(previous_week.keys() if previous_week != None else ())
        items_index['week'] = week_index
        
        for index in week_index:
            if index not in current_week:
                current_spending.append(0)
            else:
                current_spending.append(float("{0:.2f}".format(float(current_week[index]))))
            
            if index not in previous_week:
                previous_spending.append(0)
            else:
                previous_spending.append(float("{0:.2f}".format(float(previous_week[index]))))

        expenditure_split_up['current_week'] = list(zip(items_index['week'], current_spending))
        expenditure_split_up['previous_week'] = list(zip(items_index['week'], previous_spending))
        
        

        ''' 
            Month Operations
        '''
        
        current_spending = []
        previous_spending = []

        if month - 1 >= 1:
            previous_month = str(month - 1)
            previous_month_year = current_year
        else:
            previous_month_year = str(year - 1)
            previous_month = str(12)

        # Current Month Spending
        current_month  = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(current_year).child(current_month).child('category_total').get().val()
        # Previous Month Spending
        previous_month = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(previous_month_year).child(previous_month).child('category_total').get().val()
        
        

        month_index = set(current_month.keys() if current_month != None else ()).union(previous_month.keys() if previous_month != None else ())
        items_index['month'] = month_index

        if current_month == None:
            current_month = {}
        if previous_month == None:
            previous_month = {}

        for index in month_index:
            if index not in current_month:
                current_spending.append(0)
            else:
                current_spending.append(float("{0:.2f}".format(float(current_month[index]))))
            
            if index not in previous_month:
                previous_spending.append(0)
            else:
                previous_spending.append(float("{0:.2f}".format(float(previous_month[index]))))

        expenditure_split_up['current_month'] = list(zip(items_index['month'], current_spending))
        expenditure_split_up['previous_month'] = list(zip(items_index['month'], previous_spending))
        
       
        '''
            Year Operations
        '''
        current_spending = []
        previous_spending = []

        # Current Year Spending
        current_year = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(current_year).child('category_total').get().val()       
        # Previous Year Spending
        previous_year = settings.FIREBASE_DATABASE.child('user_expenditure').child(user_details['user_id']).child(year - 1).child('category_total').get().val()
        
        year_index = set(current_year.keys() if current_year != None else ()).union(previous_year.keys() if previous_year != None else ())
        items_index['year'] = year_index

        print (current_month, '\n', current_week, '\n', current_year, '\n', previous_month, '\n', previous_year, '\n', previous_week)

        if current_year == None:
            current_year = {}
        if previous_year == None:
            previous_year = {}


        for index in year_index:
            if index not in current_year:
                current_spending.append(0)
            else:
                current_spending.append(float("{0:.2f}".format(float(current_year[index]))))
            
            if index not in previous_year:
                previous_spending.append(0)
            else:
                previous_spending.append(float("{0:.2f}".format(float(previous_year[index]))))

        expenditure_split_up['current_year'] = list(zip(items_index['year'], current_spending))
        expenditure_split_up['previous_year'] = list(zip(items_index['year'], previous_spending))
        
        return render(request, 'userHome.html', context={
            'userDetails': user_details, 
            'userReceipts': user_receipts,
            'expenditureOverview': expenditure_overview,
            'expenditureSplitUp': expenditure_split_up, 
            'itemsIndex': items_index,
        })

    return render(request, 'userHome.html', context={
        'userDetails': user_details, 
    })
    


# Test Modules
def test(request):
    return HttpResponseRedirect('/userHome')
        