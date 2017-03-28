# club-net
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

## Description
A managerial networking product for clubs operating in an educational institute

## Installation Instructions
* Clone the repo using ```git clone https://github.com/mani-shailesh/clubnet.git```
* ```cd clubnet```
* ```pip install -r requirements.txt```
* Make a copy of ```credentials.py``` in the same folder as credentials.py.template and fill in the credentials. <br />
**NOTE : Do not push ```credentials.py``` in the repo. It should be restricted for your personal use only.**
* Make a database with the name ```clubnet_db``` in MySQL.
* ```python manage.py migrate```
* ```python manage.py runserver```
* Type ```http://localhost:8000/clubs/``` to check if it's working!

