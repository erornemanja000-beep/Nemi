#!/usr/bin/env python3
"""Pretvara prepis jelovnika (menu_transcript.md) u strukturisan menu.json za web jelovnik.

  python3 menu_json.py menu_transcript.md menu.json
"""
import json, re, sys

# web kategorije (tabovi) -> sekcije iz štampanog jelovnika
GROUPS = [
    ('fruehstueck', 'Frühstück', 'Breakfast', ['Frühstücksboxen', 'Box Add-ons', 'Sides and Extras', 'Aufstriche', 'Gebäck',
                                                  'Direkt gepresste Säfte', 'Frühstücksgerichte', 'Eiergerichte', 'dazu', 'Bagels']),
    ('starters', 'Bites & Starters', 'Bites & Starters', ['Bites', 'Soup & Starters']),
    ('soulfood', 'Soulfood & Salads', 'Soulfood & Salads', ['Soulfood & Salads']),
    ('italy', 'Italy', 'Italy', ['Italy']),
    ('grill', 'Barbecue & Burger', 'Barbecue & Burger', ['Barbecue', 'Burger']),
    ('klassiker', 'Klassiker', 'Classics', ['Klassiker']),
    ('tapas', 'Tapas', 'Tapas', ['Tapas']),
    ('pizza', 'Pizza', 'Pizza', ['Pizza', 'Add-ons and sides', 'Fladen', 'Saucen', 'Bakery']),
    ('desserts', 'Desserts', 'Desserts', ['Desserts']),
    ('kaffee', 'Kaffee', 'Coffee', ['Röstraum black', 'Röstraum red', 'mit Geschmack', 'Schokolade']),
    ('tee', 'Tee', 'Tea', ['Freiraum Bio & Frische Selektion', 'Schwarz & Minze', 'Grün, Kamille', 'Fruit & Herbal Infusion']),
    ('hausgemacht', 'Hausgemachtes & Alkoholfrei', 'Homemade & Soft Drinks',
     ['Hausgemachte Drinks', 'Eistee', 'Milchshakes', 'Smoothies', 'Alkoholfrei', 'Soft Drinks', 'Fruchtsaft gespritzt']),
    ('bier-wein', 'Bier & Wein', 'Beer & Wine', ['Bier', 'Prosecco / Rosé', 'Wein', 'Champagner', 'Weiß', 'Rot', 'Rosé']),
    ('spritz', 'Spritz & Aperitif', 'Spritz & Aperitif', ['Spriz', 'Negroni | Aperitif']),
    ('cocktails', 'Cocktails', 'Cocktails', ['Classics', 'Signature', 'Mules', 'Sour Cocktails', 'Mixed Shots', 'Mocktails']),
    ('spirits', 'Spirituosen', 'Spirits', ['Aperitif | Bitter', 'Whiskey', 'Cognac', 'Schnaps', 'Gin', 'Vodka', 'Rum', 'Likör',
                                           'Grappa', 'Tequila / Mezcal']),
]
ALLERGEN = re.compile(r'^([A-RL])(\s*,\s*[A-RL])*$')
PRICE = re.compile(r'^[\d.,]+(\s*/\s*[\d.,]+)*$')


def group_for(section, page):
    s = section.lower()
    if page in (9, 10):
        return 'bier-wein'
    if page == 14:
        return 'spirits'
    if page == 8 and s.startswith('smoothies'):
        return 'hausgemacht'
    for gid, *_rest, secs in GROUPS:
        for name in secs:
            if s.startswith(name.lower()):
                return gid
    return None


SIZE = re.compile(r'^[\d.,]+\s*(l|cl|ml|g)(\s*/\s*[\d.,]+\s*(l|cl|ml|g))*$', re.I)


def parse_item(text):
    text = re.sub(r'\s+\((?:filled|spelling|p\.\d|probably)[^)]*\)\s*$', '', text.strip())
    flags = []
    for tag, flag in (('[vegan]', 'vegan'), ('[veg]', 'veg'), ('[scharf/chili]', 'spicy'), ('[scharf]', 'spicy'), ('[chili]', 'spicy')):
        if tag in text:
            flags.append(flag)
            text = text.replace(tag, '')
    parts = [p.strip() for p in re.split(r'\s+—\s+', text.strip()) if p.strip()]
    item = {'name': parts[0].strip(), 'desc': '', 'allergens': [], 'price': None, 'flags': sorted(set(flags))}
    rest = parts[1:]
    if rest:
        m = re.match(r'^([\d.,]+(?:\s*/\s*[\d.,]+)*)\b', rest[-1])
        if m and PRICE.match(m.group(1).replace(' ', '')):
            item['price'] = m.group(1).replace(' ', '')
            rest.pop()
    keep = []
    for part in rest:
        if ALLERGEN.match(part):
            item['allergens'] = [a.strip() for a in part.split(',')]
        elif SIZE.match(part):
            item['size'] = part
        else:
            keep.append(part)
    if keep:
        item['desc'] = ' — '.join(keep)
    m = re.search(r'\s(\d+[,.]?\d*\s?(?:l|cl))$', item['name'])
    if m and 'size' not in item:
        item['size'] = m.group(1); item['name'] = item['name'][:m.start()].strip()
    if 'Freiraum' in item['name'] or 'Signature' in item['name']:
        item['signature'] = True
    return item


def main(src, dst):
    lines = open(src, encoding='utf-8').read().split('\n')
    page, section, note = 0, None, None
    sections = []
    for raw in lines:
        if raw.startswith('## Visual style'):
            break
        m = re.match(r'^## Page (\d+)', raw)
        if m:
            page = int(m.group(1)); continue
        m = re.match(r'^### (.+)', raw)
        if m:
            title = m.group(1)
            note = None
            nm = re.match(r'(.+?)\s*\(([^)]*)\)\s*$', title)
            if nm:
                title, note = nm.group(1), nm.group(2)
            if note and re.search(r'pill|box|column|outline', note):
                note = None
            title = title.replace('Frühstücksboxen — ', '').replace('Sides and Extras — ', '')
            section = {'page': page, 'title': title.strip(), 'note': note, 'group': group_for(m.group(1), page), 'items': [], 'footnotes': []}
            sections.append(section); continue
        if section is None:
            continue
        if raw.startswith('- '):
            body = raw[2:].strip()
            if body.startswith(('(', '"')):
                section['footnotes'].append(re.sub(r'^\([^)]*\)\s*', '', body).strip('"'))
            else:
                section['items'].append(parse_item(body))
        elif raw.startswith('  - ') and section['items']:
            section['items'][-1].setdefault('extras', []).append(parse_item(raw[4:]))
        elif raw.startswith('Footnote'):
            fn = re.sub(r'^Footnote[^:]*:\s*', '', raw).strip().strip('"')
            section['footnotes'].append(fn)
    groups = []
    for gid, de, en, _ in GROUPS:
        secs = [s for s in sections if s['group'] == gid and s['items']]
        groups.append({'id': gid, 'de': de, 'en': en, 'sections': [{k: s[k] for k in ('title', 'note', 'items', 'footnotes')} for s in secs]})
    allergen_sec = next((s for s in sections if s['page'] == 15 and 'Codex' in s['title']), None)
    out = {'source': 'Freiraum Speisekarte (PDF, Juli 2026), transkribiert', 'groups': groups,
           'allergenLegend': [i['name'] for i in allergen_sec['items'] if re.match(r'^[A-R] - ', i['name'])] if allergen_sec else []}
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = sum(len(s['items']) for g in groups for s in g['sections'])
    print('groups', len(groups), 'items', n)
    for g in groups:
        print(' ', g['id'], sum(len(s['items']) for s in g['sections']), [s['title'] for s in g['sections']])
    unassigned = [s['title'] for s in sections if s['group'] is None and s['items'] and s['page'] not in (15, 16)]
    print('unassigned sections:', unassigned)


if __name__ == '__main__':
    main(*sys.argv[1:3])
