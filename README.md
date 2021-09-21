# mtg-deck-helper-ui
Python UI for viewing a Magic: the Gathering decklist.  
Also includes tools for finding similar cards and deck suggestions.  

![Preview image](preview_image.png?raw=true "Preview image")  
  
The "SuggestSimilar" button searches for cards with similar text, using a [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) algorithm.  
  
The "View Suggestions" button suggests cards that often appear in similar decks, using co-occurrence data from this dataset of modern decks: https://github.com/ekohrt/mtg-dataset-10000-modern-decks.  
  
There is currently no feature to search a card by name: to add a card to the deck, type its name in the text field on the left.
