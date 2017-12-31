# focus 
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

## Description
A managerial networking product for clubs operating in an educational institute

## Setup Instructions

* Clone the repo using ```git clone https://github.com/mani-shailesh/focus.git```
* ```cd focus```
* ```pip install -r requirements.txt``` to install required python packages for the focus project. Before this, you may need to install ```pip``` and ```MySQL Server``` if you do not already have them. 
* Make a copy of ```credentials.py``` in the same folder as credentials.py.template and fill in the credentials. <br />
**NOTE : Do not push ```credentials.py``` in the repo. It should be restricted for your personal use only.**
* Make a database with the name ```focus_db``` in MySQL.
* Execute following commands in the given order:
    * ```python manage.py migrate``` to create required tables in your databse.
    * ```python manage.py createsuperuser``` to create a superuser for the application.
    * ```python manage.py runserver``` to run the local development server.
* Visit admin panel on your browser at ```http://localhost:8000/admin``` and login using the superuser credentials that you created in the previous step.
* Create new Social Application for enabling Facebook and Twitter login using
  your client_id and client_secret from corresponding service.
* Visit ```http://localhost:8000/docs/``` to check if it's working!
