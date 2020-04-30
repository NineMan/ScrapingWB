# scraping Wildberries site for Brandquad

# Python Junior Developer test case

scraping category "Сноубутсы женские" in Moscow:

https://www.wildberries.ru/catalog/obuv/zhenskaya/dutiki-i-snoubutsy/snoubutsy

Tested with Python 3.6.9 and Scrapy 2.1.0 via virtual environment:
# Setup

$ python3.6 -m venv venv

$ source venv/bin/activate

$ pip install -r requirements.txt

$ scrapy crawl wild -o output.json

Result:

cat output.json
