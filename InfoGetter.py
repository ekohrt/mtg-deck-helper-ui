# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 11:30:49 2021
@author: Ethan

A collection of static methods for parsing and retreiving various data 
for the magicDeckViewer GUI.
"""

import json
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os.path
import difflib

class InfoGetter:
    
    def __init__(self):
        #read the mtgJSON file
        with open('other_files/AtomicCards.json', encoding="utf8") as atomicFile:
            self.cards_dict = json.load(atomicFile)
        #tf vectors, tfidf model, and a parallel list of corresponding cardNames
        self.tfs, self.tfidf, self.cardNames = self.initTfidf(self.cards_dict)
        #frequency dict for co-occurrence recommendations
        with open('other_files/fixedCardFreqs_deckstatsModern.json', encoding="utf8") as freqsFile:
            self.freqDict = json.load(freqsFile)
        #Card Ids for fetching images
        with open('other_files/cardIds.json', encoding="utf8") as idsFile:
            self.cardIds = json.load(idsFile)

# =============================================================================
#     TF-IDF Stuff
# =============================================================================



    """
    Returns a list of pre-trained tf-idf vectors, and a parallel list of 
    corresponding cardNames (for searching through later)
    @input cards_dict is the mtgJSON file as a dictionary
    """
    def initTfidf(self, cards_dict):
        #parallel lists
        cardNames = []
        cardTexts = []  #aka our "documents" (list of strings)
        
        #used for removing punctuation, keeping {}s. (Source: https://www.semicolonworld.com/question/62188/how-to-strip-string-from-punctuation-except-apostrophes-for-nlp)
        punct = string.punctuation.replace('{', '').replace('}', '')
        translator = str.maketrans('', '', punct)
        
        #TODO: maybe remove costs from text for similarity bc they're too unique (things like {T} {3B} etc)
        #well, the number doesn't exactly matter... maybe replace with a symbol?
        
        #read each card, put their name & text into parallel lists (dict doesn't work because we need the indexes)
        card_names = self.cards_dict["data"]
        for card in card_names:
            #Filter out cards from janky sets: Vanguard, Mystery Booster, Unhinged, Unsanctioned, Unglued
            skip = False
            jankySets = ["PVAN", "UNH", "UND", "UGL", "CMB1"]
            for jank in jankySets:
                if jank in card_names[card][0]['printings']:
                    skip = True
            if skip: continue
        
            #Get the card text from the card (will be in a list, accounts for multi-face cards)
            textList = self.get_property(card, "text")
            textList[:] = [x for x in textList if x != None]
            if textList == None: 
                text = ""
            else:
                text = " ".join(textList)
                
            #delete card's name from card text (or both names if it's a split card)
            text = text.replace(card, "")
            if " // " in card:
                splitName = card.split(" // ")
                for s in splitName:
                    text = text.replace(s, "")
                
            #TODO: add card's types to card (creature types, sorcery, instant, etc)
            
            #make lowercase, remove punctuation, add to lists
            lowers = text.lower()
            no_punctuation = lowers.translate(translator)
            cardNames.append(card)
            cardTexts.append(no_punctuation)
            
        #this can take some time (param max_df=0.60 (doc freq) means that if 60%+ of documents have a word,ignore it)
        #try it without stop words or max doc freq (sklText.ENGLISH_STOP_WORDS include numbers) (min_df=0.05 means ignore words mentioned in <100 cards) (bad idea?)
        #tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=sklText.ENGLISH_STOP_WORDS)
        tfidf = TfidfVectorizer(tokenizer=InfoGetter.tokenize)
        tfs = tfidf.fit_transform(cardTexts)
        
        #return tf vectors, tfidf model, and a parallel list of corresponding cardNames
        return (tfs, tfidf, cardNames)
    
    
    
    
    """
    Helper: returns a property of a given card (in a list)
    Note: some cards have multiple faces, so this will return a liat.
    (for all properties see: https://mtgjson.com/data-models/card-atomic/)
    
    @param cardName is the string name of a card
    @param prop is the string name of a property
    """
    def get_property(self, cardName, prop):
        #check if cardname is valid:
        if cardName not in self.cards_dict["data"].keys():
            return None
        
        toReturn = []
        #loop over all faces of the card
        for face in self.cards_dict["data"][cardName]:  
            #check if this face has this property
            if prop not in face.keys():
                toReturn.append(None)
            else:
                toReturn.append(face[prop])
        return toReturn
    
    
    """
    Helper for tfidf stuff
    """
    def tokenize(text):
        stemmer = PorterStemmer()
        tokens = nltk.word_tokenize(text)
        stems = InfoGetter.stem_tokens(tokens, stemmer)
        return stems
    
    """
    Helper for tokenize
    """
    def stem_tokens(tokens, stemmer):
        stemmer = PorterStemmer()
        stemmed = []
        for item in tokens:
            stemmed.append(stemmer.stem(item))
        return stemmed
    
    
    """
    Uses tf-idf to find cards with similar text to the given card
    """
    def getSimilar(self, str_inputCard, n):
        #now, find the n most similar cards to the input card
        #modified from source: https://stackoverflow.com/a/12128777
        inputCardTextList = self.get_property(str_inputCard, "text")
        if inputCardTextList == None: 
            inputCardText = ""
        else:
            inputCardText = " ".join(inputCardTextList)
        
        #print(inputCardText)
        #calc all cosine sims with the first param
        response = self.tfidf.transform([inputCardText])
        cosine_similarities = cosine_similarity(response, self.tfs).flatten()
        
        #sort all the sims and keep the top n
        closest = []
        related_docs_indices = cosine_similarities.argsort()[:-n:-1]
        for idx in related_docs_indices:
            closest.append(self.cardNames[idx])
        return closest
    
    
    
# =============================================================================
#     Get Card Text (from mtgJSON)
# =============================================================================
    
    
    """
    Returns the card text of a given card (from mtgJSON file) (and other info)
    Format:
        CardName
        ManaCost
        Types
        CardText
    @param cardName is the card's real name (string)
    """
    def getCardText(self, cardName):
        finalText = ""
        if cardName not in self.cards_dict["data"]:
            return "Error: Invalid Card Name"
        card = self.cards_dict["data"][cardName]
        
        count = 0
        for face in card:
            
            #Get mana cost of card:
            if "manaCost" in face.keys():
                manaCost = face["manaCost"]
            else:
                manaCost = "<No Cost>"
            
            #Get Types
            if "type" in face.keys():
                types = face["type"]
            else:
               types = "<No Types>"
               
            #Get the card text from the card
            if "text" in face.keys():
                text = face["text"]
            else:
                text = "<No Text>"
                
            #If Planeswalker, get loyalty (will be list of ints)
            if "loyalty" in face.keys():
                loyalty = "Loyalty: " + str(face["loyalty"])
            else:
                loyalty = ""
            
            finalText += cardName + "\n" + manaCost + "\n" + types + "\n\n" + text + "\n\n" + loyalty + "\n"
            
            #put a "//" divider between mutliple faces of a card
            count += 1
            if count < len(card):
                finalText += "\n//\n\n"
                
        return finalText



# =============================================================================
#    Get Image (from Gatherer or from file) 
# =============================================================================
    
    """
    Returns the filepath of the given card image
    (checks card_images folder first, otherwise downloads from Gatherer)
    
    @param cardName is the card's real name (string)
    """
    def getCardImage(self, cardName):
        #check if valid cardname
        if cardName not in self.cardIds.keys():
            print("ERROR: INVALID CARD NAME \"" + cardName + "\". @InfoGetter.getCardImage")
            return None
        #get card's id number (highest = latest)
        idNum = self.cardIds[cardName]
        #check if we have the image already in folder (named as just the id number)
        imageFile = "card_images/" + str(idNum) + ".jpg"
        if os.path.isfile(imageFile):
            print("FILE EXISTS! " + imageFile)
        #otherwise download image from Gatherer.wizards.com
        else: 
            print("FETCHING FILE FROM GATHERER")
            url = "https://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=" \
                    + str(idNum) + "&type=card"
            #get image from gatherer
            response = requests.get(url)
            file = open(imageFile, "wb")
            file.write(response.content)
            file.close()
            
        return imageFile
        
    
    
    """
    Returns the filepath of the given card image, IF it has been downloaded already
    (otherwise gives the default image)
    
    @param str_cardName is the card's real name (string)
    """
    def getImageIfSaved(self, str_cardName):
        defaultImage = "card_images/DefaultCardImage.png"
        
        #check if valid card name
        if str_cardName not in self.cardIds.keys():
            print("ERROR: INVALID CARD NAME")
            return defaultImage
        
        #get card's id number (highest = latest)
        idNum = self.cardIds[str_cardName]
        
        #check if we have the image already in folder (named as just the id number)
        imageFile = "card_images/" + str(idNum) + ".jpg"
        if os.path.isfile(imageFile):
            print("FILE EXISTS! " + imageFile)
            return imageFile
        #otherwise return default image
        else:
            return defaultImage
        
        
        
# =============================================================================
#     Get Recommendations (based on co-occurrence frequencies)
# =============================================================================
    
    """
    Returns a list of n recommended cards based on the input decklist
       
    @param inputDeckList is a list of string cardnames
    @param n is an int number of recommended cards to return
    @param colors is a list of colors to keep: ["R","G","B","U","W"]
    
    @return finalReqs is a list of tuples (str_cardName, flt_percent)
    """
    def getDeckRecommendations(self, inputDeckList, n, colors = []):
        #add underscores to card names:
        #deckList = [s.replace(" ", "_") for s in inputDeckList]
        deckList = inputDeckList
        
        #Combine frequency dicts of each card in input deck, keeping highest values.
        freqs = {}
        for card in deckList:
            freqs = InfoGetter.mergeDictsKeepHighest(freqs, self.freqDict[card])
        
        #sort into one big list of cards and co-occurrence freqs, and return top n
        closestCards = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        recs = []
        for card in closestCards:
            if card[0] not in deckList: 
                #remove underscores from cardnames
                orig_name_and_pct = (card[0].replace("_", " "), card[1])
                recs.append(orig_name_and_pct)
            if len(recs) == n: #stop when you have n recommendations
                break
        
        return recs
        
        #ok, problem... when storing the decklists, we removes commas so we could
        #store decks in a csv. Well, that means cards in the freq_dict also have
        #no commas. This means the getDeckRecommendations method can't find input
        #cards. We can't just remove commas from the input: while this would work
        #for showing the recs, adding that modified cardname back into the deck
        #would still not work. We need to loop over keys in the freq_dict and 
        #replace them with the correct cardName, commas and all.
        
    
    
    """
    Helper for getDeckRecommendations: merges two dictionaries, keeping highest values
    """
    def mergeDictsKeepHighest(dict1, dict2):
        #dict1.get(k, 0.0) is the same as dict1[k] but gives default of 0.0 if key not found
        merged = { k: max(float(dict1.get(k, 0.0)), float(dict2.get(k, 0.0))) for k in set(dict1) | set(dict2) }
        return merged
        
    
    
    """
    Gets recommendations for a single card (could also use getDeckRecommendations)
    @param targetCard is a string cardname, with "_"s instead of spaces.
    """
    def getCardRecommendations(self, targetCard, n):
        return dict(sorted(self.freqDict[targetCard].items(), key=lambda x: x[1], reverse=True)[:n])
    
    
    
    """
    Returns the colors in the mana cost of the given card
    """
    #TODO
    def getCardColors(self, str_cardName):
        #get mana cost property
        pass
# =============================================================================
#     
# =============================================================================
        
    
    
    
def main():
    ig = InfoGetter()
    #print(ig.getSimilar("Lightning Bolt", 10))
    #print(ig.cards_dict['data'].keys()) #these are cardnames
    #print(ig.cards_dict['data']["Lightning Bolt"][0]['printings'])
    #Liliana of the Veil
    #print(ig.getSimilar("Dauntless Escort", 10))
    #print(len(ig.cards_dict["data"]["Huntmaster of the Fells // Ravager of the Fells"]))
    #print(ig.getDeckRecommendations(["Dauntless Escort"], 10))
    #ig.getCardImage("Liliana of the Veil")
    
    
    
if __name__ == "__main__":
    main()