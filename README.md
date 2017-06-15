# Parladata

Parladata serves as the primary Popolo-compliant database and API for parliamentary data. In an ideal world, this is what our government would provide.

## Parladata API

The Parladata API serves data as scraped from www.dz-rs.si. It creates a faithful copy, so mistakes in the original dataset will be present in Parladata. There might be mistakes in the parsed data. If you find any mistakes, please submit an issue. The most common mistake is wrongly assigning a speech to a person with a similar/same name. The API is divided into three main endpoints, p, pg, and s for MPs, parties (parliamentary groups), and sessions respectively.

### API documentation

https://dev.parlameter.si/doc/parladata

## Installation

This is your typical Django app. Copy `settings.sample.py` to `settings.py` and edit accordingly. After you're set up and you've installed all the requirements (we suggest you use `virtualenv` and `pip`) run `python manage.py runserver` and enjoy.

## Bug reports and feature requests

Please submit an issue if you find anything out of order or wish for anything to happen.

