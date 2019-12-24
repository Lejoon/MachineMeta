
km = dask_ml.cluster.KMeans(n_clusters=9, oversampling_factor=2)
print('Done')

km.fit(deck_vectors)

labels = list(km.labels_.compute()) #We call compute on it because it's lazy
decks_labels = list(zip(decks,labels)) #Now we can pair each deck to its label.

def most_common_cards(deck, k):
    deck.sort(key = lambda deck: deck[0], reverse=True)
    return [card[1] for card in deck[:k]]  

def decks_by_label(a_label):
    return [(deck, label) for (deck, label) in decks_labels if label == a_label]
  
k = 7
N = 10
for deck, label in decks_by_label(6)[:N]:
    print(str(most_common_cards(deck, k))+" "+ str(label))

import seaborn as sns
import matplotlib.pyplot as plt

label_counts = [(label,len(decks_by_label(label))) for label in range(20)]
counts = [count for _, count in label_counts]
points = {
    'cluster':[label for label, _ in label_counts],
    'count':[count for _, count in label_counts],
}

sns.barplot(x="cluster", y="count", data=points).set_title("Decks by Cluster")
plt.savefig('figure 1')

k = 40
for LABEL in range(20):
    label_set = set(most_common_cards(decks_by_label(LABEL)[0][0], k))
    for deck, label in decks_by_label(LABEL):
        label_set.intersection(set(most_common_cards(deck, k)))
    label_set = set(label_set)
    print("Cluster number {}:".format(LABEL))
    print(label_set)
    print("\n")