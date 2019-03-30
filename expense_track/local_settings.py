
import pyrebase

# Firebase settings
config = {    
    'apiKey': "",
    'authDomain': "",
    'databaseURL': "",
    'projectId': "",
    'storageBucket': "",
    'messagingSenderId': "" 
}

FIREBASE_APP_INIT = pyrebase.initialize_app(config)
FIREBASE_APP_AUTH = FIREBASE_APP_INIT.auth()
FIREBASE_APP_DATABASE = FIREBASE_APP_INIT.database()
