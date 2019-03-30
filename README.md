# Expense-Track

A Django-based receipt expense tracker for managing expenses. The app extracts the details {Receipt Id, Purchase date and time, 
\# of items purchase, item details, total spending} from the receipt and pushes it into a Firebase-Based cloud storage. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

A step by step series of examples on how to get a development env running

```
cd <your-path>/Expense-Track
sudo pip3 install -r requirements.txt
python manage.py runserver
```

## Built With

* [Django](https://docs.djangoproject.com/en/2.1/) - The web framework used
* [Tesseract](https://opensource.google.com/projects/tesseract) - Open Source OCR for character recognition
* [PyreBase](https://github.com/thisbejim/Pyrebase) - Wrapper for Firebase API

## Authors

* **Bhavish Khanna narayanan** - *Initial work* - [bhavish14](https://github.com/bhavish14)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
