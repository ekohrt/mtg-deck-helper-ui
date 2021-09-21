# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 23:53:49 2021
@author: ekohrt

Class that represents a magic deck
"""

class Deck:
    """
    Constructor: takes a properly formatted deck (string) as input
    exampleDeck = ("4 Chain Lightning\n"
                   "3 Curse of the Pierced Heart\n"
                   "4 Fireblast\n"
                   "4 Ghitu Lavarunner\n"
                   "4 Lightning Bolt\n"
                   "17 Mountain\n"
                   "\n"
                   "//Sideboard\n"
                   "2 Electrickery\n"
                   "3 Flame Rift\n")
    """
    def __init__(self, deckString):
        #original input string
        self.deckString = deckString
        allCards = Deck.parseDeckString(deckString)
        #main deck dictionary {str_cardName: int_amnt}
        self.main = allCards[0]
        #sideboard dictionary {str_cardName: int_amnt}
        self.sideboard = allCards[1]
        #count # of cards in main / side
        self.mainAmnt = sum(self.main.values())
        self.sideboardAmnt = sum(self.sideboard.values())
        #make list of strings for displaying main & side
        #self.mainList = [self.currentDeck.main[cardName] + "x " + cardName for cardName in self.currentDeck.main.keys()]
        #self.sideList = [self.currentDeck.sideboard[cardName] + "x " + cardName for cardName in self.currentDeck.sideboard.keys()]
          
    
    """
    Converts this deck into a string
    """
    def toString(self):
        s = ""
        for cardName in self.main.keys():
            s += str(self.main[cardName]) + " " + str(cardName) + "\n"
        s += "//Sideboard\n"
        for cardName in self.sideboard.keys():
            s += str(self.sideboard[cardName]) + " " + str(cardName) + "\n"
        return s
    

    """
    Add 1 given card to deck
    """    
    def addCard(self, str_cardToAdd):
        #add 1 of this card to deck
        if str_cardToAdd in self.main.keys():
            self.main[str_cardToAdd] += 1
        else:
            self.main[str_cardToAdd] = 1
    
    
    
    
    """
    Converts an input decklist string into a list of two dicts {str_cardName: int_amnt} 
    The first dict in the list is the main deck, second is sideboard.
    Decklist must be formatted like "4 cardName\n17 cardName\n 3 cardName\n..."
    """
    def parseDeckString(deckString):
        #each card on a separate line. Strip whitespace from front/back of tokens. Delete empty items.
        tokens = deckString.split("\n")
        tokens = map(str.strip, tokens)
        tokens = [value for value in tokens if value != ""]
        
        #check if a token contains "sideboard" and get its index
        sideboardIdx = -1
        for t in tokens:
            if "sideboard" in t.lower():
                sideboardIdx = tokens.index(t)
        
        #split into two lists of tokens: main and sideboard
        if sideboardIdx != -1:
            main_raw = tokens[:sideboardIdx]
            side_raw = tokens[sideboardIdx+1:]
        else:
            main_raw = tokens
            side_raw = []
        
        #convert tokens into dicts
        main = {}
        side = {}
        for token in main_raw:
            #parse main deck
            data = token.split(' ')
            if len(data) < 2: continue
            num = int(data[0])
            cardName = " ".join(data[1:])
            main[cardName] = num
        for token in side_raw:
            #parse sideboard
            data = token.split(' ')
            if len(data) < 2: continue
            num = int(data[0])
            cardName = " ".join(data[1:])
            side[cardName] = num
        
        return [main,side]

    
    

def main():
    testDeck = ("4 Chain Lightning\n"
                "3 Curse of the Pierced Heart\n"
                "4 Fireblast\n"
                "4 Ghitu Lavarunner\n"
                "4 Lightning Bolt\n"
                "17 Mountain\n"
                "\n"
                "//Sideboard\n"
                "2 Electrickery\n"
                "3 Flame Rift\n")
    print(Deck.parseDeckString(testDeck))
if __name__ == "__main__":
    main()
    
