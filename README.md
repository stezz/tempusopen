# Tempusopen records

A simple scraper to get times of swimmers out of [tempusopen.fi](tempusopen.fi)

    pipenv install

or 

    pip install Pipfile

then 
    
    mv settings_example.py to settings.py

configure there the names of the swimmers you want to find

    swimmers = [
    # Add here the list of swimmers you are interested in scraping
    {'firstname': 'John', 'lastname': 'Doe', 'team': 'Celtics'},
    ]
and then run

    scrapy crawl records_spider

And you will get out a list of all the times per style of the given swimmer(s)
