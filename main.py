import csv
import urllib
from urllib.parse import urljoin

import click
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://rabota.ua'
city_ru = 'киев'
city_encoded = urllib.parse.quote_plus(city_ru)
position = 'junior-python'


def get_soup(response):
    return BeautifulSoup(response.text, 'lxml')


def get_links_on_page(page_link):
    response = requests.get(page_link)
    soup = get_soup(response)
    offers = soup.find_all('h2', class_='card-title')
    links = []
    for offer in offers:
        details_tag = offer.find('a', class_='ga_listing')
        details_link = details_tag.attrs['href']
        links.append(details_link)
    return links


def process_offer(writer, offer_link):
    response = requests.get(offer_link)
    soup = get_soup(response)

    title_tag = soup.find('h1')
    title = title_tag.get_text()

    company_tag = soup.find('h2')
    company = company_tag.get_text()

    published_tag = soup.find('h3')
    published = published_tag.get_text().split('- ')[1]

    link = offer_link

    writer.writerow({
        'Title': title,
        'Company': company,
        'Published': published,
        'URL': link,
    })


def write_to_csv_file(filename, links):
    with open(filename, mode='w') as f:
        header = ['Title', 'Company', 'Published', 'URL']
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for link in links:
            process_offer(writer, urljoin(BASE_URL, link))


@click.command()
@click.option('-role', type=str)
@click.option('-city', type=str, default=city_encoded)
def main(role, city):
    city = urllib.parse.quote_plus(city)
    url_position = urljoin(BASE_URL, f'/zapros/{role}' + '/')
    url = urljoin(url_position, city + '/')

    links = get_links_on_page(url)

    filename = f'{position}.csv'
    write_to_csv_file(filename, links)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

