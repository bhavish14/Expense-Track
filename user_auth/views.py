from django.shortcuts import render, HttpResponseRedirect
import pyrebase
from django.conf import settings
from django.contrib import auth



# User Sign In
def sign_in(request): 
    if request.method == 'POST':
        email = request.POST.get('emailField')
        password = request.POST.get('passwordField')
        try:
            user = settings.FIREBASE_AUTH.sign_in_with_email_and_password(email, password)
            request.session['uid'] = str(user['idToken'])
            request.session['user_id'] = str(user['localId'])
            print (request.session['user_id'])
            return HttpResponseRedirect('/userHome/')
        except:
            message = 'Invalid Credentials! Please check your username and password'
            return render(request, 'user/signIn.html', context={'message': message, 'sidebar': True})  
    return render(request, 'user/signIn.html', context={'sidebar': True})


# User Sign Up
def sign_up(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstNameField')
        last_name = request.POST.get('lastNameField')
        email = request.POST.get('emailField')
        password = request.POST.get('passwordField')

        try:
            
            # Creating User Account
            user = settings.FIREBASE_AUTH.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            user_details = {
                'firstName': first_name, 
                'lastName': last_name,
                'account_status': 1
            }

            settings.FIREBASE_DATABASE.child('users').child(user_id).child('details').set(user_details)

            # Logging in the user
            user = settings.FIREBASE_AUTH.sign_in_with_email_and_password(email, password)
            request.session['uid'] = str(user['idToken'])
            request.session['user_id'] =  str(user['localId'])       
            return HttpResponseRedirect('/userHome/')
        except:
            message = 'UserName Already Exists! Please change'
            return render(request, 'user/signUp.html', context={'message': message, 'sidebar': True})  

    return render(request, 'user/signUp.html', context = {'sidebar': True})

# User Logout
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

