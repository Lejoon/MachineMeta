#%%
# MTGGoldfish Scraper
import requests, bs4, lxml, re, os, errno, pandas as pd
from pathlib import Path
from collections import Counter
from string import digits

MTGSCRAPER_URL = "https://www.mtggoldfish.com"
ROOT_DIR = os.getcwd()

#%%
class Tournament: 
    def __init__(self, _decks, _name, _date, _format):
        self.counts = Counter([str(deck) for deck in _decks])
        self.decks = _decks
        self.name = _name
        self.date = _date
        self.format = _format
        self.size = len(_decks)
        
    def __str__(self):
        top_decks = ""
        
        for deck in self.counts.most_common():
            top_decks += deck[0] + ": " + str(deck[1]) + "\n"
            
        return self.name + '\n'  + self.date + '\n' + top_decks
    
    def __getitem__(self, item):
        return self.decks[item]
        
class Deck:
    def __init__(self, _name, _url, _player):
        self.name = _name
        self.url = _url
        self.player = _player
        
    def __str__(self):
        return self.name

def get_soup(_url):
    response_text = requests.get(_url).text
    return bs4.BeautifulSoup(response_text, "lxml")    

def fetch_tournament(_tournament):
    """
    Fetches a tournament from MTGGoldfish from the url:
    MTGSCRAPER_URL/tournament/_tournament#online
    """
    soup = get_soup(MTGSCRAPER_URL + "/tournament/" + _tournament + "#online")
    
    decks = [Deck(span.a.text, span.a['href'], span.find("a", href=re.compile("/player/")).text) for span in soup.findAll("tr", {"class": ["tournament-decklist-odd", "tournament-decklist-event"]})]
    name = soup.find("div", {"class": "col-md-12"}).h1.text.replace('\n', '')
    date = soup.find(text=re.compile("Date: ")).split("Date: ",1)[1].replace('\n', '')
    format = soup.find(text=re.compile("Format: ")).split("Format: ",1)[1].replace('\n', '')

    return Tournament(decks, name, date, format)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
        
def download_deck(_url,_format,_tournament):
    #TODO make it so that the soup is not fetched if file name already exists, use the os.path.isfile below
    link = MTGSCRAPER_URL + _url.replace('/deck', '/deck/download')
    print(link)
    response = requests.get(link).text
    
    deck_dir = ROOT_DIR + '/' + _format + '/' + _tournament
    mkdir_p(deck_dir)

    deckfile = deck_dir + '/' + re.findall("\d+", link)[0] + '.txt'

    if not os.path.isfile(deckfile):
        print(deckfile)
        with open(deckfile, 'a+') as f:
            f.write(response)

print('Done initializing classes')

#%%

tournament_list = ["pioneer-ptq-12038785",
                   "pioneer-ptq-12033252",
                   "pioneer-ptq-12033251",
                   "pioneer-ptq-12033250",
                   "pioneer-ptq-12033249",
                   "pioneer-ptq-12028088",
                   "pioneer-ptq-12033248",
                   "pioneer-ptq-12028087",
                   "pioneer-ptq-12028086",
                   "pioneer-ptq-12021797",
                   "pioneer-ptq-12014480",
                   "pioneer-ptq-12006968",
                   "pioneer-challenge-12038799",
                   "pioneer-challenge-12028101",
                   "pioneer-challenge-12021812",
                   "pioneer-challenge-12014495",
                   "pioneer-challenge-12006983",
                   "pioneer-challenge-12000548",
                   ]

rows = []

for page in tournament_list:
    tournament = fetch_tournament(page)
    
    
    for deck in tournament:
        deck_info = dict()
        deck_info['Deck'] = deck.name
        deck_info['Player'] = deck.player
        deck_info['URL'] = deck.url
        deck_info['Tournament'] = tournament.name
        deck_info['Date'] = tournament.date
        deck_info['Format'] = tournament.format
        deck_info['Size'] = tournament.size
        
        rows.append(deck_info)
        download_deck(deck.url, tournament.format, tournament.name)
        
    #print(rows)

df = pd.DataFrame(rows)
print('Done loading MTGGGoldfish data')
#%%
print(df)
print(df['URL'])

#%%
df.to_csv(ROOT_DIR + r'file.csv')

#%%
pd.set_option('display.max_rows', None)
df.groupby('Deck')['Player'].count()






#%%

url = MTGSCRAPER_URL + "/tournament/" + "pioneer-ptq-12038785 + "#online"
response_text = requests.get(url).text
soup = bs4.BeautifulSoup(response_text, "lxml")

print("Done reading soup document")

decks = [Deck(span.a.text, span.a['href'], span.find("a", href=re.compile("/player/")).text) for span in soup.findAll("tr", {"class": ["tournament-decklist-odd", "tournament-decklist-event"]})]
name = soup.find("div", {"class": "col-md-12"}).h1.text
date = soup.find(text=re.compile("Date: ")).split("Date: ",1)[1] 
format = soup.find(text=re.compile("Format: ")).split("Format: ",1)[1]

ptq1 = Tournament(decks, name, date, format)

print(ptq1)
#for deck in ptq1.decks:
#    print(deck)
print(ptq1.decks[0].player)

print([deck for deck in ptq1.counts.most_common(3)])

print(ptq1.date)
print(ptq1.format)
print(ptq1.name)
print(ptq1.total)
print(ptq1.counts)