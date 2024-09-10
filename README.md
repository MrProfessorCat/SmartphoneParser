# SmartphoneParser

##### SmartphoneParser is a python script for collecting statistics of the most popular smartphone operating systems on the Ozon market. As a result it creates .csv file with statistic.
[http://84.252.142.175/redoc/](http://84.252.142.175/redoc/)
### TECH

* [Python 3.11.4](https://www.python.org/)
* [Scrapy 2.11.2](https://scrapy.org/)
* [Selenium 4.24.0](https://www.selenium.dev/)
* [webdriver-manager 4.0.2](https://pypi.org/project/webdriver-manager/)
* [SQLAlchemy 2.0.34](https://www.sqlalchemy.org/)


## Features

SmartphoneParser provides two spiders for crawling. 
- phones_spider
- sel_phones_spider (uses selenium for dynamic pages)

## Installation

Clone projects

```sh
git clone git@github.com:MrProfessorCat/SmartphoneParser.git
```


Inside SmartphoneParser directory create and activate python virtual environment

```sh
python -m venv venv
```

* if Windows

    ```
    .\venv\Scripts\activate.bat
    ```

* if Linux

    ```
    source venv/Scripts/activate
    ```

Upgrade pip

```sh
python -m pip install --upgrade pip
```

Install dependencies from requirements.txt

```sh
pip install -r requirements
```

In phone_parser project run one of the spiders

```sh
cd phone_parser
scrapy crawl sel_phone_spide
```
