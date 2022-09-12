# Kindle2Anki

## Description
A simple Python script to create Anki cards for Japanese words from Kindle's Vocab-Builder and Yomichan dictionaries

# Features
- Fully automatic ```Word, Reading, Definition, Sentence, Audio, BookName``` Anki card creation with definitions from how many Yomichan dictionaries you want and audio from JapanesePod
- Manual selection of which book the script will mine the words from, the amount of cards to be created and the minimum frequency rank a word needs to have in order to be added
- No need to import any APKG files as the cards are created using AnkiCOnnect

## Screenshots
<table>
  <tr>
    <td> <img src="Screenshots/Kindle2Anki_running.JPG" width=auto height=auto></td>
    <td><img src="https://user-images.githubusercontent.com/99134182/188528265-f6e0777e-a033-4b5b-8abd-9b143fb722f4.JPG" width=auto height=auto></td>
    <td><img src="https://user-images.githubusercontent.com/99134182/188528262-6a6143cb-36a3-45b5-ab32-0f5d9ef93e91.JPG" width=auto height=auto></td>
    <td><img src="https://user-images.githubusercontent.com/99134182/188528266-bc099279-785e-4db8-9522-dd92a6f5f22b.JPG" width=auto height=auto></td>
  </tr>
 </table>

# Installation
- Make sure Kindle's Vocab Builder is active on
```Settings > Reading Options > Vocabulary Builder```or
```設定 > 読書オプション > 単語帳```
- Install SudachiPy
```pip install sudachipy sudachidict_full```
- Install [AnkiConnect](https://ankiweb.net/shared/info/2055492159) if you don't have it already installed
- Clone this repository

# Usage
### This script utilizes AnkiConnect, make sure you have Anki running on the background before you run the script
- Plug your kindle into your computer and grab the vocab.db file from its storage by going to ```system/vocabulary/```, or by searching for "vocab.db", and paste it in the same folder as the Kindle2Anki.py file
- Run the script
- Choose the book you want to mine from when prompted to
- Choose how many cards you want the script to generate when prompted to
- Wait for it to finish running and enter "OK" to close the script when prompted to

### First run setup
- You'll have to install your dictionaries and frequency lists, make sure you have all of them in the same folder as the Kindle2Anki.py file
- The script is not compatible with Pitch Accent dictionaries
- The script is also not compatible with multiple-frequency frequency lists, please use one with only 1 frequency per word
- Be careful when entering your deck and card info, any mistypes will result in the script not working properly

## Note that:
- Anki doesn't let you create a card with an empty first field, make sure you set your "Term" field to your note's first field.
- This script will only create cards for japanese words
- This script will not generate any duplicate cards
- The cards are generated automatically, flaws are expected ~~even more with kindle's shitty text parser~~
- This script will only try to create a card for a specific word once, if you delete a faulty card it will not be created again on the next run. As you run the script more times the amount of faulty cards is expected to diminish
- The indicated number of new cards is somewhat off most of the time, it is only a visual indicator and don't actually affect the number of cards generated
