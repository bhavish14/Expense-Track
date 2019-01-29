
import pyrebase

# Firebase settings
config = {    
    'apiKey': "AIzaSyCO8YUAAt30zXH-STsURBlS4SvGEKhfFdo",
    'authDomain': "expense-track-io.firebaseapp.com",
    'databaseURL': "https://expense-track-io.firebaseio.com",
    'projectId': "expense-track-io",
    'storageBucket': "expense-track-io.appspot.com",
    'messagingSenderId': "324272958377" 
}

FIREBASE_APP_INIT = pyrebase.initialize_app(config)
FIREBASE_APP_AUTH = FIREBASE_APP_INIT.auth()
FIREBASE_APP_DATABASE = FIREBASE_APP_INIT.database()
