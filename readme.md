# MTG test deck builder

Generate quick and dirty cards from a standard decklist for print-at-home playtesting.

## Installation

1. Clone this repo
2. Install dependencies with `pip install -r requirements.txt`

## Usage

Ensure you have a deck list .txt file with one card per line and each line containing the quantity of that card, a space, then it's name. E.g.

```text
1 Akroma's Will
1 Apex Altisaur
1 Arcane Signet
3 Mountain
...
```

Then run the script with `python generate.py` and follow the instructions.

### Output

The application will output a series of images in an `output/` directory, each one containing a page of cards. Import these into a word processor and print at A4 size and you'll be able to cut them out to the right size. 

There are two possible output formats which you can select once the script launches:


#### Text only

![sample output page with plain text detail of several MTG cards](https://bitbucket.org/pangolinpaw/test_deck/raw/d7c130d7de5ffcbdedab4687c31d6a19a1b49ea5/assets/sample_output.png)

The generated cards are intended to insert into sleeves in front of existing cards and roughly overlay the card text area.

#### Full cards

![sample output page with images of several MTG cards arranged in a grid](https://bitbucket.org/pangolinpaw/test_deck/raw/138f46f9961f2283c4c1a05c413f78aed05314fe/assets/sample_output_02.png)

The generated cards are intended to insert into sleeves and are roughly the same size as official cards.

