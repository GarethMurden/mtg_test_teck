import json
import math
import numpy as np
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests
import time
from tkinter import Tk
from tkinter import filedialog

dirname, _ = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

VERSION = 'v1.0'

CARD_SIZE = {
    'text':{
        'height': 450,
        'width': 750,
        'margin': 20
    },
    'image':{
        'height': 680, # 88mm
        'width':   488, # 63mm
    }
}

BASIC_LANDS = [
    'Mountain',
    'Swamp',
    'Island',
    'Forest',
    'Plains'
]

def cleanup(temp_files):
    for filename in temp_files:
        if os.path.exists(filename):
            os.remove(filename)

def combine_full_cards(image_files):
    # Inspired by https://stackoverflow.com/a/30228789
    rotated_images = []
    for image_file in image_files:
        image = Image.open(image_file)
        card = image.thumbnail(
            (
                CARD_SIZE['image']['width'],
                CARD_SIZE['image']['height']
            )
        )
        image = image.rotate(90, expand=True)
        rotated_images.append(image)

    blank_image = Image.new("RGB", (CARD_SIZE['image']['height'], CARD_SIZE['image']['width']), (255, 255, 255))
    row_files = []
    cards_per_row = 2
    for row_num in range(0, len(rotated_images), cards_per_row):
        images = rotated_images[row_num:row_num+cards_per_row]
        while len(images) < cards_per_row:
            images.append(blank_image)
        try:
            images = np.hstack(images)
        except:
            for image in images:
                image.show()
                input()
        images = Image.fromarray(images)
        save_as = f'{THIS_DIRECTORY}images{os.sep}row_{str(int(row_num / cards_per_row) +1).rjust(2, "0")}.png'
        images.save(save_as)
        row_files.append(save_as)

    blank_row = np.hstack([blank_image for x in range(cards_per_row)])
    blank_row = Image.fromarray(blank_row)
    rows_per_page = 4
    for row_num in range(0, len(row_files), rows_per_page):
        images = [Image.open(row) for row in row_files[row_num:row_num+rows_per_page]]
        while len(images) < rows_per_page:
            images.append(blank_row)
        images = np.vstack(images)
        images = Image.fromarray(images)
        save_as = f'{THIS_DIRECTORY}output{os.sep}page_{str(int(row_num / rows_per_page) +1).rjust(2, "0")}.png'
        images.save(save_as)
    cleanup(row_files)

def combine_text_cards(card_list):
    row_files = []
    blank_image = Image.new("RGB", (CARD_SIZE['text']['width'], CARD_SIZE['text']['height']), (255, 255, 255))
    cards_per_row = 3
    for row_num in range(0, len(card_list), cards_per_row):
        images = [Image.open(card) for card in card_list[row_num:row_num+cards_per_row]]
        while len(images) < cards_per_row:
            images.append(blank_image)
        images = np.hstack(images)
        images = Image.fromarray(images)
        save_as = f'{THIS_DIRECTORY}images{os.sep}row_{str(int(row_num / cards_per_row) +1).rjust(2, "0")}.png'
        images.save(save_as)
        row_files.append(save_as)
    blank_row = Image.new("RGB", (CARD_SIZE['text']['width'] * cards_per_row, CARD_SIZE['text']['height']), (255, 255, 255))
    rows_per_page = 7
    for row_num in range(0, len(row_files), rows_per_page):
        images = [Image.open(row) for row in row_files[row_num:row_num+rows_per_page]]
        while len(images) < rows_per_page:
            images.append(blank_row)
        images = np.vstack(images)
        images = Image.fromarray(images)
        save_as = f'{THIS_DIRECTORY}output{os.sep}page_{str(int(row_num / rows_per_page) +1).rjust(2, "0")}.png'
        images.save(save_as)
    return row_files

def draw_card(card):
    background = Image.new("RGB", (CARD_SIZE['text']['width'], CARD_SIZE['text']['height']), (255, 255, 255))
    draw = ImageDraw.Draw(background)
    icon_font = ImageFont.truetype(f'{THIS_DIRECTORY}fonts{os.sep}PlanewalkerDings02.ttf', 45)
    # Cost
    cost_lookup = {
        'W':'a',    # white
        'U':'b',    # blue
        'B':'c',    # black
        'R':'d',    # red
        'G':'e',    # green
        'X':'x',    # X
        'P':'i'     # phyrexian
    }
    mana_cost = card['mana_cost'].replace('{','').replace('}','')
    formatted_cost = []
    for char in mana_cost:
        formatted_cost.append(cost_lookup.get(char, char))
    mana_cost = ''.join(formatted_cost)
    draw.text(
        (CARD_SIZE['text']['width'] - icon_font.getlength(mana_cost) - CARD_SIZE['text']['margin'], CARD_SIZE['text']['margin']),
        mana_cost,
        (  0,  0,  0),
        font=icon_font
    )
    # Title
    title_font = ImageFont.truetype(f'{THIS_DIRECTORY}fonts{os.sep}Magicmedieval-pRV1.ttf', 50)
    name, line_count = wrap_text(card['name'], title_font, CARD_SIZE['text']['width'] - icon_font.getlength(mana_cost) - CARD_SIZE['text']['margin'])
    draw.text(
        (CARD_SIZE['text']['margin'], CARD_SIZE['text']['margin']),
        name,
        (  0,  0,  0),
        font=title_font
    )
    (_, title_height), _ = title_font.font.getsize(name)
    title_height = title_height * line_count
    
    font = ImageFont.truetype(f'{THIS_DIRECTORY}fonts{os.sep}Roboto-Regular.ttf', 30)
    # Types
    draw.text(
        (CARD_SIZE['text']['margin'], title_height + 25),
        card['type'],
        (  0,  0,  0),
        font=font
    )
    # Text
    (_, types_height), _ = title_font.font.getsize(card['type'])
    start_height = title_height + 25 + types_height + 25
    card_text, _ = wrap_text(card['text'], font, CARD_SIZE['text']['width'] - (CARD_SIZE['text']['margin'] * 2))
    draw.text(
        (CARD_SIZE['text']['margin'], start_height),
        card_text,
        (  0,  0,  0),
        font=font
    )
    # Combat
    (combat_width, combat_height), _ = title_font.font.getsize(card['combat'])
    draw.text(
        (CARD_SIZE['text']['width'] - combat_width - CARD_SIZE['text']['margin'], CARD_SIZE['text']['height'] - combat_height - CARD_SIZE['text']['margin']),
        card['combat'],
        (  0,  0,  0),
        font=font
    )
    save_as = f'{THIS_DIRECTORY}images{os.sep}{file_safe_name(card['name'])}.png'
    background.save(save_as)
    return save_as

def file_safe_name(card_name):
    return card_name.replace('/', '-').replace('\\', '-')

def generate_deck(cards, mode, include_lands):
    card_details = []
    if not include_lands:
        cards = [card for card in cards if card['name'] not in BASIC_LANDS]
        print(f' Fetching data for {len(cards)} cards (lands excluded)')
    else:
        print(f' Fetching data for {len(cards)} cards')
    for counter, card in enumerate(cards):
        progress(counter +1, len(cards))
        detail = get_detail(card['name'])
        if detail is not None:
            card_details += detail
    card_images = []
    if mode == 'image':
        print('\n Downloading images')
        for counter, card in enumerate(card_details):
            progress(counter +1, len(card_details))
            image = get_image(card['name'], card['image'])
            if image is not None:
                card_images.append(image)
    else:
        print('\n Drawing plain text cards')
        for counter, card in enumerate(card_details):
            progress(counter +1, len(card_details))
            image = draw_card(card)
            if image is not None:
                card_images.append(image)
    print('\n Preparing printable pages')
    if mode == 'image':
        combine_full_cards(card_images)
    else:
        combine_text_cards(card_images)

def get_detail(card_name):
    sides = load_cache(card_name)
    if sides is None:
        time.sleep(0.25) # Rate limit
        sides = []
        url = f'https://api.scryfall.com/cards/named?fuzzy={card_name.replace(" ", "+")}'
        r = requests.get(
            url,
            headers={
                'User-Agent':'DeckTester/{VERSION}',
                'Accept':'application/json'
            }
        )
        sides = []
        if r.status_code == 200:
            if 'card_faces' in r.json():
                faces = r.json()['card_faces']
            else:
                faces = [r.json()]
            for face in faces:
                face_data = {
                    'name':face['name'],
                    'image':face['image_uris']['normal'],
                    'mana_cost':face['mana_cost'],
                    'type':face['type_line'],
                    'text':face['oracle_text'] + f' ({r.json()["name"]})',
                    'combat':'',
                    'loyalty':''
                }
                if 'power' in face:
                    face_data['combat'] = f"{face['power']}/{face['toughness']}"
                if '' in face:
                    face_data['loyalty'] = face['loyalty']
                sides.append(face_data)
        save_cache(sides, f'{THIS_DIRECTORY}data{os.sep}{file_safe_name(card_name)}.json')
    return sides

def get_image(name, url):
    image_path = f'{THIS_DIRECTORY}images{os.sep}{name}.jpg'
    if not os.path.exists(image_path):
        r = requests.get(url)
        with open(image_path, 'wb') as f:
            f.write(r.content)
    return image_path

def load_cache(card_name):
    cache_file = f'{THIS_DIRECTORY}data{os.sep}{file_safe_name(card_name)}.json'
    if os.path.exists(cache_file):
        return load_json(cache_file)
    else:
        return None

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.loads(f.read()) 

def progress(current, max):
    width = 2
    padding = 50
    perc = round((float(current) / max) * 100, 1)
    rounded_perc = int(round(perc,0) / width)
    bar = rounded_perc * '#'
    bar = bar.ljust(padding, '-')
    bar = '[{}] {}%'.format(bar, str(int(perc)).ljust(3))
    print ('\r  {}'.format(bar), end='')

def read_decklist(decklist_file):
    cards = []
    with open(decklist_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        words = line.split(' ')
        quantity = int(words[0].replace('x', ''))
        name = ' '.join(words[1:]).replace('\n', '')
        for q in range(quantity):
            cards.append({'name':name})
    return cards

def save_cache(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))

def show_heading():
    os.system('cls')
    print(' ============================')
    print(f' Playtest Deck Generator {VERSION}')
    print(' ============================')

def wrap_text(text, font, line_length):
    # from https://stackoverflow.com/a/67203353
    lines = ['']
    for word in text.split():
        if word != '\n':
            line = f'{lines[-1]} {word}'.strip()
        else:
            line = f'{lines[-1]}\n'
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines), len(lines)

def main():
    show_heading()
    directory_list = [
        f'{THIS_DIRECTORY}data',
        f'{THIS_DIRECTORY}images',
        f'{THIS_DIRECTORY}output'
    ]
    for directory in directory_list:
        if not os.path.exists(directory):
            os.mkdir(directory)
    if os.path.exists(f'{THIS_DIRECTORY}decklist.txt'):
        decklist = f'{THIS_DIRECTORY}decklist.txt'
        print(' Read card names from decklist.txt')
    else:
        input(' Press Enter and select deck list text file (one card per line in the format `1x Name`):')
        decklist = filedialog.askopenfilename()
    cards = read_decklist(decklist)
    include_lands = input(' Include basic lands in output? [Y/N] ')
    if include_lands.upper() == 'Y':
        include_lands = True
    else:
        include_lands = False
    print(' What format would you like generated?')
    print('  1 - Plain text')
    print('  2 - Full card')
    output_format = input(' > ')
    if output_format == '1':
        mode = 'text'
    else:
        mode = 'image'
    temporary_images = generate_deck(cards, mode, include_lands)
    input(f' Done. Output saved to \n  "{THIS_DIRECTORY}output"')


if __name__ == '__main__':
    main()
