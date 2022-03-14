import time
import zipfile
import os
import json
from sudachipy import dictionary
import urllib.request
import re
import sqlite3

"""
If you run into any problems while trying to use this script 
you can contact me on discord Kartoffel#7357 and I'll try to fix it
no guarantees tho
"""

TKZR = dictionary.Dictionary(dict_type="full").create()

dictsFile = open("app_files/dicts.json", encoding="utf-8")
dicts = json.load(dictsFile)

jpodFile = open("app_files/jpodFiles.json", encoding="utf-8")
jpod = json.load(jpodFile)

freqMainFile = open("app_files/mainFreq.json", encoding="utf-8")
freqMain = json.load(freqMainFile)

historyFile = open("app_files/added.json", encoding="utf-8")
history = json.load(historyFile)

historyFile2 = open("app_files/FreqHigh.json", encoding="utf-8")
historyFreq = json.load(historyFile2)

historyFile3 = open("app_files/errorHistory.json", encoding="utf-8")
historyError = json.load(historyFile3)

freqListsFile = open("app_files/freqlists.json", encoding="utf-8")
freqlists = json.load(freqListsFile)

configFile = open("app_files/config.json", encoding="utf-8")
config = json.load(configFile)
dict_name = config["dict_Names"]
freqMax = config["freqMax"]

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
            if re.search("/", str(j[2])):
                freqlists[freqN][j[0]] = int(j[2].split("/")[0])
            else:
                freqlists[freqN][j[0]] = j[2]

print("Kindle2Anki")
if config["first_run"] == 1:
    print("\n\nThis will only be asked once,\non the next run you'll not have to inform everything again.")
    dict_Num = int(input("\nPlease inform how many dictionaries you want to add: "))
    print("\nEnsure the zips are on the same directory as this script")
    config["dictNum"] = dict_Num
    for i in range(dict_Num):
        with zipfile.ZipFile("{}".format(input("\nEnter the filename for your {}° dictionary: ".format(i+1))), 'r') as zip_ref:
            zip_ref.extractall("app_files/{}".format(i))
        appendDict2()
        add_dict(i)
    freqNum = int(input("\nThis script don't support multi frequency per word frequency lists,\nmake sure the frequency list you'll add has only one frequency per word\n\nPlease inform how many frequency lists you want to add,\nyou have to add at least one: "))
    for j in range(freqNum):
        with zipfile.ZipFile("{}".format(input("\nEnter the filename for your {}° frequency list: ".format(j+1))), 'r') as zip_ref:
            zip_ref.extractall("app_files/freq/{}".format(j))
        appendDict()
        add_freqList(j)
    freqMax = int(input("\nPlease inform the maximum frequency limit\nany words with a frequency rank superior to\nthat will not be processed: "))
    config["freqMax"] = freqMax
    config["first_run"] = 0
    deck = input("\nPlease inform the name of the deck(!!!case sensitive!!!) where you want the cards to be added: ")
    config["deckName"] = deck
    cardType = input("\nPlease inform the card type(!!!case sensitive!!!) you want to use as template for the added cards: ")
    config["cardType"] = cardType
    termField = input("\nPlease inform the field name(!!!case sensitive!!!) where you want the 'Word' to be: ")
    config["termField"] = termField
    readField = input("\nPlease inform the field name(!!!case sensitive!!!) where you want the 'Reading' to be: ")
    config["readField"] = readField
    dictField = input("\nPlease inform the field name(!!!case sensitive!!!) where you want the 'Definitions' to be: ")
    config["dictField"] = dictField
    sentField = input("\nPlease inform the field name(!!!case sensitive!!!) where you want the 'Sentence' to be: ")
    config["sentField"] = sentField
    audioField = input("\nPlease inform the field name(!!!case sensitive!!!) where you want the 'Audio' to be: ")
    config["audioField"] = audioField
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
    print("\nDone!\n")

def newCard(deckInfo, term, reading, defs, source):
    global jpod
    tmpJpod = (reading+"_"+term)
    if tmpJpod in jpod:
        return {"action": "addNote", "version": 6, "params": {"note":{"deckName": deckInfo[0], "modelName": deckInfo[1], "fields": {deckInfo[2]: term, deckInfo[3]: reading, deckInfo[4]: defs.replace("\n", "<br>"), deckInfo[5]: source}, "options": {"allowDuplicate": False, "duplicateScope": "deck", "duplicateScopeOptions": {"deckName": deckInfo[0], "checkChildren": False, "checkAllModels": False}}, "tags": ["Kindle2Anki"], "audio": [{"filename": "{} - {}.mp3".format(reading, term),"url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji={}&kana={}".format(term, reading), "fields": [deckInfo[6]]}]}}}
    else:
        print("Warning! Card created without audio: ", term)
        return {"action": "addNote", "version": 6, "params": {"note":{"deckName": deckInfo[0], "modelName": deckInfo[1], "fields": {deckInfo[2]: term, deckInfo[3]: reading, deckInfo[4]: defs.replace("\n", "<br>"), deckInfo[5]: source}, "options": {"allowDuplicate": False, "duplicateScope": "deck", "duplicateScopeOptions": {"deckName": deckInfo[0], "checkChildren": False, "checkAllModels": False}}, "tags": ["Kindle2Anki"]}}}

def invoke(action, params, term="error"):
    global history
    global historyError
    history.append(term)
    time.sleep(3)
    try:
        requestJson = json.dumps(params).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    except:
        historyError.append(term)
        print("Fail! Failed to add: ", term)

def deconjug(term, source, mode=0):
    tkTerm = TKZR.tokenize(term)
    tkSource = TKZR.tokenize(source)
    for i in range(len(tkSource)):
        if (re.search(term, tkSource[i].surface())) or (re.search(tkTerm[0].dictionary_form(), tkSource[i].dictionary_form()) or (re.search(tkTerm[0].normalized_form(), tkSource[i].normalized_form()))):
            if mode == 0:
                return tkSource[i].dictionary_form()
            else:
                return tkSource[i].normalized_form()

def lookup(term, source, dictN=0):
    global dicts
    try:
        definition = dicts[dictN][term]
        return [term, definition[1], definition[5][0], source.strip(), dictN]
    except KeyError:
        try:
            tmpTerm = term.strip()
            tmpTerm = tmpTerm[0:-1]
            tmpTerm += "い"
            definition = dicts[dictN][tmpTerm]
            return [tmpTerm, definition[1], definition[5][0], source.strip(), dictN]
        except KeyError:
            try:
                tmpTerm = term.strip()
                tmpTerm += "い"
                definition = dicts[dictN][tmpTerm]
                return [tmpTerm, definition[1], definition[5][0], source.strip(), dictN]
            except KeyError:
                try:
                    termTK = deconjug(term, source)
                    definition = dicts[dictN][termTK]
                    return [termTK, definition[1], definition[5][0], source.strip(), dictN]
                except KeyError:
                    try:
                        termTK = deconjug(term, source, 1)
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


dict_DBterms = {}
dict_DBtermsRev = {}
term_list = []
dict_DBsource = {}
dict_DBBooks = {}
book_list = []
book_listDB = []
wordCount = {}
wordCountAdded = {}
cnt = 0

for i in range(len(dbWords)):
    if dbWords[i][3] == "ja":
        dict_DBterms[dbWords[i][2]] = dbWords[i][0]
        dict_DBtermsRev[dbWords[i][0]] = dbWords[i][2]
        term_list.append(dbWords[i][2])

for i in range(len(dbSource)):
    try:
        wordCount[dbSource[i][2]] += 1
    except:
        wordCount[dbSource[i][2]] = 1
        wordCountAdded[dbSource[i][2]] = 0
    if dbSource[i][2] not in book_listDB:
        book_listDB.append(dbSource[i][2])

for i in range(len(dbSource)):
    if re.search("ja", dbSource[i][1]):
        try:
            tmpWords = lookup(dict_DBtermsRev[dbSource[i][1]], dbSource[i][5])
            stem = dict_DBtermsRev[dbSource[i][1]]
            if tmpWords != None:
                if (tmpWords[0] in history) or (stem in history) or (tmpWords[0] in historyFreq) or (stem in historyFreq) or (tmpWords[0] in historyError) or (stem in historyError):
                    wordCountAdded[dbSource[i][2]] += 1
        except:
            wordCountAdded[dbSource[i][2]] += 1

for i in range(len(dbBooks)):
    if dbBooks[i][3] == "ja":
        dict_DBBooks[dbBooks[i][4]] = dbBooks[i][0]
        if (dbBooks[i][4] not in book_list) and (dbBooks[i][0] in book_listDB):
            book_list.append(dbBooks[i][4])

def pickBook(numCards=9999):
    global historyFreq
    global historyError
    global cnt
    print("\n\n")
    for i in range(len(book_list)):
        print("id:",i,"\t|","Words:",wordCount[dict_DBBooks[book_list[i]]],"\t|","New:",(wordCount[dict_DBBooks[book_list[i]]] - wordCountAdded[dict_DBBooks[book_list[i]]]), "\t|",book_list[i])
    book = dict_DBBooks[book_list[int(input("\nEnter the id of the book to mine from: "))]]
    numCards = int(input("\nEnter the number of words to be processed, or 0 to try to add all avaiable: "))
    if numCards == 0:
        numCards = 9999
    cnt = 0
    for i in range(len(dbSource)):
        if dbSource[i][2] == book:
            dict_DBsource[dbSource[i][1]] = dbSource[i][5]
    for j in range(len(term_list)):
        if dict_DBterms[term_list[j]] in dict_DBsource:
            try:
                tmpList = lookup(term_list[j], dict_DBsource[dict_DBterms[term_list[j]]])
                if tmpList != None:
                    subFreq = False
                    if (tmpList[0] in history) or (term_list[j] in history) or (tmpList[0] in historyFreq) or (term_list[j] in historyFreq) or (tmpList[0] in historyError) or (term_list[j] in historyError):
                        continue
                    for q in range(len(freqlists)):
                        try:
                            tmpTerm = float(freqlists[q][tmpList[0]])
                            if tmpTerm <= freqMax:
                                subFreq = True
                        except KeyError:
                            continue
                    if cnt <= numCards:
                        if subFreq:
                            entries = []
                            for u in range(config["dictNum"]):
                                entry = lookup(term_list[j], dict_DBsource[dict_DBterms[term_list[j]]], u)
                                if entry != None:
                                    if (entry[0] in history) or (term_list[j] in history) or (entry[0] in historyFreq) or (term_list[j] in historyFreq) or (entry[0] in historyError) or (term_list[j] in historyError):
                                        continue
                                    else:
                                        entries.append(entry)
                            if len(entries) > 0:
                                furigana = ''
                                definition = '<div style="text-align: left;"><ol>'
                                for o in entries:
                                    if o[1] != "":
                                        furigana = o[1]
                                    definition += '<li><i>({})</i>{}</li>'.format(dict_name[o[4]], o[2])
                                definition += '</ol></div>'
                                card = newCard([config["deckName"], config["cardType"], config["termField"], config["readField"], config["dictField"], config["sentField"], config["audioField"]], entries[0][0], furigana, definition, entries[0][3])
                                invoke("addNote", card, entries[0][0])
                                print(cnt, "Success: ", entries[0][0])
                                cnt += 1
                        else:
                            print("Fail! Freq rank > {} or no frequency avaiable: ".format(freqMax), tmpList[0])
                            historyFreq.append(tmpList[0])
            except KeyError:
                print("Fail! No entry avaiable for: ", term_list[j])
                historyError.append(term_list[j])

pickBook()

with open("app_files/added.json", "w", encoding="utf-8") as file:
    json.dump(history, file, ensure_ascii=False)
with open("app_files/FreqHigh.json", "w", encoding="utf-8") as file:
    json.dump(historyFreq, file, ensure_ascii=False)
with open("app_files/errorHistory.json", "w", encoding="utf-8") as file:
    json.dump(historyError, file, ensure_ascii=False)

endVar = input("\n\nAdded cards(not excluding the ones that were duplicates so the actual number of created cards probably is lower): {}\n\nEnter 'OK' to close the script: ".format(cnt))