#%%
# MTGGoldfish Scraper
import requests, bs4, lxml, re, os, errno, dask, dask_ml, glob, pandas as pd
from pathlib import Path
from collections import Counter
from string import digits
import dask_ml.cluster


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
        
def download_deck(_id,_format,_tournament):
    #TODO make it so that the soup is not fetched if file name already exists, use the os.path.isfile below
    link = MTGSCRAPER_URL + '/deck/download/' + _id
    deck_dir = ROOT_DIR + '/' + _format + '/' + _tournament
    deckfile = deck_dir + '/' + _id + '.txt'
    
    if os.path.isfile(deckfile):
        return
    
    response = requests.get(link).text
    mkdir_p(deck_dir)

    if not os.path.isfile(deckfile):
        print(deckfile)
        with open(deckfile, 'a+') as f:
            f.write(response)

print('Done initializing classes')

#%%
#Imports the latest Pioneer decklists
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
                   "pioneer-challenge-12043463",
                   "pioneer-challenge-12038799",
                   "pioneer-challenge-12028101",
                   "pioneer-challenge-12021812",
                   "pioneer-challenge-12014495",
                   "pioneer-challenge-12006983",
                   "pioneer-challenge-12000548",
                   "pioneer-preliminary-12049217",
                   "pioneer-preliminary-12044998",
                   "pioneer-preliminary-12044995",
                   "pioneer-preliminary-12044981",       
                   "magicfest-oklahoma-2019-saturday-pioneer-ptq",
                   "magicfest-oklahoma-2019-friday-pioneer-ptq"
                   ]

rows = []

for page in tournament_list:
    tournament = fetch_tournament(page)
    
    
    for deck in tournament:
        deck_info = dict()
        deck_info['Deck'] = deck.name
        deck_info['Player'] = deck.player
        deck_info['ID'] = re.findall("\d+", deck.url)[0]
        deck_info['Tournament'] = tournament.name
        deck_info['Date'] = tournament.date
        deck_info['Format'] = tournament.format
        deck_info['Size'] = tournament.size
        
        rows.append(deck_info)
        download_deck(re.findall("\d+", deck.url)[0], tournament.format, tournament.name)
        
    print('Done importing ' + str(tournament))

df = pd.DataFrame(rows)
print('Done loading MTGGGoldfish data')

#%%
#Read file and tournament structure into a list of decklists.
deck_dir = ROOT_DIR + '/' + 'Pioneer' + '/'

main_path = glob.glob(deck_dir + "*")
tournament_dirs = []
decks = []

for path in main_path:
    #print(path)
    tournament_dirs.append(path)
    
for tournament_path in tournament_dirs:
    for filename in glob.glob(path + '/*'):
        #print(glob.glob(path))
        with open(filename,'r') as deck:
            decks.append(deck.read())
            

#split the decks into lines
for i,deck in enumerate(decks):
     decks[i] = deck.split('\n')
     decks[i] = list(filter(None, decks[i]))
    
     
#separate the number of apparitions from the card's name
for deck in decks:
     for i, card in enumerate(deck):
         quantity = int(card.split(' ')[0])
         card_name = ' '.join(card.split(' ')[1:])
         deck[i] = (quantity,card_name)

def card_names(a_deck):
    return [card[1] for card in a_deck]
  
all_card_names = []
for deck_card_names in [card_names(deck) for deck in decks]:
    all_card_names+=deck_card_names

    
print(len(all_card_names)) #21975
all_card_names = set(all_card_names) #make them unique
print(len(list(all_card_names))) #271


def deck_to_vector(deck):
    v = [0]*len(all_card_names)
    for i, name in enumerate(all_card_names):
        for number, card_name in deck:
            if card_name == name:
                v[i]+=number
    return v

deck_vectors = [deck_to_vector(deck) for deck in decks]



#print(decks)
    
print('Done reading files')
     #with open(filename,'r') as deck:
     #    decks.append(deck.read())

#%%
df.to_csv(ROOT_DIR + r'file.csv')
print('File saved to ' + ROOT_DIR + r'file.csv')


