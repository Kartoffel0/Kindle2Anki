# Kindle2Anki
A simple command line script to create ```Word, Reading, Definition, Sentence, Audio``` Anki cards from Kindle's Vocab-Builder's database

# Requirements
This script requires [SudachiPy](https://pypi.org/project/SudachiDict-full/)
```
pip install SudachiDict-full
```
This script utilizes [Yomichan dictionaries](https://github.com/FooSoft/yomichan#dictionaries) and [ranked frequency lists](https://drive.google.com/drive/folders/1g1drkFzokc8KNpsPHoRmDJ4OtMTWFuXi)

The script is not compatible with multiple-frequency frequency lists, please use one with only 1 frequency per word

# Usage
The first time you run the script you'll have to install your dictionaries and frequency lists, make sure you have all of them in the same folder as the Kindle2Anki.py file

Usage after you finish the first run config:
- plug your kindle into your computer
- Grab the vocab.db file manually from your kindle's system folder, or just search for "vocab" , and paste it in the same folder as the Kindle2Anki.py file
- Run the script
- Choose the book you want to mine from
- Choose how many cards you want the script to generate, it doesn't account for the duplicates so the actual number of generated cards probably is lower

Note that:
- The script will only create cards for japanese words
- The script will not generate duplicate cards
- The cards are generated automatically, flaws are expected(even more with kindle's shitty text parser)
- The script will only try to create a card for a specific word once, if you delete a faulty card it will not be created again on the next run. As you run the script more times the amount of faulty cards is expected to diminish
