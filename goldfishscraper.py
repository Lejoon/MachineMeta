#MTGGoldfish Scraper
import requests, bs4, lxml, re, os, errno
from pathlib import Path
from urlparse import urlparse, urljoin
from string import digits

MTGSCRAPER_URL = "https://www.mtggoldfish.com"
decks_dir = os.path.expanduser("~")+'/Documents'+'/Deck'

#Recursive MKDIR
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def recursive_search_format(format_url):
    response_text = requests.get(format_url).text
    soup = bs4.BeautifulSoup(response_text,"lxml")

    #Image with URL to deck archetypes
    table_f = soup.findAll("a", {"class": "card-image-tile-link-overlay"})

    all_links_f = [tag['href'] for tag in table_f]

    for link_f in all_links_f:

        urld = MTGSCRAPER_URL + link_f

        #Convert deck names from "modern-deck-name-######" to "deck-name"
        deck_name = link_f.split('/')[-1]
        deck_name = deck_name.replace("modern-","")
        deck_name = deck_name.translate(None,digits)
        deck_variant = deck_name[:-1]

        print(deck_variant)
        response_text = requests.get(urld).text
        soup = bs4.BeautifulSoup(response_text,"lxml")

        all_decks = [span.a for span in soup.findAll("span", {"class": "deck-price-online"})]

        all_links=[]

        for row in all_decks:
            if row is not None:
                deck_number = re.findall("\d+",row['href'])

                # Deck URL for download, eg /deck/download/NUMBER
                all_links.append('/deck/download/' + deck_number[0])


        for link in all_links:
             print(link)

             link2 = MTGSCRAPER_URL + link
             response_deck = requests.get(link2).text

             deck_dir = decks_dir + '/' + deck_format + '/' + deck_variant
             mkdir_p(deck_dir)

             deckfile = deck_dir + '/' + re.findall("\d+", link)[0] + '.txt'
             if not os.path.isfile(deckfile):
                 print(deckfile)
                 with open(deckfile, 'a+') as f:
                     f.write(response_deck)

format_list = ["Modern"]
for deck_format in format_list:
    url = MTGSCRAPER_URL + "/metagame/" + deck_format + "/full"
    recursive_search_format(url)
print('Done.')
