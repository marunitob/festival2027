from app.db_classes import Film, Beseda, Workshop, Host
from . import ALLOWED_EXTENSIONS, db, app
import json
import random
import os

def get_rooms() -> dict:
    """
    vrati dict s mistnostma pro kazdy den
    format: {den: [mistnost1, mistnost2, ...], den2: [...], ...}
    pouziva se pri zobrazovani programu (je potreba vedet, v jakych mistnostech se ten den neco deje - to nemusi byt kazdy den stejny)
    """
    with app.app_context():
        rooms = dict()
        for day in [1, 2, 3]:
            rooms[day] = set()
            rooms[day].update([r[0] for r in list(db.session.query(Film.room).filter(Film.day == day).distinct().all())])
            rooms[day].update([r[0] for r in list(db.session.query(Beseda.room).filter(Beseda.day == day).distinct().all())])
            rooms[day].update([r[0] for r in list(db.session.query(Workshop.room).filter(Workshop.day == day).distinct().all())])
            
    def rooms_sort_function(room):
        if room in app.config["ROOMS_ORDERED"]: return app.config["ROOMS_ORDERED"].index(room)
        return len(app.config["ROOMS_ORDERED"])+1
    for day in [1, 2, 3]:
        rooms[day] = list(rooms[day])
        rooms[day].sort(key=rooms_sort_function)
    return rooms

def update_rooms():
    app.rooms = get_rooms()

def get_all_rooms(films_only=False) -> list:
    """
    vrati vsechny mistnosti, kde se behem festivalu neco deje
    - argument films_only: pokud je True, vrati jenom mistnosti, kde se pousti nejaky film
    """
    rooms = set()
    rooms.update([r[0] for r in list(db.session.query(Film.room).distinct().all())])
    if films_only: return list(rooms)
    rooms.update([r[0] for r in list(db.session.query(Beseda.room).distinct().all())])
    rooms.update([r[0] for r in list(db.session.query(Workshop.room).distinct().all())])
    return list(rooms)

def allowed_file(filename, allowed_extensions=ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def correct_uid(uid, h_allowed=True):
    if '_' not in uid: return False
    if len(uid.split('_')) != 2: return False
    item_type, item_id = uid.split('_')
    if not item_id.isdigit(): return False
    if h_allowed:
        if item_type not in ['w', 'b', 'f', 'h']: return False
    else:
        if item_type not in ['w', 'b', 'f']: return False
    return True

def get_object_by_uid(uid, correct=True):
    """
    returns Film, Beseda, Workshop or Host object depending on input
    - example: f_5 returns Film object with id 5
    """
    if not correct:
        if not correct_uid(uid):
            raise Exception('Incorrect uid provided')
    item_type, item_id = uid.split('_')
    item_id = int(item_id)
    if item_type == 'f':
        return Film.query.get(item_id)
    if item_type == 'b':
        return Beseda.query.get(item_id)
    if item_type == 'w':
        return Workshop.query.get(item_id)
    if item_type == 'h':
        return Host.query.get(item_id)
    
def load_albums():
    albums_path = app.config['ALBUMS_JSON']
    # slozka i soubor jsou v gitignore, takze pri prvnim spusteni je potreba je vytvorit
    os.makedirs(os.path.dirname(albums_path), exist_ok=True)
    if not os.path.exists(albums_path):
        with open(albums_path, 'w') as f:
            json.dump({}, f)
    app.albums_dict = json.load(open(albums_path, 'r'))

def write_albums():
    json.dump(app.albums_dict, open(app.config['ALBUMS_JSON'], 'w'))

def random_hex_token(length=16):
    return ''.join(random.choice('0123456789ABCDEF') for i in range(length))