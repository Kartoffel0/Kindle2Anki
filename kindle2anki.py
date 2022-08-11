from logging import exception
import time
import zipfile
import os
import json
from sudachipy import dictionary
import urllib.request
import re
import sqlite3
from collections import deque
from datetime import datetime

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

def loadJson(filename, default):
    try:
        return json.load(open(f"{filename}.json", encoding="utf-8"))
    except:
        return default

try:
    jpod = json.load(open("app_files/jpodFiles.json", encoding="utf-8"))
except:
    print(" Japanesepod's avaiable audio database not found!\n Please download it from Kindle2Anki's github repository!")
    jpod = []

try:
    freqMain = json.load(open("app_files/mainFreq.json", encoding="utf-8"))
except:
    freqMain = {}

config = loadJson("app_files/config", {"first_run":1})
dicts = loadJson("app_files/dicts", [])
freqlists = loadJson("app_files/freqLists", [])
history = loadJson("app_files/added", [])
historyError = loadJson("app_files/errorHistory", [])

def add_dict(dictN):
    dict = {}
    fileNames = os.listdir("app_files/{}".format(dictN))
    dictName = json.load(open("app_files/{}/index.json".format(dictN), encoding="utf-8"))["title"]
    fileNames.remove("index.json")
    for i in fileNames:
        data = json.load(open("app_files/{}/{}".format(dictN, i), encoding="utf-8"))
        for j in data:
            if (j[0] in dict):
                try:
                    if j[1] == freqMain[j[0]]:
                        dict[j[0]] = j
                except KeyError:
                    continue
            else:
                dict[j[0]] = j
    return [dictName, dict]

def add_freqList(freqN):
    freqlist = {}
    fileNames = os.listdir("app_files/freq/{}".format(freqN))
    fileNames.remove("index.json")
    for i in fileNames:
        data = json.load(open("app_files/freq/{}/{}".format(freqN, i), encoding="utf-8"))
        for j in data:
            if type(j[2]) is dict:
                if "frequency" in j[2]:
                    freqlist[j[0]] = j[2]["frequency"]
            elif re.search("★*\(\d+\)", j[2]) is not None:
                freqlist[j[0]] = j[2]
            else:
                if re.search("/", str(j[2])):
                    freqlist[j[0]] = int(j[2].split("/")[0])
                else:
                    freqlist[j[0]] = j[2]
    return freqlist

print(" Kindle2Anki - https://github.com/Kartoffel0/Kindle2Anki")
if config["first_run"] == 1:
    print("\n This will only be asked once,\n on the next run you'll not have to inform everything again.")
    dict_Num = int(input("\n Please inform how many dictionaries you want to add:\n "))
    print("\n Ensure the zips are on the same directory as this script")
    config["dictNum"] = dict_Num
    for i in range(dict_Num):
        with zipfile.ZipFile("{}".format(input("\n Enter the filename for your {}° dictionary:\n ".format(i+1))), 'r') as zip_ref:
            zip_ref.extractall("app_files/{}".format(i))
        dict = add_dict(i)
        config["dict_Names"].append(dict[0])
        dicts.append(dict[1])
    freqNum = int(input("\n This script don't support multi frequency per word frequency lists,\n make sure the frequency list you'll add has only one frequency per word\n\n Please inform how many frequency lists you want to add:\n "))
    for j in range(freqNum):
        with zipfile.ZipFile("{}".format(input("\n Enter the filename for your {}° frequency list:\n ".format(j+1))), 'r') as zip_ref:
            zip_ref.extractall("app_files/freq/{}".format(j))
        freqlists.append(add_freqList(j))
    if freqNum > 0:
        freqMax = int(input("\n Please inform the maximum frequency limit\n any words with a frequency rank superior to\n that will not be processed, or 0 to not set a limit:\n "))
        config["freqMax"] = freqMax
    else:
        config["freqMax"] = 0
    config["first_run"] = 0
    deck = input("\n Please inform the name of the deck(!!!case sensitive!!!) where you want the cards to be added:\n ")
    config["deckName"] = deck
    cardType = input("\n Please inform the Note Type(!!!case sensitive!!!) you want to use as template for the added cards:\n ")
    config["cardType"] = cardType
    termField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Word' to be:\n ")
    config["termField"] = termField
    readField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Reading' to be:\n ")
    config["readField"] = readField
    dictField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Definitions' to be:\n ")
    config["dictField"] = dictField
    sentField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Sentence' to be:\n ")
    config["sentField"] = sentField
    audioField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Audio' to be:\n ")
    config["audioField"] = audioField
    freqField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Word Frequency' to be, or enter 0 if you don't want it on your cards:\n")
    config["freqField"] = freqField
    nameField = input("\n Please inform the field name(!!!case sensitive!!!) where you want the 'Book Name' to be\n Enter 0 if you don't want to add the book name to your cards:\n ")
    if nameField != 0:
        config["bookName"] = 1
        config["bookField"] = nameField
    checkScope = int(input("\n Please inform where do you want the script to check for duplicates,\n enter 0 to check for them only on the deck you specified or 1 to check for them on your whole collection:\n "))
    config["scope"] = "deck" if checkScope == 0 else "collection"
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

dict_name = config["dict_Names"]
freqMax = config["freqMax"]
try:
    timestamps = config["timestamps"].copy()
except:
    timestamps, config["timestamps"] = {}, {}
    
def newCard(config, args):
    global jpod
    tmpJpod = (args["reading"]+"_"+args["term"])
    card = {"action": "addNote", "version": 6, "params": {"note":{"deckName": config["deckName"], "modelName": config["cardType"], "fields": {config["termField"]: args["term"], config["readField"]: args["reading"], config["dictField"]: args["definition"].replace("\n", "<br>"), config["sentField"]: args["sentence"]}, "options": {"allowDuplicate": False, "duplicateScope": "deck", "duplicateScopeOptions": {"deckName": config["deckName"], "checkChildren": True, "checkAllModels": True}}, "tags": ["Kindle2Anki"]}}}
    if tmpJpod in jpod:
        card["params"]["note"]["audio"] = [{"filename": "{} - {}.mp3".format(args["reading"], args["term"]),"url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji={}&kana={}".format(args["term"], args["reading"]), "fields": [config["audioField"]]}]
    else:
        print(" Warning!    No audio avaiable: ", args["term"])
    if "frequency" in args:
        card["params"]["note"]["fields"][config["freqField"]] = args["frequency"]
    if "bookName" in args:
        card["params"]["note"]["fields"][config["bookField"]] = args["bookName"]
    return card

def invoke(params, term="error"):
    global cntCards
    global historyError
    global config
    time.sleep(1)
    try:
        if config["scope"] == "deck":
            requestJson = json.dumps(params).encode('utf-8')
        else:
            params["params"]["note"]["options"]["duplicateScope"] = "collection"
            params["params"]["note"]["options"]["duplicateScopeOptions"].pop("deckName", None)
            params["params"]["note"]["options"]["duplicateScopeOptions"].pop("checkChildren", None)
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
        
def lookup(term, source, dictN=0, exact=0):
    if dictN == -1:
        for d in range(config["dictNum"]):
            tmpLP = lookup(term, source, d)
            if tmpLP is not None:
                return tmpLP
        return None
    else:
        if exact == 1:
            try:
                definition = dicts[dictN][term]
                return [term, definition[1], definition[5][0], source.strip(), dictN]
            except KeyError:
                return None
        else:
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
        tmpWords = lookup(dict_DBtermsRev[dbSource[i][1]], dbSource[i][5], -1)
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
    global book
    onlyNew = False
    print("\n Words:\t\tTotal number of words from that book on Kindle's database\n Avaiable:\tTotal amount of those words not yet processed by this script\n New:\t\tTotal amount of those words that were added since the indicated 'last mined from' date")
    print("\n | ID\t| WORDS\t\t| AVAIABLE\t| NEW \t(YY/MM/DD) | BOOK NAME")
    for i in range(len(book_list)):
        if dict_DBBooks[book_list[i]] in config["timestamps"] and config["timestamps"][dict_DBBooks[book_list[i]]] != 0:
            print(" |", i," \t|",wordCount[dict_DBBooks[book_list[i]]]," \t\t|",(wordCount[dict_DBBooks[book_list[i]]] - wordCountAdded[dict_DBBooks[book_list[i]]]), "    \t|", wordCountNew[dict_DBBooks[book_list[i]]], " \t({})".format(str(datetime.fromtimestamp(config["timestamps"][dict_DBBooks[book_list[i]]]/1000)).split(" ")[0].replace("-", "/")[2:]), "|",book_list[i])
        else:
            print(" |", i," \t|",wordCount[dict_DBBooks[book_list[i]]]," \t\t|",(wordCount[dict_DBBooks[book_list[i]]] - wordCountAdded[dict_DBBooks[book_list[i]]]), "    \t|", wordCountNew[dict_DBBooks[book_list[i]]], " \t(00/00/00)", "|",book_list[i])
    bookName = book_list[int(input("\n Enter the ID of the book to mine from:\n "))]
    book = dict_DBBooks[bookName]
    numCards = int(input("\n Enter the number of cards to be added:\n You can also enter 0 to add all avaiable or -1 to mine from the new words only:\n "))
    if numCards == 0:
        numCards = 99999
    if numCards == -1:
        onlyNew = True
        numCards = int(input("\n Enter how many of the new words you want to mine, or 0 to add all avaiable:\n "))
        if numCards == 0:
            numCards = 99999
    for i in range(len(dbSource)):
        if dbSource[i][2] == book:
            if onlyNew:
                if dbSource[i][2] in config["timestamps"]:
                    if timestampsDB[dbSource[i][1]] > config["timestamps"][dbSource[i][2]]:
                        dict_DBsource[dbSource[i][1]] = dbSource[i][5]
                else:
                    dict_DBsource[dbSource[i][1]] = dbSource[i][5]
            else:
                dict_DBsource[dbSource[i][1]] = dbSource[i][5]
    for j in range(len(term_listW)):
        if dict_DBterms[term_listW[j]] in dict_DBsource:
            try:
                tmpList = lookup(term_listW[j], dict_DBsource[dict_DBterms[term_listW[j]]], -1)
                freqs = []
                if tmpList != None:
                    if freqMax == 0:
                        subFreq = True
                    else:
                        subFreq = False
                    if (tmpList[0] in history) or (term_listW[j] in history) or (term_listS[j] in history) or (tmpList[0] in historyError) or (term_listW[j] in historyError) or (term_listS[j] in historyError):
                        continue
                    for q in range(len(freqlists)):
                        try:
                            tmpTerm = float(freqlists[q][tmpList[0]])
                            if tmpTerm <= freqMax or subFreq == True:
                                subFreq = True
                                freqs.append(tmpTerm)
                        except KeyError:
                            continue
                    if len(freqs) == 0:
                        freqs.append(123456789)
                    if cntCards < numCards:
                        if subFreq:
                            entries = []
                            for u in range(config["dictNum"]):
                                if len(entries) == 0:
                                    entry = lookup(term_listW[j], dict_DBsource[dict_DBterms[term_listW[j]]], u, 1)
                                    if entry != None:
                                        if (entry[0] in history) or (term_listW[j] in history) or (term_listS[j] in history) or (entry[0] in historyError) or (term_listW[j] in historyError) or (term_listS[j] in historyError):
                                            continue
                                        else:
                                            entries.append(entry)
                                else:
                                    entry = lookup(entries[0][0], dict_DBsource[dict_DBterms[term_listW[j]]], u, 1)
                                    if entry != None:
                                        if entry[1] == entries[0][1] or entry[0] == entries[0][1] or ((entries[0][1] == '' or entry[1] == '') and entry[0] == entries[0][0]):
                                            entries.append(entry)   
                            if len(entries) == 0 or len(entries) < config["dictNum"]:
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
                                            if entry[1] == entries[0][1] or entry[0] == entries[0][1] or ((entries[0][1] == '' or entry[1] == '') and entry[0] == entries[0][0]):
                                                if entry not in entries:
                                                    entries.append(entry)   
                            if len(entries) > 0:
                                furigana = ''
                                definition = '<div style="text-align: left;"><ol>'
                                for o in entries:
                                    if o[1] != "" and furigana == '':
                                        furigana = o[1]
                                    definition += '<li><i>({})</i>{}</li>'.format(dict_name[o[4]], o[2])
                                definition += '</ol></div>'
                                args = {"term": entries[0][0], "reading": furigana, "definition": definition, "sentence": entries[0][3]}
                                if config["bookName"] != 0:
                                    args["bookName"] = bookName.rstrip("*")
                                if config["freqField"] != 0:
                                    args["frequency"] = str(int(min(freqs))).replace("123456789", "")
                                card = newCard(config, args)
                                invoke(card, entries[0][0])
                                history.append(term_listW[j])
                        else:
                            print(" Fail!    Frequency rank > {} or no frequency avaiable: ".format(freqMax), tmpList[0])
            except Exception as e:
                print(" Fail!    ", term_listW[j], e)
                historyError.append(term_listW[j])

pickBook()

with open("app_files/added.json", "w", encoding="utf-8") as file:
    json.dump(history, file, ensure_ascii=False)
with open("app_files/errorHistory.json", "w", encoding="utf-8") as file:
    json.dump(historyError, file, ensure_ascii=False)

if int(input("\n Added cards: {}\n Enter 0 to update the 'last mined from' date and reset the 'new' card counter, or -1 keep it as it is now:\n ".format(cntCards))) == 0:
    config["timestamps"][book] = timestamps[book]
    with open("app_files/config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False)

endVar = input(" Done!\n\n Enter 'OK' to close the script:\n ")
