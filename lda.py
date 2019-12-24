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
     decks[i] = str(deck).replace('\n', ' ')
     decks[i] = str(decks[i]).replace('  ', ' ')
     print(decks[i]+'\n')
     
deckfile = ROOT_DIR + '/decks.csv'
with open(deckfile, 'w') as f:
    for item in decks:
        f.write("%s\n" % item)
        

#%%
#Latent Dirichlet Allocation algorithm
import gensim
import re 
from six import iteritems

dictionary = gensim.corpora.Dictionary([x.strip() for x in re.split(r"[\d]+", line.replace("\"", ""))] for line in open(deckfile))
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
dictionary.filter_tokens(once_ids)  # remove cards that appear only once
dictionary.compactify()  # remove gaps in id sequence after words that were removed
#%%
import numpy as np
unique_cards = len(dictionary.keys())
print(unique_cards)
class MyCorpus(object):
    def __iter__(self):
        for line in open(deckfile):
            decklist = line.replace("\"", "") # remove start and end tokens            
            decklist = re.split(r"([\d]+)", decklist) # split by numbers and card names
            decklist = [x.strip() for x in decklist] # remove whitespace
            decklist = list(filter(None, decklist)) # remove empty words
            cleaned_decklist = [] 
            for i in range(len(decklist)//2): # remove numbers, add multiplicities of cards
                for j in range(int(decklist[i*2])):
                    cleaned_decklist.append(decklist[i*2+1])
            yield dictionary.doc2bow(cleaned_decklist)
corpus_memory_friendly = MyCorpus()
archetypes = 30
np.random.seed(1)
alpha_prior = [1.0 / archetypes] * archetypes
beta_prior = [1.0 / archetypes] * unique_cards
iterations = 30
#%%
lda = gensim.models.ldamodel.LdaModel(corpus=corpus_memory_friendly, id2word=dictionary, num_topics=archetypes, passes=iterations, alpha = alpha_prior, eta = beta_prior)

#%%
number_of_top_cards = 16
archetypes_to_inspect = 20
for i in range(archetypes_to_inspect):
    print(("Archetype %i \n %s \n") % (i, lda.print_topic(i, topn=number_of_top_cards)))
#%%
archetype_id = 2
archetype_topic = np.array(lda.show_topic(archetype_id, topn=9999))

archetype_distribution = np.array(archetype_topic[:,1], dtype="float32")
archetype_distribution = archetype_distribution / np.sum(archetype_distribution)

archetype_indices = np.zeros(len(archetype_distribution))
main_deck = 60
sideboard = 15
while np.sum(archetype_indices) < main_deck+sideboard:
    new_card = np.random.multinomial(1, archetype_distribution)
    archetype_indices += new_card
    if 5 in archetype_indices:
        archetype_indices -= new_card
archetype_cards = np.array(archetype_topic[:,0], dtype="str")
minimum_cards = 1.0
deck_title = "ARchetype"
print(deck_title)
for i in range(len(archetype_distribution)):
    if archetype_indices[i] >= minimum_cards:        
        print('%i %s' % (archetype_indices[i], archetype_cards[i]))