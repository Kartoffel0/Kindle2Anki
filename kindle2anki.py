import time
import zipfile
import os
import json
from sudachipy import dictionary
import urllib.request
import re
import sqlite3
from collections import deque

"""
If you run into any problems while trying to use this script 
you can contact me on discord Kartoffel#7357 and I'll try to fix it
no guarantees tho
"""

TKZR = dictionary.Dictionary(dict_type="full").create()
cntCards = 0
dict_DBterms = {}
dict_DBtermsRev = {}
dict_DBtermsRev2 = {}
term_listS = deque()
term_listW = deque()
dict_DBsource = {}
dict_DBBooks = {}
book_list = []
book_listDB = []
wordCount = {}
wordCountAdded = {}
sameBook = {}
timestampsDB = {}
wordCountNew = {}

dictsFile = open("app_files/dicts.json", encoding="utf-8")
dicts = json.load(dictsFile)

jpodFile = open("app_files/jpodFiles.json", encoding="utf-8")
jpod = json.load(jpodFile)

freqMainFile = open("app_files/mainFreq.json", encoding="utf-8")
freqMain = json.load(freqMainFile)

historyFile = open("app_files/added.json", encoding="utf-8")
history = json.load(historyFile)

historyFile3 = open("app_files/errorHistory.json", encoding="utf-8")
historyError = json.load(historyFile3)

freqListsFile = open("app_files/freqlists.json", encoding="utf-8")
freqlists = json.load(freqListsFile)

configFile = open("app_files/config.json", encoding="utf-8")
config = json.load(configFile)

if "bookName" not in config and config["first_run"] == 0:
    bookOpt = int(input("\n Would you like to add the name of the book you're mining from to your cards?\n Enter 1 to confirm or 0 to decline: "))
    if bookOpt == 0:
        config["bookName"] = 0
        with open("app_files/config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False)
        print("\n Done!\n")
    else:
        bookField = input('\n Please inform the field name!!!case sensitive!!! where you want the "Book Name" to be: ')
        config["bookName"] = 1
        config["bookField"] = bookField
        with open("app_files/config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False)
        print("\n Done!")
dict_name = config["dict_Names"]
freqMax = config["freqMax"]
try:
    timestamps = config["timestamps"].copy()
except:
    timestamps, config["timestamps"] = {}, {}

def add_dict(dictN):
    global dict_name
    global dicts
    global config
    cnt = 0
    fileNames = os.listdir("app_files/{}".format(dictN))
    for name in fileNames:
        if name == "index.json":
            dict1_IdFile = open("app_files/{}/index.json".format(dictN), encoding="utf-8")
            dict1_Index = json.load(dict1_IdFile)
            dict_name.append(dict1_Index["title"])
            config["dict_Names"].append(dict1_Index["title"])
        else:
            cnt += 1
    for i in range(1, cnt+1):
        dictFile = open("app_files/{}/{}".format(dictN, fileNames[i]), encoding="utf-8")
        data = json.load(dictFile)
        for j in data:
            if (j[0] in dicts[dictN]):
                try:
                    if j[1] == freqMain[j[0]]:
                        dicts[dictN][j[0]] = j
                except KeyError:
                    continue
            else:
                dicts[dictN][j[0]] = j

def appendDict():
    global freqlists
    freqlists.append({})

def appendDict2():
    global dicts
    dicts.append({})  

def add_freqList(freqN):
    global freqlists
    cnt = 0
    fileNames = os.listdir("app_files/freq/{}".format(freqN))
    for name in fileNames:
        if name == "index.json":
            continue
        else:
            cnt += 1
    for i in range(1, cnt+1):
        freqFile = open("app_files/freq/{}/{}".format(freqN, fileNames[i]), encoding="utf-8")
        data = json.load(freqFile)
        for j in data:
            if type(j[2]) is dict:
                if "frequency" in j[2]:
                    freqlists[freqN][j[0]] = j[2]["frequency"]
            else:
                if re.search("/", str(j[2])):
                    freqlists[freqN][j[0]] = int(j[2].split("/")[0])
                else:
                    freqlists[freqN][j[0]] = j[2]

print(" Kindle2Anki - https://github.com/Kartoffel0/Kindle2Anki")
if config["first_run"] == 1:
    print("\n This will only be asked once,\n on the next run you'll not have to inform everything again.")
    dict_Num = int(input("\n Please inform how many dictionaries you want to add: "))
    print("\n Ensure the zips are on the same directory as this script")
    config["dictNum"] = dict_Num
    for i in range(dict_Num):
        with zipfile.ZipFile("{}".format(input("\n Enter the filename for your {}° dictionary: ".format(i+1))), 'r') as zip_ref:
            zip_ref.extractall("app_files/{}".format(i))
        appendDict2()
        add_dict(i)
    freqNum = int(input("\n This script don't support multi frequency per word frequency lists,\n make sure the frequency list you'll add has only one frequency per word\n\n Please inform how many frequency lists you want to add,\n you have to add at least one: "))
    for j in range(freqNum):
        with zipfile.ZipFile("{}".format(input("\n Enter the filename for your {}° frequency list: ".format(j+1))), 'r') as zip_ref:
            zip_ref.extractall("app_files/freq/{}".format(j))
        appendDict()
        add_freqList(j)
    freqMax = int(input("\n Please inform the maximum frequency limit\n any words with a frequency rank superior to\n that will not be processed: "))
    config["freqMax"] = freqMax
    config["first_run"] = 0
    deck = input("\n Please inform the name of the deck(!!!case sensitive!!!) where you want the cards to be added: ")
    config["deckName"] = deck
    cardType = input("\n Please inform the card type(!!!case sensitive!!!) you want to use as template for the added cards: ")
    config["cardType"] = cardType
    termField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Word' to be: ")
    config["termField"] = termField
    readField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Reading' to be: ")
    config["readField"] = readField
    dictField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Definitions' to be: ")
    config["dictField"] = dictField
    sentField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Sentence' to be: ")
    config["sentField"] = sentField
    audioField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Audio' to be: ")
    config["audioField"] = audioField
    nameField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Book Name' to be\n Enter 0 if you don't want to add the book name to your cards: ")
    if nameField != 0:
        config["bookName"] = 1
        config["bookField"] = nameField
    names = []
    for i in range(len(config["dict_Names"])):
        if config["dict_Names"][i] in names:
            continue
        else:
            names.append(config["dict_Names"][i])

    config["dict_Names"] = names
    dict_name = config["dict_Names"]

    with open("app_files/config.json", "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False)
    with open("app_files/dicts.json", "w", encoding="utf-8") as file:
        json.dump(dicts, file, ensure_ascii=False)
    with open("app_files/freqLists.json", "w", encoding="utf-8") as file:
        json.dump(freqlists, file, ensure_ascii=False)
    print("\n Done!\n")

def newCard(deckInfo, term, reading, defs, source, book=0):
    global jpod
    tmpJpod = (reading+"_"+term)
    if tmpJpod in jpod:
        if book == 0:
            return {"action": "addNote", "version": 6, "params": {"note":{"deckName": deckInfo[0], "modelName": deckInfo[1], "fields": {deckInfo[2]: term, deckInfo[3]: reading, deckInfo[4]: defs.replace("\n", "<br>"), deckInfo[5]: source}, "options": {"allowDuplicate": False, "duplicateScope": "deck", "duplicateScopeOptions": {"deckName": deckInfo[0], "checkChildren": True, "checkAllModels": True}}, "tags": ["Kindle2Anki"], "audio": [{"filename": "{} - {}.mp3".format(reading, term),"url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji={}&kana={}".format(term, reading), "fields": [deckInfo[6]]}]}}}
        else:
            return {"action": "addNote", "version": 6, "params": {"note":{"deckName": deckInfo[0], "modelName": deckInfo[1], "fields": {deckInfo[2]: term, deckInfo[3]: reading, deckInfo[4]: defs.replace("\n", "<br>"), deckInfo[5]: source, deckInfo[7]: book}, "options": {"allowDuplicate": False, "duplicateScope": "deck", "duplicateScopeOptions": {"deckName": deckInfo[0], "checkChildren": True, "checkAllModels": True}}, "tags": ["Kindle2Anki"], "audio": [{"filename": "{} - {}.mp3".format(reading, term),"url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji={}&kana={}".format(term, reading), "fields": [deckInfo[6]]}]}}}
    else:
        print(" Warning! No audio avaiable: ", term)
        if book == 0:
            return {"action": "addNote", "version": 6, "params": {"note":{"deckName": deckInfo[0], "modelName": deckInfo[1], "fields": {deckInfo[2]: term, deckInfo[3]: reading, deckInfo[4]: defs.replace("\n", "<br>"), deckInfo[5]: source}, "options": {"allowDuplicate": False, "duplicateScope": "deck", "duplicateScopeOptions": {"deckName": deckInfo[0], "checkChildren": True, "checkAllModels": True}}, "tags": ["Kindle2Anki"]}}}
        else:
            return {"action": "addNote", "version": 6, "params": {"note":{"deckName": deckInfo[0], "modelName": deckInfo[1], "fields": {deckInfo[2]: term, deckInfo[3]: reading, deckInfo[4]: defs.replace("\n", "<br>"), deckInfo[5]: source, deckInfo[7]: book}, "options": {"allowDuplicate": False, "duplicateScope": "deck", "duplicateScopeOptions": {"deckName": deckInfo[0], "checkChildren": True, "checkAllModels": True}}, "tags": ["Kindle2Anki"]}}}

def invoke(params, term="error"):
    global cntCards
    global historyError
    time.sleep(3)
    try:
        requestJson = json.dumps(params).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
        if len(response) == 2:
            if response['error'] is None:
                cntCards += 1
                print("", cntCards, "Success:   ", term)
            elif response['error'] == 'cannot create note because it is a duplicate':
                print(" Fail!    Note is a duplicate: ", term)
            else:
                raise Exception
        else:
            raise Exception
    except:
        historyError.append(term)
        print(" Fail!    Failed to add: ", term)

def deconjug(term, mode=0):
    tkTerm = TKZR.tokenize(term)
    if mode == 0:
        return tkTerm[0].dictionary_form()
    else:
        return tkTerm[0].normalized_form()
        
def lookup(term, source, dictN=0):
    try:
        definition = dicts[dictN][term]
        return [term, definition[1], definition[5][0], source.strip(), dictN]
    except KeyError:
        try:
            termTK = deconjug(term)
            definition = dicts[dictN][termTK]
            return [termTK, definition[1], definition[5][0], source.strip(), dictN]
        except KeyError:
            try:
                termTK = deconjug(term, 1)
                definition = dicts[dictN][termTK]
                return [termTK, definition[1], definition[5][0], source.strip(), dictN]
            except KeyError:
                return None

sqliteConnection = sqlite3.connect('vocab.db')

cursor = sqliteConnection.cursor()
cursor.execute("SELECT * FROM WORDS;")
dbWords = cursor.fetchall()

cursor2 = sqliteConnection.cursor()
cursor2.execute("SELECT * FROM LOOKUPS;")
dbSource = cursor2.fetchall()

cursor3 = sqliteConnection.cursor()
cursor3.execute("SELECT * FROM BOOK_INFO;")
dbBooks = cursor3.fetchall()

for i in range(len(dbWords)):
    if dbWords[i][3] == "ja":
        dict_DBterms[dbWords[i][1]] = dbWords[i][0]
        dict_DBtermsRev[dbWords[i][0]] = dbWords[i][1]
        dict_DBtermsRev2[dbWords[i][0]] = dbWords[i][2]
        term_listS.appendleft(dbWords[i][2])
        term_listW.appendleft(dbWords[i][1])
        timestampsDB[dbWords[i][0]] = dbWords[i][5]

for i in range(len(dbSource)):
    try:
        if dbSource[i][2] not in wordCountNew:
            wordCountNew[dbSource[i][2]] = 0
        if dbSource[i][2] in timestamps:
            if timestampsDB[dbSource[i][1]] > timestamps[dbSource[i][2]]:
                timestamps[dbSource[i][2]] = timestampsDB[dbSource[i][1]]
        else:
            timestamps[dbSource[i][2]] = timestampsDB[dbSource[i][1]]
            config["timestamps"][dbSource[i][2]] = 0
    except:
        pass

for i in range(len(dbSource)):
    if dbSource[i][2] in wordCount and dbSource[i][2] in wordCountAdded:
        wordCount[dbSource[i][2]] += 1
        try:
            if timestampsDB[dbSource[i][1]] > config["timestamps"][dbSource[i][2]]:
                wordCountNew[dbSource[i][2]] += 1
        except:
            pass
    else:
        try:
            if timestampsDB[dbSource[i][1]] > config["timestamps"][dbSource[i][2]]:
                wordCountNew[dbSource[i][2]] += 1
        except:
            pass
        wordCount[dbSource[i][2]] = 1
        wordCountAdded[dbSource[i][2]] = 0
    if dbSource[i][2] not in book_listDB:
        book_listDB.append(dbSource[i][2])
    try:
        tmpWords = lookup(dict_DBtermsRev[dbSource[i][1]], dbSource[i][5])
        stem = dict_DBtermsRev[dbSource[i][1]]
        stem2 = dict_DBtermsRev2[dbSource[i][1]]
        if tmpWords == None:
            wordCountAdded[dbSource[i][2]] += 1
            if timestampsDB[dbSource[i][1]] > config["timestamps"][dbSource[i][2]]:
                wordCountNew[dbSource[i][2]] -= 1
        elif (tmpWords[0] in history) or (stem in history) or (stem2 in history) or (tmpWords[0] in historyError) or (stem in historyError) or (stem2 in historyError):
            wordCountAdded[dbSource[i][2]] += 1
            if timestampsDB[dbSource[i][1]] > config["timestamps"][dbSource[i][2]]:
                wordCountNew[dbSource[i][2]] -= 1
    except:
        pass

for i in range(len(dbBooks)):
    if dbBooks[i][3] == "ja":
        if dbBooks[i][4] in dict_DBBooks:
            if dbBooks[i][0] in book_listDB:
                sameBook[dbBooks[i][4]] += 1
                dict_DBBooks[dbBooks[i][4]+("*" * sameBook[dbBooks[i][4]])] = dbBooks[i][0]
                book_list.append(dbBooks[i][4]+("*" * sameBook[dbBooks[i][4]]))
        else:
            if dbBooks[i][0] in book_listDB:
                dict_DBBooks[dbBooks[i][4]] = dbBooks[i][0]
                sameBook[dbBooks[i][4]] = 0
                if dbBooks[i][4] not in book_list:
                    book_list.append(dbBooks[i][4])
        
def pickBook():
    global history
    global historyError
    global cntCards
    onlyNew = False
    print("\n Words:\t\tTotal number of words from that specific book on Kindle's database\n Avaiable:\tTotal number of words from that specific book not yet processed by this script\n New:\t\tTotal number of new words from that specific book on Kindle's database compared to the last run")
    print("\n | ID\t| WORDS\t\t| AVAIABLE\t| NEW\t| BOOK NAME")
    for i in range(len(book_list)):
        print(" |", i," \t|",wordCount[dict_DBBooks[book_list[i]]]," \t\t|",(wordCount[dict_DBBooks[book_list[i]]] - wordCountAdded[dict_DBBooks[book_list[i]]]), "    \t|", wordCountNew[dict_DBBooks[book_list[i]]], " \t|",book_list[i])
    bookName = book_list[int(input("\n Enter the id of the book to mine from: "))]
    book = dict_DBBooks[bookName]
    numCards = int(input("\n Enter the number of cards to added, 0 to add all avaiable or -1 to mine only from the new words: "))
    if numCards == 0:
        numCards = 99999
    if numCards == -1:
        onlyNew = True
        numCards = int(input("\n Enter how many of the new words you want to mine, or 0 to add all avaiable: "))
        if numCards == 0:
            numCards = 99999
    for i in range(len(dbSource)):
        if dbSource[i][2] == book:
            if onlyNew:
                if dbSource[i][2] in config["timestamps"]:
                    if timestampsDB[dbSource[i][1]] > config["timestamps"][dbSource[i][2]]:
                        dict_DBsource[dbSource[i][1]] = dbSource[i][5]
                else:
                    break
            else:
                dict_DBsource[dbSource[i][1]] = dbSource[i][5]
    for j in range(len(term_listW)):
        if dict_DBterms[term_listW[j]] in dict_DBsource:
            try:
                tmpList = lookup(term_listW[j], dict_DBsource[dict_DBterms[term_listW[j]]])
                if tmpList != None:
                    subFreq = False
                    if (tmpList[0] in history) or (term_listW[j] in history) or (term_listS[j] in history) or (tmpList[0] in historyError) or (term_listW[j] in historyError) or (term_listS[j] in historyError):
                        continue
                    for q in range(len(freqlists)):
                        try:
                            tmpTerm = float(freqlists[q][tmpList[0]])
                            if tmpTerm <= freqMax:
                                subFreq = True
                        except KeyError:
                            continue
                    if cntCards < numCards:
                        if subFreq:
                            entries = []
                            for u in range(config["dictNum"]):
                                if len(entries) == 0:
                                    entry = lookup(term_listW[j], dict_DBsource[dict_DBterms[term_listW[j]]], u)
                                    if entry != None:
                                        if (entry[0] in history) or (term_listW[j] in history) or (term_listS[j] in history) or (entry[0] in historyError) or (term_listW[j] in historyError) or (term_listS[j] in historyError):
                                            continue
                                        else:
                                            entries.append(entry)
                                else:
                                    entry = lookup(entries[0][0], dict_DBsource[dict_DBterms[term_listW[j]]], u)
                                    if entry != None:
                                        if entry[1] == entries[0][1]:
                                            entries.append(entry)   
                            if len(entries) > 0:
                                furigana = ''
                                definition = '<div style="text-align: left;"><ol>'
                                for o in entries:
                                    if o[1] != "" and furigana == '':
                                        furigana = o[1]
                                    definition += '<li><i>({})</i>{}</li>'.format(dict_name[o[4]], o[2])
                                definition += '</ol></div>'
                                if config["bookName"] == 0:
                                    card = newCard([config["deckName"], config["cardType"], config["termField"], config["readField"], config["dictField"], config["sentField"], config["audioField"]], entries[0][0], furigana, definition, entries[0][3])
                                    invoke(card, entries[0][0])
                                    history.append(term_listW[j])
                                else:
                                    card = newCard([config["deckName"], config["cardType"], config["termField"], config["readField"], config["dictField"], config["sentField"], config["audioField"], config["bookField"]], entries[0][0], furigana, definition, entries[0][3], bookName.rstrip("*"))
                                    invoke(card, entries[0][0])
                                    history.append(term_listW[j])
                        else:
                            print(" Fail!    Frequency rank > {} or no frequency avaiable: ".format(freqMax), tmpList[0])
            except KeyError:
                print(" Fail!    No entry avaiable for: ", term_listW[j])
                historyError.append(term_listW[j])

pickBook()

config["timestamps"] = timestamps
with open("app_files/config.json", "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False)
with open("app_files/added.json", "w", encoding="utf-8") as file:
    json.dump(history, file, ensure_ascii=False)
with open("app_files/errorHistory.json", "w", encoding="utf-8") as file:
    json.dump(historyError, file, ensure_ascii=False)

endVar = input("\n Added cards: {}\n\n Enter 'OK' to close the script: ".format(cntCards))
