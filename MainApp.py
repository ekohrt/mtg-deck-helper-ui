# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 13:50:01 2021
@author: Ethan

This class iherits from the original ui class. This way we can make changes to the 
ui in QTDesigner while keeping this backend intact. Run the app from here.
"""
import MtgDeckHelperGUI as mtgGui
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import InfoGetter
import Deck


class MainApp(mtgGui.Ui_MainWindow):
    
    def __init__(self, window):
        self.setupUi(window)
        
        
        
        #Set up intance variables for current_deck, selected card, and infoGetter
        self.infoGetter = InfoGetter.InfoGetter()
        
        #start app with a demo deck
        demoDeck = "4 Goblin Guide\n4 Monastery Swiftspear\n4 Eidolon of the Great Revel\n2 Skullcrack\n2 Lightning Helix\n4 Lightning Bolt\n//Sideboard\n2 Rest in Peace\n2 Skullcrack\n2 Wear // Tear"
        self.currentDeck = Deck.Deck(demoDeck)
        
        #update decklist widget with current deck
        self.updateDeckListWidget()
        
        #clear suggestionsListWidget at the start
        self.suggestions_listWidget.clear()
        
        #string for holding the most recently selected card's name
        self.selectedCard = ""
        
        ##########################
        #Attach Buttons to methods
        ##########################
        self.addToDeck_pushButton.clicked.connect(self.addToDeck)
        self.viewSimilar_pushButton.clicked.connect(self.viewSimilar)
        self.getImage_pushButton.clicked.connect(self.pullImagePressed)
        self.matchColors_checkBox.clicked.connect(self.matchColors)
        self.viewSuggestions_pushButton.clicked.connect(self.viewSuggestionsPressed)
        self.deck_listWidget.itemClicked.connect(self.deckItemClicked_event)
        self.suggestions_listWidget.itemClicked.connect(self.suggestionsItemClicked_event)

        
        #########################
        #other stuff
        #########################
        self.pasteDeck_plainTextEdit.setPlaceholderText("Paste Deck Here:") #ex.\n36 Lightning Bolt\n24 Mountain\n//Sideboard\n15 Storm Crow"
        self.pasteDeck_plainTextEdit.setPlainText(self.currentDeck.toString())




    # =============================================================================
    # Button Handlers
    # =============================================================================
    
    """
    Run this when user clicks something in deck_listWidget
    send card's original name to the "select card" method
    """
    def deckItemClicked_event(self, item):
        #deck items have a "3x cardName" format to them, so cut off "3x " to get original name
        text = item.text()
        cardName = text
        if 'x' in text:
            idx = text.find('x') +2     #this gets idx of first char in name
            cardName = text[idx:]
            
        self.selectCard(cardName)
    
    """
    run this when user clicks item suggestions_listWidget
    send card's original name to the "select card" method
    """
    def suggestionsItemClicked_event(self, item):
        #suggestion items are formatted like "cardName :: 0.9845" so split on the " :: ".
        cardName = item.text().split(" :: ")[0]
        self.selectCard(cardName)
    
    
    """
    Updates the QListWidget to show the cards in the current deck.
    """
    def updateDeckListWidget(self):
        #clear list
        self.deck_listWidget.clear()
        
        #loop over cards in deck, add a string showing number and name
        self.deck_listWidget.addItem("Main (" + str(self.currentDeck.mainAmnt) + ")")
        #make list of cardnames with "3x " in front or whatever number they have
        mainWithNums = [str(self.currentDeck.main[card]) + "x " + card for card in self.currentDeck.main.keys()]
        self.deck_listWidget.addItems(mainWithNums)
        
        self.deck_listWidget.addItem("")    #divider between main and sideboard
        self.deck_listWidget.addItem("Sideboard (" + str(self.currentDeck.sideboardAmnt) + ")")
        sideWithNums = [str(self.currentDeck.sideboard[card]) + "x " + card for card in self.currentDeck.sideboard.keys()]
        self.deck_listWidget.addItems(sideWithNums)
    
    
    """
    updates the suggestions list with a new list of cardnames 
    (get from Infogetter.getDeckRecommendations(inputDeckList, n) or .getSimilar(str_cardName))
    """
    def updateSuggestionsListWidget(self, cardList):
        #clear list
        self.suggestions_listWidget.clear()
        #loop over cards in recommendatons, add a string showing number and name
        self.suggestions_listWidget.addItems(cardList)
    
    
    
    
    """
    Handler for View Suggestions button
    """
    def viewSuggestionsPressed(self):
        #read text from input field and convert to deck object
        text = self.pasteDeck_plainTextEdit.toPlainText()
        self.currentDeck = Deck.Deck(text)
        print(self.currentDeck.toString())
        #update deckListWidget
        self.updateDeckListWidget()
        #get recommendations - list of tuples: [(str_cardName, flt_percent), ...]
        recs = self.infoGetter.getDeckRecommendations(self.currentDeck.main.keys(), 100)
        itemList = [card[0] + " :: " + str(card[1]) for card in recs]
        #update suggestionsListWidget
        self.updateSuggestionsListWidget(itemList)
        print("PUSHED viewSuggestions")
    
    
    #Handler for Pull Image button
    def pullImagePressed(self):
        if self.selectedCard != "":
            img = self.infoGetter.getCardImage(self.selectedCard)
            pixmap = QtGui.QPixmap(img, "1")
            self.card_image.setPixmap(pixmap)
            self.card_image.resize(pixmap.width(),pixmap.height())
            
    
    #Add to Deck Button
    def addToDeck(self):
        self.currentDeck.addCard(self.selectedCard)
        #update the text field and deck list widget
        self.pasteDeck_plainTextEdit.setPlainText(self.currentDeck.toString())
        self.updateDeckListWidget()
        print("pushed addToDeck")
    
    
    #Suggest similar button
    def viewSimilar(self):
        simList = self.infoGetter.getSimilar(self.selectedCard, 100)
        self.updateSuggestionsListWidget(simList)
        print("pushed suggestSimilar")
    
    
    #Match Colors Button
    def matchColors(self):
        #this is gonna suck balls... it's going to need to be an input into every method...
        print("pushed matchColors")


    
    """
    Run this when you click on a card name in a listwidget.
    Changes text field to show selected card's info.
    Also updates image if file already is downloaded.
    @param str_cardName is the string name of the selected card
    """
    def selectCard(self, str_cardName):
        #store name of selected card
        self.selectedCard = str_cardName
        #update text field with card's info
        text = self.infoGetter.getCardText(str_cardName)
        self.cardText_plainTextEdit.setPlainText(text)
        #get image if saved (otherwise default img) and update image
        img = self.infoGetter.getImageIfSaved(str_cardName)
        pixmap = QtGui.QPixmap(img, "1")
        self.card_image.setPixmap(pixmap)
        self.card_image.resize(pixmap.width(),pixmap.height())
    
    
    # =============================================================================
    # 
    # =============================================================================




def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    #create instance of our app
    ui = MainApp(MainWindow)
    #show the window and start the app
    MainWindow.show()
    app.exec_()

if __name__ == "__main__":
    main()