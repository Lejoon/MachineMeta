#%%
# MTGGoldfish Scraper
import requests, bs4, lxml, re, os, errno, dask, glob, pandas as pd
from pathlib import Path
from collections import Counter
from string import digits

MTGSCRAPER_URL = "https://www.mtggoldfish.com"
ROOT_DIR = os.getcwd()
FILE_PATH = ROOT_DIR + '/' + r'Tournaments.csv'
SEP = ','

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
    """
    id only: Fetches deck from Tournament.csv file
    
    url, name, player: Fetches deck from MTGGoldfish
    """
    def __init__(self, name = '', url = '', player = '', id = ''):
        #If deck is 
        if not id:
            self.name = name
            self.url = url
            self.player = player
            
        if os.path.isfile(FILE_PATH):
            df = pd.read_csv(FILE_PATH, sep=SEP)   
            
            for idx,row in df.iterrows(): 
                if row["ID"] == id:
                    self.name = row["Deck"]
                    self.player = row["Player"]
                    self.url = MTGSCRAPER_URL + '/deck/download/' + str(id)
                    self.list = print_deck(id)
        
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
    
    print('importing ' + _tournament)
    
    decks = [Deck(name = span.a.text, url = span.a['href'], player = span.find("a", href=re.compile("/player/")).text) for span in soup.findAll("tr", {"class": ["tournament-decklist-odd", "tournament-decklist-event"]})]
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
 
def exists_tournament(_format,_tournament):
    deck_dir = ROOT_DIR + '/' + _format + '/' + _tournament
    
    if os.path.isdir(deck_dir):
        return 1
    
    return 0

def deck_path(_id, format = '', tournament = ''):   
    if os.path.isfile(FILE_PATH):
        df = pd.read_csv(FILE_PATH, sep=SEP)   
        
        for idx,row in df.iterrows(): 
            if row["ID"] == _id:
                format = row["Format"]
                tournament = row["Tournament"]   
    
    deck_dir = ROOT_DIR + '/' + format + '/' + tournament
    deckfile = deck_dir + '/' + str(_id) + '.txt'
    
    return deckfile

def print_deck(_ids, filename = '', format = '', tournament = ''):
    if isinstance(_ids, list):
        decks = []
        
        for _id in _ids:
            deck_info = dict()
            deck_info['ID'] = _id
            deck_info['Decklist'] = open(deck_path(_id), 'r').read()
            deck_info['New_Deck_Name'] = ''
            
            decks.append(deck_info)
        
        df = pd.DataFrame(decks)
        df.to_csv(ROOT_DIR + '/' + filename)
        
        print('Saved to: ' + ROOT_DIR + '/' + filename)
            
    if isinstance(_ids, int):
        f = open(deck_path(_ids, format, tournament), 'r').read()
        return f

def download_deck(_id,_format,_tournament):
    link = MTGSCRAPER_URL + '/deck/download/' + _id
    deck_dir = ROOT_DIR + '/' + _format + '/' + _tournament
    deckfile = deck_dir + '/' + _id + '.txt'
    
    response = requests.get(link).text
    mkdir_p(deck_dir)

    if not os.path.isfile(deckfile):
        #print(deckfile)
        with open(deckfile, 'a+') as f:
            f.write(response)
        return 1
            
def download_tournaments(_list):
    
    rows = []
    
    for page in _list:
        tournament = fetch_tournament(page)
        
        if exists_tournament(tournament.format, tournament.name):
            print('Tournament already exists: ' + str(tournament))
            continue
        
        print('Importing ' )
        for deck in tournament:
            deck_info = dict()
            deck_info['Deck'] = deck.name
            deck_info['Player'] = deck.player
            deck_info['ID'] = re.findall("\d+", deck.url)[0]
            deck_info['Tournament'] = tournament.name
            deck_info['Date'] = tournament.date
            deck_info['Format'] = tournament.format
            deck_info['Size'] = tournament.size
            
            download_deck(re.findall("\d+", deck.url)[0], tournament.format, tournament.name)
            deck_info['Decklist'] = print_deck(int(deck_info['ID']), format = tournament.format, tournament = tournament.name)
            deck_info['Deck Adjusted'] = ''
            rows.append(deck_info)
        print('Done importing ' + str(tournament))

    df = pd.DataFrame(rows)
    write_decks(df)
    
def write_decks(_df):
    if not os.path.isfile(FILE_PATH):
        _df.to_csv(FILE_PATH, sep=SEP)
        print('File created: ' + FILE_PATH)
    else: 
        _df.to_csv(FILE_PATH, mode='a', header=False, sep=SEP)
        print(str(len(_df.index)) + ' rows appended to: ' + FILE_PATH)
     
print('Done initializing classes')
#%%

# FIX UNTITLED DEKCS


def get_all_decks_id(deckname):
    rows = []
    
    if os.path.isfile(FILE_PATH):
        df = pd.read_csv(FILE_PATH, sep=';')
        
        for idx,row in df.iterrows(): 
            if row["Deck"] == deckname:
                rows.append(row["ID"])
                
    return rows

def overwrite_deck_names(id = 0, new_deck_name = '', file = ''):
    if not file:
        if os.path.isfile(FILE_PATH):
            df = pd.read_csv(FILE_PATH, index_col = 0, sep=SEP)
            
            for idx,row in df.iterrows(): 
                if row["ID"] == id:
                    old_deck_name = df["Deck"]
                    df["Deck"] = new_deck_name
                    print('Changed deck name from: ' + old_deck_name + ' to: ' + new_deck_name)

    if file:
        template_path = ROOT_DIR + '/' + file
        if os.path.isfile(FILE_PATH):
            df = pd.read_csv(FILE_PATH)
            
            df_template = pd.read_csv(template_path, sep = SEP)
            
            for idx, i in df_template.iterrows():
                id = i["ID"]
                new_deck_name = i["New_Deck_Name"]
                print(str(id) + new_deck_name)
            
                mask = df.ID == id
                
                df['Deck'][mask] = new_deck_name
                
        df.to_csv(ROOT_DIR + '/' + 'testing.csv')
   

print_deck(get_all_decks_id('Untitled'), filename = 'untitled.csv')
overwrite_deck_names(file = 'untitled.csv')


#%%
# Add decklists to Tournaments.csv

decklists = []
counter = 0
if os.path.isfile(FILE_PATH):
    df = pd.read_csv(FILE_PATH, index_col=0)
    
    for idx,row in df.iterrows(): 
        id = row["ID"]
        decklists.append(print_deck(id))
        counter += 1
        print(counter)
        
    df["Decklist"] = decklists
    df["Deck Adjusted"] = ''
    
    df.to_csv(FILE_PATH)
    


#%%
#Imports the latest Pioneer decklists
tournament_list = ["pioneer-ptq-12006968", #OK IMPORTED
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

tournament_list = ["pioneer-ptq-12033248", #OK IMPORTED
                   "pioneer-ptq-12028087",
                   "pioneer-ptq-12028086",
                   "pioneer-ptq-12021797",
                   "pioneer-ptq-12014480"]

tournament_list = ["pioneer-ptq-12033250", #OK IMPORTED
                   "pioneer-ptq-12033249",
                   "pioneer-ptq-12028088"]

tournament_list = ["pioneer-ptq-12038785", #OK IMPORTED
                   "pioneer-ptq-12033252",
                   "pioneer-ptq-12033251"]

tournament_list = ["pioneer-challenge-12049245", #OK IMPORTED
                   "pioneer-challenge-12052914",
                   "pioneer-preliminary-12049222",
                   "pioneer-preliminary-12049235",
                   "pioneer-preliminary-12049238",
                   "pioneer-preliminary-12052874",
                   "pioneer-preliminary-12052877",
                   "pioneer-preliminary-12052886"]

tournament_list = ["pioneer-preliminary-12052891", #OK IMPORTED
                   "pioneer-preliminary-12052904",
                   "pioneer-preliminary-12052907",
                   "pioneer-preliminary-12052927",
                   "pioneer-preliminary-12052930",
                   "pioneer-preliminary-12052939",
                   "pioneer-preliminary-12052944",
                   ]

tournament_list = ["scg-pioneer-classic-columbus",
                   "pioneer-preliminary-12061213"]
 
download_tournaments(tournament_list)
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
