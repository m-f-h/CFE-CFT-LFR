#!/usr/bin/env python3                           -*- coding: utf-8 -*-
"""
CFE_CFT_LFR.py    
Module with functions to manage LFR/CFE/CFT chess competitions.
(c) Oct. 2025 by MFH
"""

##### PART I : imports and global variable initialisations #####

import __main__
__main__.st.write("Debugging...: Now importing CFE_CFT_LFR.py")

from streamlit import write, markdown, text_input as input

def display_HTML(*args):
    markdown(*args, unsafe_allow_html=True)

def display(*args, **kwargs): # we must discard kwargs (such as `clear=True`)
    if 'clear' in kwargs:
        ... # should we use a clear() function in streamlit ?
    if args and args[0].startswith("<"):
        display_HTML(*args)
    else:
        write(*args)

display("Starting script...")

GLOBALS = globals()

import datetime # for datetime.fromtimestamp().strftime() & timezone
import time # for `sleep()`

#from IPython.display import HTML
# this is just 'NOP', at present :
#HTML = lambda *args: args if len(args)>1 else args[0]

#import CFE_data as DATA

url_annuaire = default_annuaire =\
    "https://www.chess.com/fr/announcements/view/annuaire-des-equipes-locales"

for name in ( 'clubs_info_dict',    # dict { club_url: club_info_dict }
                    # this is a dict of all clubs, with their 'name', 'admins', etc.
              'joueurs',            # dict { user: player_data }
                    # this is a dict of all players, with their 'finished',
                    # 'ongoing' and 'registered' matches (each of which is a list)  
              'club_matches_data',  # dict { club_url: [ match_data, ... ] }
                    # this is a dict of club's matches (list), indexed by club
                # voir aussi : actualiser_liste_rencontres()
              'matches',            # dict { match_id: match_data }
                    # this is a "flat" dict of all matches, for easy access
              'rencontres',         # dict { pattern: [ match_id, ... ] }
                    # dict of matches lists, indexed by pattern
              ):
    if name not in globals():
        if hasattr(GLOBALS, name):
            globals()[name] = GLOBALS[name]
        else:
            display(f"`{name}` undefined in `CFE_data` and `__main__` - creating empty dict.")
            GLOBALS[name] = {}

##################################################

import datetime # for datetime.fromtimestamp().strftime()
import time # for `sleep()`
#from IPython.display import HTML


# INITIALISATIONS

#@title corrections : rencontres "mal étiquetées" à enlever/ajouter dans certaines compétitions
corrections={ # premier indice: "pattern" ; puis : 'add'/'remove' ; puis list, set ou dict de "match_id".
              # pour 'add', il *faut* utiliser un `dict`, et donner l'intitulé correct (p.ex. entre (...) à la fin)
    "CFE.*26": {
        'remove': {"https://www.chess.com/club/matches/1804520":
                    "CFE 2026 U1400 R5 - Rennes vs Grenoble: fait partie de la CFE *2025* !"
        },
 }, "CFE.*25": {
        'add': {"https://www.chess.com/club/matches/1804520": #/grenoble-echecs-metropole/1804520
                  "CFE 2026 U1400 R5 - Rennes vs Grenoble (en vrai: CFE 2025 U1400 R5 !)"
        },
 }, "LFR.*25": {
        'add': {"https://www.chess.com/club/matches/region-grand-est/1810132":
                  "Region Grand Est vs Hauts-de-France (LFR 2025 U1400 R8)",
                "https://www.chess.com/club/matches/team-centre-val-de-loire-1/1712343":
                  "Team Centre Val de Loire contre Ile-de-France club (LFR 2025 U1400 R1)"
        },
 }, "CFE.*2025.*1400[ ,-]*R": { # problème seulement si le 'R' était "demandé"
        'add': {"https://www.chess.com/club/matches/1740101":
                    "CFE2025 U1400 R2 Toulouse contre Rennes (le R2 était manquant)",
                "https://www.chess.com/club/matches/rennes/1718419":
                    "CFE 2025 U1400 R1: Rennes vs La Tour Infernale (= Isbergues): 'R1' manquait",
        },
}}

#@title `Menu()` : afficher un menu, attendre un choix, et exéctuer actions

"""Affiche le `greeting` (en-tête) (si fourni) et le menu,
attend l'un des choix proposés, et execute l'action correspondante.
`menu` est un dict { choix: action } ou les `choix` sont `int` ou `str`
et les `action` sont des fonction dont le docstring est affiché dans le menu,
en utilisant `data` pour substituer d'éventuelles `{variables}` dans les docstrings.
"""

class Menu(dict): 
    """Classe Menu, dérivée de dict, pour afficher un menu, attendre un choix,
    et exécuter l'action correspondante.
    Les entées du dict sont :
    - 'greeting' (optionnel): en-tête / message "de bienvenue" affiché en début du menu
    - 'choix': dict { int|str: callable } : numéros correspondant au choix d'une action
Chaque entrée de 'choix' est un choix (int ou str) mappé à une fonction dont
le docstring est affiché dans le menu.

La méthode `run()` affiche le menu, attend un choix, et exécute l'action.
Des paramètres supplémentaires peuvent être passés à `Menu()` et seront
utilisés pour formater les docstrings des fonctions (avec `str.format()`).
"""
    def __init__(self, choix: dict, greeting: str = '', **data):
        """Initialise le menu avec `greeting`, `choix` et autres données `data`
        pour formater les docstrings des fonctions."""
        super().__init__(choix = choix, greeting = greeting, data = data)
        self.run()
        self.done = 1
    def run(self):
        """Affiche le menu, attend un choix, et exécute l'action correspondante."""
        if hasattr(self, 'done') and self.done: return
        if self['greeting']:
            display_HTML(self['greeting'])#, clear = True)
        data = self['data']
        for var,val in data.items(): # make sure data is up to date
            if var in globals():
                data[var] = globals()[var]    
            else: # this can happen only once !
                globals()[var] = data[var] = \
                      eval(val, #globals=
                           globals()) # update data
        menu = self['choix']
        for choix, action in menu.items():
            display(f"({choix}) -", action.__doc__.format( **data ))
        time.sleep(1)
        while True:
            display("Votre choix : ")
            if (i := input().strip()) in menu \
                or i.isdigit() and (i := int(i)) in menu:
                break
            display_HTML("<b style='text-color:red'>Veuillez entrer un des choix proposés!</b>")
        if menu[i]()=='return': return


#0. Initialisations et fonctions basiques
"""
ask(prompt) ; fmt_user,club,match,... ; etc., et les import nécessaires
"""

#@title `ask(prompt)`

def ask(prompt = "(Appuyer sur [Entrée] pour continuer.)"):
    """Affiche un prompt et attend une entrée utilisateur (peut-être vide) ;
    renvoit True si la réponse ne commence pas par 'n' ou 'N'."""
    display(prompt) ; time.sleep(1) # pour éviter problèmes avec display_HTML(...)
    return not input().strip().lower().startswith('n')
     

#@title fmt_user, club, match...

CHESSCOM = "https://www.chess.com/"
MEMBER = CHESSCOM + "member/"
CLUB_URL = CHESSCOM + "club/"
MATCH_URL = CLUB_URL + "matches/"

def fmt_user(user): # display `user` as given (with or w/o '@') with link to userpage
    return f"<a href='{MEMBER}{user.lstrip('@')}'>{user}</a>"

def fmt_club(club, name=None):
    return f"<a href='{CLUB_URL}{club}'>" + (
        f"{name} ({club})" if name else club ) + "</a>"

def fmt_timestamp(timestamp, fmt = '%Y-%m-%d', default = '?'):
    """Convert unix timestamp to usual date (+time if desired, e.g. '%H:%i:%s').
    Return default if invalid timestamp."""
    try: return datetime.datetime.fromtimestamp(timestamp).strftime(fmt)
    except (TypeError, ValueError): return default
def date2timestamp(year = 2025, month = 1, day = 1):
    return datetime.datetime(year, month, day, 
                             tzinfo=datetime.timezone.utc).timestamp()

def fmt_match(match_id, fmt = '%Y-%m-%d'):
    match_id = match_id.split('/')[-1] # remove URL prefix if there
    if match_data := get_match_data(match_id):
        match_name = match_data.get('name', 'N/N')
        start_date = fmt_timestamp(start_time := match_data.get('start_time'),
           fmt, '?') + fmt_timestamp(end_time := match_data.get('end_time'),
           fmt = ", Fin: " + fmt, default = ", prévu" if "regist" in match_data.get(
                                              'status','') else ", en cours")
        text = f"{match_name} (ID: {match_id}, Début: {start_date})"
    else:
        text = f"Match ID: {match_id} (détails non disponibles)"
    return f"<a href='{MATCH_URL}{match_id}'>{text}</a>"     
#@title `matches_pattern(name, pattern)`: regex search with memoized pattern

import re # for regex -- only needed here
compiled_regex = {}
def matches_pattern(name, pattern):
    if pattern not in compiled_regex:
        compiled_regex[pattern] = re.compile(pattern, re.IGNORECASE)
    return compiled_regex[pattern].search(name)

#@title add_to_main_menu(function): the problem is that if we re-run the script, either it gives duplicates in the menu or we can't use "insert" and/or automatic ("next free") numbering

"""
if 0:
  def shift_up(number,main_menu):
    if number+1 in main_menu: shift_up(number+1)
    main_menu[number+1] = main_menu[number]

def add_to_main_menu(function, number=None):
    if number is None:
       number = next(n for n in range(1,len(main_menu)+9) if n not in main_menu)
    elif number in main_menu:
      display(f"WARNING: shifting menu entries '{number}' and higher to insert item as {number}.")
#      shift_up(number)
    main_menu[number] = function
"""

# 1. liste et choix de la compétition à analyser

#@title `make_dict(s: str) => compétitions` : liste des pages web avec information sur les compétitions

# d'abord, make_dict => dict( nom: url ) pour chaque nom = 'CFE 2026 D1' etc
# puis on transforme les url en compet = {'url': url} afin de rajouter d'autres
# données après.
def make_dict(s: str):
    "L'URL doit être separée du 'label' par ': '. (Plus d'espace est possible.)"
    return dict( (t.strip('- ') for t in row.split(': '))
       for row in s.split("\n") if 'http' in row)

compétitions = make_dict("""Ceci collé à partir d'un message perso:
Pour le classement ça sera utile pour toutes ces divisions de CFE:
CFE 2026 D1: https://www.chess.com/clubs/forum/view/cfe2026-d1
CFE 2026 D2: https://www.chess.com/clubs/forum/view/cfe2026-d2
CFE 2026 D3: https://www.chess.com/clubs/forum/view/cfe2026-d3
CFE 2026 u1400: https://www.chess.com/clubs/forum/view/cfe2026-u1400
Idem pour LFR:
- LFR 2026 L1: https://www.chess.com/clubs/forum/view/lfr2026-l1
- LFR 2026 L2: https://www.chess.com/clubs/forum/view/lfr2026-l2
- LFR 2026 L3: https://www.chess.com/clubs/forum/view/lfr2026-l3
- LFR 2026 U1400: https://www.chess.com/clubs/forum/view/lfr2026-u1400
- LFR 2026 U1000: https://www.chess.com/clubs/forum/view/lfr2026-u1000
et:
LFR 2026 960 : https://www.chess.com/clubs/forum/view/lfr2026-960
Autre compét. pour établir le classement:
LFR 2025 U1400 : https://www.chess.com/fr/announcements/view/calendrier-lfr2025-en-moins-de-1400
""")
### On veut par la suite ajouter d'autres info pour chaque compétition,
### donc on change les valeurs en dict ( url = ... ):
for cid,url in compétitions.items():
    compétitions[cid] = { 'url': url } # 'nom': cid,
#compétitions
#TO DO: extraire la liste des clubs et leur nom de ces pages
     

#@title (1) choix_compèt: afficher/changer la compétition à analyser.
def choix_compèt():
    """Changer la compétition à analyser. Choix actuel : '{pattern}'"""
    global pattern, rencontres
    while True:
      display_HTML("<h2>***** Choix de la compétition *****</h2>")#, clear=True)
      display(f"""Compétition ('pattern') actuellement choisie: '{pattern}'
Nombre de rencontres trouvées pour cette compétition: %d""" %
            len(rencontres.get(pattern,'')) )
      if not rencontres.get(pattern):
          display_HTML("<dd><b style='color:red'>(Mauvais 'pattern' ou actualisation nécessaire (taper 'a' ci-dessous) !)</dd>")
      pat_list = { no: compet for no,compet in enumerate(
            (f"{c}.*2{a}" for a in ("6","5","6.*u1400",) for c in ("LFR","CFE","CFT"))
            , 1) }
      display(f"""
[Indication: un espace (ou point) suivi d'une étoile dans le 'pattern' permet de
      sélectionner les rencontres dont le nom comprend des espace (ou des caractères
      quelconques) à cet endroit ou non. (Exemple : "CFE.*25" va sélectionner
      tout parmi "CFE 2025", "CFE'25", "CFE2025", et "CFE marseille 125".)
      Sans l'année, les rencontres de toutes les années seraient considérées.
  Je vous propose quelques pattern prédéfinis, il suffira de taper le numéro :
{pat_list}
Tapez 'a' pour actualiser la liste des rencontres,
      [Entrée] pour retour au menu principal.]
Entrez votre choix (nouveau 'pattern', 'a' ou [Entrée]): """)
      time.sleep(1)
      i = input().strip()
      if not i: return
      elif i.lower()=='a': actualiser_liste_rencontres()
      elif i.isdigit() and (n:=int(i))in pat_list:
          pattern = pat_list[n]
      else: pattern = i
      # et on reste dans la boucle "while True:" pour l'afficher

##################################################
"""
CFE_rencontres.py
(c) Oct. 2025 by MFH

Part 2. Liste des rencontres dans le cadre d'un championnat donné (p.ex. LFR 2025)

- d'abord, pour un club donné: get_club_matches()
- puis, pour l'ensemble des clubs: make_club_matches_data() => club_matches_data[pattern]
- puis, réunion de tous les match_id: get_unique_matches() => matches[pattern]

Part 3. Données complètes pour chaque rencontre

- match_data(id) va rapatrier les données via l'API seulement la première fois,
    puis les stocker localement dans all_full_matches_data, où il va les chercher ensuite
- affiche_rencontres(matches[pattern]) afficher les rencontres pour un championnat donné en ordre chronologique

Part 6. liste des rencontres pour un ou plusieurs joueurs

Functions:
- get_player_matches(username, status) : renvoit une liste de rencontres pour `username`
- get_opponent(player, match_id, unkn) : renvoie le nom de l'adversaire
- affiche_rencontres_joueur(username, status, fmt)
- match_en_cours(match_id, username) : `True` iff match(partie) en cours (ni fini, ni prévu)
- affiche_rencontres_joueurs_club()
"""
import requests
import re


### Part 2. Liste des rencontres dans le cadre d'un championnat donné (p.ex. LFR 2025)
"""
 pour un club donné

 get_club_matches() utilise fetch_club_matches() pour prendre les rencontres
   d'un club dans le cadre d'un championnat donné
"""
#@title get_club_matches( club_url_id, pattern, status )

def get_club_matches(club_url_id, pattern = None,
                     status = ('registered', 'in_progress', 'finished'), debug = 0):
    """
    Fetches match data for a specific club and filters matches by name using a regular expression pattern
    and/or by status.

    Args:
        club_url_id (str): The URL ID of the club.
        pattern (str): The regular expression pattern to filter by (case-insensitive).

    Returns:
        list: A list of dicts (empty if none found), containing match details for the filtered matches,
              viz.: match = { '@id': API_URL/.../match_id, 'name': ..., 'time_class': "daily",
                    'start_time': unix_timestamp, 'opponent': API_URI/.../club_id, 'result': "lose"}
              NOTE : this is not the "full" match data, as in get_match_data!
    """
    if pattern is None: pattern = GLOBALS.pattern
    filtered_matches = []
    try:
        if debug:
          display(end = f"Lecture liste des rencontres pour {club_url_id!r}...")
        matches_data = fetch_club_matches(club_url_id) # Use the existing get_club_matches function

        # Compile the regex for case-insensitive matching
        regex = re.compile(pattern, re.IGNORECASE) # Removed uppercase conversion

        # Iterate through items and check status
        for st, matches in matches_data.items():
            if st not in status:
                # or not isinstance(matches, list):
                # earlier, we considered all possible "regular" statuses here
                # (finished, in progress, registered) and if stat wasn't in one of them
                # it was usually "comment" and we printed it out for information.
                # But now as we select among possible statuses we simply skip it.
                continue
                # display(f"{status}: {matches}") # usually a comment
            filtered_matches.extend(match for match in matches
                                    if regex.search(match['name']))
        if filtered_matches:
          if debug:
             display(f" Success: {len(filtered_matches)} matches.")
        else:
          if debug:
            display("No match data available.")

    except requests.exceptions.RequestException as e:
        display(f"Error fetching matches for club {club_url_id}: {e}")
    except Exception as e:
        display(f"An unexpected error occurred while fetching matches for club {club_url_id}: {e}")

    return filtered_matches
     

#@title test
#fetch_club_matches( 'team-french-antilles', 'CFT.*26')
     
# pour l'ensemble des clubs et un championnat donné
#@title make_club_matches_data( clubs = None, pattern='')
def make_club_matches_data(clubs: list|None = None, pattern=''):
    """
    Fetches and filters match data for a list of clubs based on a name pattern.
    Args:
        clubs (list, optional): A list of club URL IDs to process.
               Defaults to all club URL IDs in global clubs_info_dict if None.
        pattern (str, optional): The name pattern to filter matches by (case-insensitive regex).
              Defaults to '' (selects all matches with a name).

    Returns:
        dict: A dictionary where keys are club URL IDs and values are lists of
              filtered match dictionaries.
        This dict is called `club_matches_data` here, but the returned result
        will be stored in the *global* variable `club_matches_data[pattern]`.
    """
    club_matches_data = {} # locally, will become globals()[club_matches_data][pattern]

    clubs_to_process = clubs if clubs else clubs_info_dict
    if not pattern: pattern = GLOBALS['pattern']

    display(f"Recherche rencontres '{pattern}' pour {len(clubs_to_process)} clubs...")
    display("-" * 80)

    for url_id in clubs_to_process:
        filtered_matches = get_club_matches(url_id, pattern = pattern)
        if filtered_matches:
            club_matches_data[url_id] = filtered_matches

    display("-" * 80)
    display(f"Finished processing match data for {len(club_matches_data)} clubs with filtered matches.")

    return club_matches_data

     

#@title Fetch matches for given competition and all clubs
if 0:
  while True:
    pattern = input("Pour quelle compétition (préfixe des noms de rencontre) ? "
                    ).strip()
    if not pattern:
        if ask("Utiliser la valeur par défaut 'LFR2025' ?"):
          pattern = 'LFR2025'; break
    else: pattern = pattern.upper(); break

def actualiser_liste_rencontres( pattern = ''):

    if not pattern : pattern = GLOBALS['pattern']

    global club_matches_data
    if 'club_matches_data' not in globals(): club_matches_data = {}

    if pattern not in club_matches_data:
        club_matches_data[pattern] = {}

    elif club_matches_data[pattern]:
        display(f"""La liste des rencontres '{pattern}' existe déjà ({
            len(club_matches_data[pattern])} entrées).
        Etes vous sûr de vouloir la recharger ?""")
        while not(i := input().strip().lower()): continue
        if i.startswith('n'):
            display("OK -- opération annulée. Appuyez sur [Entrée] pour continuer.")
            input(); return
        #    raise Exception("User interrupt")
    if cmd := make_club_matches_data(pattern=pattern):
        display("OK -", len(cmd), " rencontres trouvées.")
        club_matches_data[pattern] |= cmd
    else: display(f"Aucune rencontre trouvée pour '{pattern}'.")

    global matches
    matches[ pattern ] = get_unique_matches( club_matches_data[ pattern ])

    return club_matches_data[pattern]

if 0:
  display("compétition / pattern =", pattern)# := 'CFE *2025')
  if 'matches'not in vars(): matches={}
  display(f'Found {len(matches[pattern])} matches for {pattern!r}.')

if 0: # Fetch *all* matches for a specific list of clubs ### OBSOLETE / UNUSED ####
   selected_clubs = ["la-reine-danjou"] #"martinique", "bretagne-echecs"]
   all_matches_for_selected_clubs = make_club_matches_data(clubs=selected_clubs)
   for c,m in all_matches_for_selected_clubs.items():
      display(f"Found {len(m)} matches for {c!r}.")
if 0: # Fetch matches for a given list of clubs & pattern ### OBSOLETE / UNUSED ####
   matches_for_selected_clubs = make_club_matches_data(selected_clubs,
                                                       pattern := "LFR2025")
   display("Adding these to global 'club_matches_data':")
   for c,m in matches_for_selected_clubs.items():
      display(f"Adding {len(m)} matches for {c!r}, with {pattern = !r}.")
      club_matches_data[c] = club_matches_data.get(c,[]) + m
'''
#@title divers essais
if 0:
  display(len(cmd := dict(club_matches_data)))
  club_matches_data.clear()
  club_matches_data['LFR2025']=cmd

if 0:
  cmd = club_matches_data[pattern]
  display(pattern, ":", len(cmd), "clubs.")
if 0:
  for match in cmd['team-ajaccio']:
    display(match['name'])
if 0: cmd['team-ajaccio']
if 0: display("Found", s := sum(len(m)for m in cmd.values()),
            f"= {s//2} x 2 matches.")
'''
     

#@title `get_unique_matches`: consolidation des matches
def get_unique_matches( club_matches_dict ):
    """
    Makes a dict of all unique matches, from a dictionary of club match lists.
    Args:
        club_matches_dict: A dictionary where keys are club URL IDs and
                                  values are lists of match dictionaries.
            NOTE: the *global* var. club_matches_dict has as keys the patterns
            corresponding to competitions, and values are `club_matches_dict`
            as expected here.
            The 'match dictionaries" are those found in club/.../matches: {
              "name": "LFR2025 D3 - R1 Les foudres de Auvergne-Rhone-Alpes vs Martinique",
              "@id": "https://api.chess.com/pub/match/1713457",
              "opponent": "https://api.chess.com/pub/club/les-foudres-de-auvergne-rhone-alpes",
              "start_time": 1736931782,
              "time_class": "daily",
              "result": "lose"
            }. Obviously the "result" will be the opposite in one and the other
            "version" of the match dict (that of the 'opponent' club).

    Returns:
        A dict( match_ID = dict(name=..., start_time=..., teams={club_id1, club_id2} }
              with match_ID = @id found across all club match lists,
              an additional entry 'teams': { club_id, opponent_club_id },
              and the entry 'opponent' removed.
    """
    unique_matches = {}
    for club_id, matches_list in club_matches_dict.items():
        for match in matches_list:
            teams = { club_id, match['opponent'].split('/')[-1] }
            if match_id := match.get('@id'):
                if m := unique_matches.get(match_id):
                  if m['teams'] != teams or m['start_time'] != match['start_time']:
                      display("WARNING: inconsistent data for {match_id}:")
                      display(club_id, match, m)
                else: # if not yet present, add "teams" information
                  m = match | { 'teams': teams } # NB: do NOT re-initialize 'match'!!
                  m.pop('opponent')
                  unique_matches[match_id] = m
            else:
                display(f"Warning! no '@id' in {match} of {club_id}!")

    return unique_matches

# Example usage (assuming club_matches_data is available from a previous step):
# all_unique_ids = get_unique_match_ids(club_matches_data)
# display(f"Found {len(all_unique_ids)} unique match IDs.")
     

#display( club_matches_data[ pattern ]['team-provence'])


# Part 3. Données complètes pour chaque rencontre
"""
- match_data(id) va rapatrier les données via l'API seulement la première fois,
  puis les stocker localement dans all_full_matches_data, où il va les chercher ensuite
- affiche_rencontres(matches[pattern]) afficher les rencontres pour un championnat donné en ordre chronologique
"""
#@title `get_match_data(id)` + global dictionary to store full match data

# Assuming all_full_matches_data might have been initialized or loaded earlier

if 'all_full_matches_data' not in globals():
    all_full_matches_data = {}

def get_match_data(match_id: str, debug = 0):
    """
    Retrieve full match data for a given match ID, using the global dictionary
    `all_full_matches_data` to store and return previously fetched data
    (where the keys are *short* match_id = basename of long match '@id').

    Args:
        match_id: The ID of the match. (We're tolerant for long and short form)

    Returns:
        dict or None: A dictionary containing the full match data, or None if
                      the data could not be fetched.
        example: https://api.chess.com/pub/match/1713457
    """
    if '/'in match_id: match_id = match_id.split('/')[-1]
    # Check if the full match data is already in the global dictionary
    if match_id in all_full_matches_data:
        if debug: display(f"Returning cached data for match ID: {match_id}")
        return all_full_matches_data[match_id]

    # If not in the dictionary, fetch the data using get_match_data
    try:
        display(f"Fetching full data for match ID {match_id}...", end="")
        full_data = fetch_match_data(match_id)
        # Store the fetched data in the global dictionary
        display(f" Success.")
        return full_data
    except requests.exceptions.RequestException as e:
        display(f"Error fetching data for match ID {match_id}: {e}")
    except Exception as e:
        display(f"An unexpected error occurred while fetching data for match ID {match_id}: {e}")

# Example usage:
# match_id_example = "1713457" # Replace with an actual match ID
# full_match_info = get_match_data(match_id_example)
# if full_match_info:
#     display("\nFull match data example:")
#     display(full_match_info)
     

#len(all_full_matches_data )
     

#@title divers essais
if 0: matches[pattern][ 'https://api.chess.com/pub/match/1802340' ]
if 0: next(iter(matches['CFE *2025'].items()))

# afficher chronologiquement une liste de rencontres donnée
"""
Cette fonction affiche_rencontres(matches[pattern]) évite de rapatrier les "full data" : si les données complètes n'ont pas encore été chargées, il n'y a donc pas le score même si la rencontre est finie.
"""
#@title afficher chronologiquement une liste de rencontres donnée
import datetime
def affiche_rencontres( matches: dict|list|None = None ):
    """L'argument peut être juste une liste de match_ids,
    auquel cas on fait appel a `full_match_data()`, ou alors
    un dict qui contient toute l'info nécessaire dans les valeurs.
    Si c'est vide, on prend globals()['rencontres'][pattern]
    """
    if not matches:
        if not(gm := globals().get('matches')):
           display("Aucune liste de rencontres établie. Veuillez 'a'ctualiser la compétition !")
           return ask()
        if len(gm) > 1 :
            display(f"""Afficher les rencontres pour la compèt {pattern!r} actuellement choisie,
  ou pour toutes les rencontres: {", ".join(
      f'{p} ({len(m)})' for p,m in gm.items() )} ? [a = actuel / t = toutes]""")
            if( input().strip().lower().startswith('t')):
                matches = sum((list(m) for m in gm.values()), [])
            elif not(matches := gm.get(pattern)):
                display(f"""Aucun match connu pour la compèt '{pattern}' !
                J'essaie d'en choisir une autre...""")
        if not matches:
            matches = max(gm.values(), key=len)

    if not isinstance(matches, dict): # list|tuple|set):
        if not all( isinstance( m, dict ) for m in matches):
            matches = [ m if isinstance(m, dict) else get_match_data(m)
                        for m in matches ]
        matches = { match['@id']: match for match in matches }
    for i,m in matches.items():
            if '@id'not in m: m['@id'] = i
    sorted_matches = sorted(matches.values(),
                            key=lambda x: x.get('start_time', 0))

    def fmt_date( timestamp, fmt = '%Y.%m.%d'): # '%b' = Abbreviated month name
        if timestamp:
            try: return datetime.datetime.fromtimestamp(timestamp).strftime(fmt)
            except (TypeError, ValueError): pass
        return '?'
    def get_score(team):
        return team.get('score','?') if (team := match.get(team)) else '?'

    display("Rencontres triées par date de départ :",
          "=" * 60,
          "Début - Fin  -  Résultat  -  Nom de la rencontre", sep="\n")
    #      2025-10-10 - ?  1 - 0
    for match in sorted_matches:
        # Print in the desired format
        display('-'.join(fmt_date(match.get(t+'_time'))for t in('start','end')),
              ' - '.join(get_score('team'+i) for i in'12'),
              match.get('name'), sep=', ')

    display("=" * 60)

#affiche_rencontres()#( matches[pattern] )


### Part 6. liste des rencontres pour un ou plusieurs joueurs

#@title `get_player_matches(username, status)`: renvoit une liste de rencontres pour `username`

def normalize_status(status: str|list|set|tuple) -> tuple:
    """
Normalize status: convert several possible abbreviations to the standard form,
which is a tuple or list of strings among ('finished', 'in_progress', 'registered').
"""
    standard = ('finished', 'in_progress', 'registered', '')
    if isinstance(status, str):
       if not status.isalpha():
          # first check whether we must split (even if single-letter abbreviations
          # are used, e.g. separated by commas and/or whitespace)
          separators = ''.join(c for c in status if not c.isalpha())
          status = [s for s in status.split(separators) if s]
       elif len(status) < len(standard): # single letter abbrev, e.g. 'fi' = finished, in_progress
          status = tuple(status)
       else: status = (status,)
    if not all(s in standard for s in status): # e.g., if abbreviations are used
        old = set(status) # discard duplicates
        status = tuple(ns for s in old  # discard unknown
                  if (ns := next(ss for ss in standard if ss.startswith(s)))
                  or (ns := next(ss for ss in standard if s in ss))
                  or s.startswith('u') and (ns := 'registered')) # "upcoming"
        if len(status) < len(old): display(f"Warning: some in {old} were ignored.")
        elif len(status) > 3 : # there must be duplicates -- should not happen
            display(f"Warning: duplicates in {status = } -- should not happen! {old =}")
            status = tuple(s for s in set(status) if standard[:3])
    return status

def get_player_matches(username, status = ('in_progress', 'registered'),
                       as_dict = False, # return only list of match_id's
                       debug=0) -> list:
    """For a given player, return the list of club match_id's he did/does/will participate in.

`status` can be a tuple/list/set/string with items among {finished, in_progress, registered},
possibly abbreviated or separated by comma and/or space, cf. `normalize_status()`

The global dict `joueurs[username]` will contain an item for each of status, of the form:
"in_progress": [ {"name": "CFE2025 Phases Finales R2 - Antilles Françaises vs Nantes",
                  "url": "https://www.chess.com/club/matches/1815536",
                  "@id": "https://api.chess.com/pub/match/1815536",
                  "club": "https://api.chess.com/pub/club/team-french-antilles",
                  "results": {
                    "played_as_black": "resigned",
                    "played_as_white": "win"
                  },
                  "board": "https://api.chess.com/pub/match/1815536/1" }, ... ]

If `joueurs[username]` already exists and has these items (all s in status),
we assume those lists are complete and up to date.

Related global data:
  * `joueurs[compèt = pattern]` : { club_id : {recontres...}}
  * `matches[compèt] = { match_@id: {'name':..., 'start_time': 1752469383,
        '@id': match_@id='https://api.chess.com/pub/match/1803610',
        'result': 'lose'/'win', 'teams': {'la-tour-infernale', 'team-ajaccio'}}}`.
    """
    if not username: raise ValueError("Username must be given!")
    status = normalize_status(status)
    if not username in joueurs:
        joueurs[username] = {}
    if not all(s in joueurs[username] for s in status):
        if debug: display(end = f"Fetching data for player '{username}'... ")
        try: player_matches = fetch_data(f'player/{username}/matches')
        except:
            display(f"ERROR: can't get data for {username = }. Do they exist?)")
            ask(); return()
        if player_matches:
          if debug: display("success:", ' + '.join(f'{len(m)} {s}' for s,m
                                                 in player_matches.items()))
          if debug > 1: display(player_matches)
          joueurs[username] |= player_matches
        else: display(f"Couldn't find {username}'s matches :-( !")
    # we assume the lists are now complete.
    # make the simplified list of match id's
    return [ m if as_dict or not( ((id := m.get('@id')) or
              (id := m.get('url'))) and (id := id.split('/')[-1]) ) else id
        for s in status for m in joueurs[username][s] ]

     

#list ( all_full_matches_data.keys() )
#all_full_matches_data['1803610']
#joueurs['madameapprentie']
#fetch_data('player/toto/matches')
#list(joueurs)
if 0:
  for m in get_player_matches("madameapprentie",'fi',as_dict=1):
    display(m) #HTML(''+fmt_match(m)+''))
     

#@title `get_opponent(player, match_id, unkn)`: renvoie le nom de l'adversaire
def get_opponent(player, match_id, unknown = None):
    """Renvoie le nom de l'adversaire, ou `unknown` si non trouvé. Si le match
    est seulement programmé/prévu, l'adversaire n'est pas encore définitivement connu."""
    # 'registered' => le match n'a pas encore commencé et l'adversaire est inconnu
    if (match_data := get_match_data(match_id)) and match_data.get('status'
        )in('finished','in_progress') and (teams := match_data.get('teams')):
      teams = list(teams.values()) # 0: team1, 1: team2
      for i,team in enumerate(teams):
        # for each team, scan the list of players to find `player`, then its board,
        # then in the opponent team that board and from there the player = opponent
        if b := next((p['board'] for p in team['players']
                      if p['username']==player), 0):
          return next((o['username'] for o in teams[1-i]['players']
                       if o['board'] == b), unknown)
    return unknown
     

#@title `affiche_rencontres_joueur(username, status, fmt)`

def affiche_rencontres_joueur(username: str|None = '',
                              status = ('in_progress','registered'), fmt = 'HTML'):
    "Afficher la liste des rencontres en cours et à venir pour un joueur donné."
    """Renvoie la liste des rencontres ayant le statut donné pour le joueur `username`.
    Utilise la fonction `get_player_matches()` qui mémoize dans `joueurs[username]`."""

    if username: interactive = False
    else:
        interactive = True
        display("Entrez le nom du joueur: (Le 'username' avec ou sans '@' au début)")
        username = input().strip().lower()
        if not username: return

    if username[0]=='@': username = username[1:] #.lstrip('@')

    if not(player_matches := get_player_matches(username, status = status)):
        display(f"Aucun match trouvé pour '{username}'. (Faute de frappe ?)")
        ask() ; return

    output = f"Joueur {fmt_user(username)} &mdash; Rencontres&nbsp;:\n<ul>\n<li>"

    # enlever les rencontres où le joueur a déjà fini ses 2 parties
    player_matches = [m for m in player_matches if match_en_cours(m, username)]

    def fmt_adversaire(match_id):
        if adversaire := get_opponent(username, match_id):
            return f" (contre {fmt_user(adversaire)})"
        return''

    if not player_matches:
        output +=  "plus aucun match en cours !"
    else:
        output += "\n".join( fmt_match(match_id) + fmt_adversaire(match_id) + ""
                               for match_id in player_matches )
    display_HTML(output + "\n")
    if interactive : ask()

     

#@title `match_en_cours(match_id, username)` : `True` iff match(partie) en cours (ni fini, ni prévu)
def match_en_cours(match_id, username):
    # we have to find the match `match_id` in all_full_matches_data (format as
    # in https://api.chess.com/pub/match/1839354) or in joueurs[username]
    # (format as in https://api.chess.com/pub/player/engagnant/matches)
    if mat := all_full_matches_data.get(match_id):
        # format of `mat`:
        if mat.get('end_time'): return False
        for team in mat['teams'].values(): # match['teams'] is a dict
            for p in team['players']: # team['players'] is a list of dicts
                if username==p['username']:
                  return sum(k.startswith('played_as')for k in p) < 2
    elif player_data := joueurs.get(username):
        for st,matches in player_data.items(): # hopefully only 'fini..','reg..','in_prog...'
          if st in ('in_progress','registered'): #ignore finished matches(rencontres)
            for m in matches: # matches should be a list of dict
                if m['@id'].endswith(match_id):
                   return len(m.get('results','')) < 2
    display(f"Weird - this should not happen: match {match_id!r} not found in data for {username!r}.")
    return True # so it shows up in the list - just in case
     

#affiche_rencontres_joueur("deep-blou")
if 0: all_full_matches_data['1848645' if 0 else '1776070']
if 0: display( min(all_full_matches_data.items()))
#joueurs['madameapprentie']#.clear()
#list(matches)#players_team_list
     

#@title `affiche_rencontres_joueurs_club()`
def affiche_rencontres_joueurs_club():
    "Affiche la liste des rencontres pour chaque joueur d'un club donné."
    display("*** Affichage des rencontres pour tous les joueurs d'un club ***\n")
    club_id = choix_du_club()
    players = get_club_players_list(club_id)
    for p in players:
        affiche_rencontres_joueur(p)
    ask()

###################################################

"""
CFE_classement.py
(c) Oct. 2025 by MFH

Part 7. Classements

Description:

make_classement(...) consiste à:

choisir une compétition compet = compétitions[nom]

On récupère la liste des clubs = get_clubs_from_page(url) qui participent à compet sur la page web url = compet['url'] ; on la stocke dans compet['clubs'] = clubs (anciennement dans global clubs[compète/pattern]).

On rappatrie la liste des rencontres = cherche_rencontres(compet) dans le cadre de cette compète, à partir des clubs = compet['clubs'] et pattern = compet['pattern'] ; on les stocke dans compet['matches'] = rencontres.

On calcule les resultats = get_results(compet) à partir des rencontres, sous forme de resultats[c1][c2] = (s1, s2, open, c1), où s1, s2 sont les points obtenus par le club c1 et c2; open est le nbre de parties pas encore finies, et on tient compte du dict. compet['aliases'] qui représente des changements de noms en cours de la campagne.

make_table(compet) établit et affiche le tableau en fonction des resultats, avec pour chaque club une ligne et aussi une colonne, plus d'autres colonnes supplémentaires avec F = nombre de rencontres terminées, Pts = nombre de points (2 par win, 1 par draw), V/N/D (win/draw/loss) et MA (nbre de parties gagnées).

Fonctions:
- get_clubs_from_page( URL, ...) : rapatrier la liste des clubs à partir de la page web URL.
- cherche_rencontres(compet) : établir la liste des rencontres pour la compétition `compet`.
- applique_corrections(compet, matches) : appliquer d'éventuelles corrections aux rencontres de `compet`.
- get_results(compet) : calcul des scores pour tableau, à partir de `compet['matches']`.
- make_table(compet, clubs, width, fmt) : make HTML table
"""
#@title `get_clubs_from_page( URL, ...)`
import html, requests

# sous-routine : pour le(s) paragraphe(s) de la page qui contient une liste des
# noms et url des clubs, extraire le nom et le club_id = basename(url).

def extract_id_and_name(src: str, debug=0):
    """
    Extract the name (= pure text with punctuation trimmed)
    `html` should contain exactly one href="...".
    The line is assumed to be of the form, as in ...)
    <p>Bordeaux: <a href="https://www.chess.com/club/bordeaux">https://www.chess.com/club/bordeaux</a><br />Grenoble: <a href="https://www.chess.com/club/grenoble-echecs-metropole">https://www.chess.com/club/grenoble-echecs-metropole</a><br />Isbergues: <a href="https://www.chess.com/club/la-tour-infernale">https://www.chess.com/club/la-tour-infernale</a><br />Montpellier: <a href="https://www.chess.com/club/team-montpellier">https://www.chess.com/club/team-montpellier</a>&nbsp;<br />Paris neuf trois: <a href="https://www.chess.com/club/paris-neuf-trois">https://www.chess.com/club/paris-neuf-trois</a>&nbsp;<br />Rennes: <a href="https://www.chess.com/club/rennes">https://www.chess.com/club/rennes</a>&nbsp;<br />Strasbourg: <a href="https://chess.com/club/team-strasbourg">https://chess.com/club/team-strasbourg</a>&nbsp;<br />Toulouse: <a href="https://www.chess.com/club/team-toulouse-equipa-tolosa">https://www.chess.com/club/team-toulouse-equipa-tolosa</a>&nbsp;</p>
    sometimes no ':', sometimes &nbsp; interspersed ...
    or as in https://www.chess.com/fr/announcements/view/calendrier-lfr2025-en-moins-de-1400 :
    <p><a href="https://www.chess.com/club/bretagne-echecs" target="_blank">Bretagne</a><br /><a href="https://www.chess.com/club/echiquier-de-normandie" target="_blank">Normandie</a><br /><a href="https://www.chess.com/club/team-hauts-de-france" target="_blank">Hauts de France</a><br /><a href="https://www.chess.com/club/chess-occitanie" target="_blank">Occitanie</a><br /><a href="https://www.chess.com/club/team-provence" target="_blank">PACA</a><br /><a href="https://www.chess.com/club/team-centre-val-de-loire-1" target="_blank">Centre Val de Loire</a><br /><a href="https://www.chess.com/club/ile-de-france-club" target="_blank">Ile de France</a><br /><a href="https://www.chess.com/club/les-foudres-de-auvergne-rhone-alpes" target="_blank">Les foudres d'Auvergne Rh&ocirc;ne Alpes</a><br /><a href="https://www.chess.com/club/region-grand-est" target="_blank">R&eacute;gion Grand Est</a><br /><a href="https://www.chess.com/club/team-nouvelle-aquitaine" target="_blank">Team Nouvelle Aquitaine</a></p>
    """
    if debug: display("extracting from", src)
    try: start_href = src.index('href=')+5 # must have -- or exception is thrown
    except: return
    end_href = src.find( src[start_href], start_href+2 ) # find next same delimiter
    url = src[ start_href+1 : end_href ]
    src = src.replace(url,'')
    if " " in src: src = src.replace(" "," ")
    # we must do this by hand or   => \xa0 => problem
    # remove HTML entities like   , é ...
    src = html.unescape(src)
    while "<" in src:
        src = src.strip(" :.")
        if src.endswith(">"): src = src[ : src.rfind("<") ] # known to exist
        elif src.startswith("<"):
            if (i := src.find(">")) < 0: break
            src = src[ i+1 : ]
        else: # HTML tag "in the middle" (WEIRD !)
          if (j := src.find('>', i := src.index('<'))) < 0: break
          src = src[ : i ] + src[ j+1 : ]
    if "(" in src: src = src[ : src.index('(') ]
    if src := src.strip(" .:"): # else return None
      return url.split('/')[-1], src

# fonction principale: scan la page URL pour des paragraphes avec la liste des clubs

def get_clubs_from_page( URL, pattern = "chess.com/club/" ):
    "Retrieve web page at URL and extract club list from there."

    response = requests.get(URL, stream=True)
    if not response.ok:
       display(f"Problem retrieving page '{URL}'.")
       ask() ; return

    clubs = {} # NOTE: this result will be stored in global dict clubs[compèt] !
    # or maybe rather in compet['clubs'] with compet being in compétitions.values().
    #div = ''.encode() ; scanning = 1
    div = '</header'.encode() ; scanning = 1
    for bline in response.iter_lines():
        # first skip to div, then skip to (next) line with pattern
        if scanning:
          if div not in bline or (scanning==1 and (scanning := 2) and
                                  (div := pattern.encode())): continue
          # now we found the (first or subsequent) matching line
        elif not div in bline: # not scanning : we had already found a matching line
          # skip lines w/o pattern if there are short,
          # in case the pattern might continue
          if len(bline) > 50: break # long enough line not having the pattern in it
          continue # skip this
        line = bline.decode()
        if not line.count(pattern) > 1: continue # we expect the line to have multiple club links
        clubs.update(T for L in line.split('</a>') # HTML TAG /A
                     if (T:=extract_id_and_name(L))) # <br /> would be another possibility
        scanning = 0 # no more in scan mode:
                     # the next long enough line w/o pattern will exit the function

    return clubs # to be stored in compet['clubs']

None and'''
# test
if 0: #
  clubs = {}
  for nom,compet in compétitions.items():
    if isinstance(compet, str):
      url = compet; compétitions[nom] = {'url': url, 'nom': nom}
    else: url = compet['url']
    display("Considering", nom,":", url)
    clubs[compet] = get_clubs_from_page(url)
    display("Found:"); display(clubs[compet])
if 0:
  display(clubs_lfr25_u1400 :=
        get_clubs_from_page("https://www.chess.com/fr/announcements/view/calendrier-lfr2025-en-moins-de-1400"
        ))
'''


#display(list(classement_data))
#['CFE2026 D1', 'CFE2026 D2', 'CFE2026 D3', 'CFE2026 u1400', 'LFR2026 L1', 'LFR2026 L2', 'LFR2026 L3',
# 'LFR2026 U1400', 'LFR2026 U1000', 'LFR2026 960', 'LFR 2025 U1400']
#list(clubs)
#clubs['LFR 2025 U1400']
     

def pattern2nom(pattern): return pattern.replace(".*"," ").replace(" *"," ")
def nom2pattern(nom): return nom.replace(" ",".*")
#pattern2compet()
#dict_ajout_alias(clubs['LFR 2025 U1400'])
#make_table(res,width=1200)
     

#@title `cherche_rencontres(compet)` : établir la liste des rencontres
def cherche_rencontres(compet): #clubs, pattern = None):
    """Utilise compet[clubs] et compet[pattern] et corrections."""

    if matches := compet.get('matches'):
        if not ask(f"""Une liste de {len(matches)} rencontres est déjà connue pour {compet['nom']}.
        Voulez-vous vraiment recalculer la liste?"""):
            return matches # they said no, they don't want to re-calculate

    # NOTE : compet['pattern']=='' is possible (to select all)
    if 'pattern' not in compet:
        if nom := compet.get('nom'):
            compet['pattern'] = nom2pattern(nom)
        else:
          display('Erreur: compèt ne contient ni nom, ni pattern !')
          ask() ; return
    if 'nom' not in compet and (pattern := compet.get('pattern')):
        # pattern could be '' but this doesn't allow to construct a name
        compet['nom'] = pattern2nom(pattern)
        # mais `nom` n'est pas vraiment requis

    # établir la liste des clubs si nécessaire

    if not(clubs := compet.get('clubs')):
        if url := compet.get('url'):
            display(f"""Tentative de rapatriement de la liste des clubs à partir de
la page '{url}'... """)
            if clubs := get_clubs_from_page(url):
               compet['clubs'] = clubs ; display("fini !")
            else:
                display("\nERREUR: N'ai pu déterminer la liste des clubs!")
    # is it now set ?!
    if clubs := compet.get('clubs'):
        display_HTML(
        f"<dl><dt>Les {len(clubs)} clubs participant à la compète sont:</dt>\n<dd>"
        + ", ".join(fmt_club(c) for c in clubs) + "</dd>\n</dl>\n")
    else:
        display("ERREUR: liste des clubs inconnue - ne peux procéder.")
        ask() ; return

    display("Rapatriement des rencontres pour ces clubs...")

    cmd = make_club_matches_data(clubs, compet['pattern'])
    if matches := get_unique_matches(cmd) :
       if ask(f"{len(matches)} rencontres trouvées. Afficher la liste ?"):
          display_HTML("<dt>Liste des rencontres trouvées:</dt><dd>" # HTML tag dt
          + "</dd>\n<dd>".join(fmt_match(m)for m in matches) + "</dd>\n</dl>" ) # HTML tag dd
    applique_corrections(compet, matches)
    return matches
cherche_résultats = cherche_rencontres
     

#@title applique_corrections(compet, matches):
def applique_corrections(compet, matches):
    "Appliquer d'éventuelles corrections, données dans le dict global `corrections`, concernant `compet`."
    for pattern,corr in corrections.items():
        if pattern == compet.get("pattern") or matches_pattern(compet.get('nom'), pattern):
            # competition name matches pattern
            for action, tasks in corr.items():
                if action=='remove':
                    remove=[]
                    for task in tasks: # task could be an integer or short or long match_id
                        t = str(task).split('/')[-1]
                        for m in matches:
                            if m.endswith(t): remove.append(m)
                    for m in remove:
                        p=matches.pop(m); display(f"Correction: removed {p['name']}:", m)
                elif action=='add':
                    for match_id, name in tasks.items():
                        if matches_pattern(name, compet['pattern']): # and match_id.split('/')[-1] not in matches :
                            display(end = f"Correction: adding match {match_id}... ")
                            if match_data := get_match_data(match_id):
                               matches[match_id] = match_data
                               display(f"done: added {name}")
                            else:
                                 display(f"ERROR: Couldn't add {name}.")
     

#@title `get_results(compet)` : calcul des scores pour tableau, à partir de `compet['matches']`
def get_results(compet): #(matches, cutoff, aliases)
    """
    `compet` should have an entry 'matches' (= liste des rencontres),
    and may have entries 'cutoff' (limiting date for match outcomes to take into account)
    and 'aliases' (a dict of name changes).
    For each match_id in `matches`, get match_data = get_match_data(match_id)
    and create an entry match_data['result'] = {club1: score, club2: score}.
    The information is found in the dict match_data['teams'] which has two entries
    'team1' and 'team2', each of which is a dict with an entry 'score',
    and the club's id can be found in the entry '@id'.

    Returns:
        dict: A nested dictionary where the outer keys are club IDs, inner keys are
              opponent club IDs, and values are tuples of (club_score, opponent_score).
    """
    results = {}
    if not(matches := compet.get('matches')):
        if matches := cherche_rencontres(compet):
            compet['matches'] = matches
        else:
            display(f"Pas de rencontres connues pour la compet '{compet.get('nom','?')}' !")
            return

    for match_id in matches:
        if match_data := get_match_data(match_id):
            if len(teams := match_data.get('teams')) == 2:
                # make a new entry 'result' in `match_data`, which is a dict
                # {club1: score1, club2: score2 }

                match_data['result'] = result = {
                    t.get('@id', '').split('/')[-1]: t.get('score', 0)
                    for t in teams.values() }
                open = 0 if match_data.get('status') == 'finished' else\
                      -1 if match_data.get('status') == 'registered' else\
                       sum( 2-sum( k.startswith('played_as_') for k in p)
                            for p in teams['team1']['players'])
                for c1,c2 in zip(result, reversed(result)):
                    if c1 not in results: results[c1] = {}
                    results[c1][c2] = result[c1], result[c2], open, int(match_id.split('/')[-1])
                                      # 'status': match_data.get('status') }

    # now "merge" aliases:
    # * add results[c][a0] =(us,them,open) to results[c][a1] and delete results[c][a0]
    # * merge results[a0] into results[a1] and delete results[a0]
    show=set();
    debug = lambda a0: a0 in show or show.add(a0) or display(debug_string)
    for a0, a1 in aliases.items(): # a0 = old, a1 = new
        debug_string = f"Merging alias {a0} => {a1}..."
        for c,sc in results.items():
            if a0 in sc:     # if a,b > 999 it's the last component, match_id
               debug(a0)
               sc[a1] = tuple(a+b if a+b < 999 else b for a,b in zip(sc[a0], sc[a1])
                              ) if a1 in sc else sc[a0]
               del sc[a0]
        if a0 in results:
           debug(a0)
           if a1 in results:
                results[a1] |= results.pop(a0)
           else: results[a1] = results.pop(a0)

    return results


#{nom:len(compet) for nom,compet in compétitions.items()}
#display(compet := compétitions['CFE 2026 D1'])
#del compet['results']

     

#@title `make_table(compet, clubs, width, fmt)` : make HTML table
def make_table(compet, #results, clubs = clubs['LFR 2025 U1400'],
               order='diag',
               fmt = "border=1 cellpadding=2 cellspacing=0 "):
    """
    Make an HTML table representing the results of `compet`.
    If `compet` doesn't have an entry 'results' with the scores, try to compute it.
    For each key `club_id` in `results = compet['results']`, there will be a row
    labelled `compet['clubs'][club_id]['nom'], and also column for each opponents,
    labelled with the first three letters of that name.
    These columns give the score = results[club_id][opponent_club_id].
    There are additional columns : F (number of finished matches), Pts (number of
    points = 2 per win + 1 per draw), V (number of wins), N (number of draws),
    D (number of losses), MA = total own score (sum of 1st components of score).
    The rows are numbered, with the clubs are listed in order of decreasing 'Pts'
    (more = better), increasing 'F', result of their match if 'Pts' & 'F' are equal,
    and finally decreasing 'MA'.
    The number of finished matches is determined by the 3rd component of the score
    which is the number of unfinished games (=> finished iff score[2] == 0).
    The number of open games also allows to determine whether the given score already
    implies whether the club has won or lost even if there are unfinished games.
    Such scores get orange background, green if score[2]=0, else red.
pour déterminer l'ordre classement:
1) nombre de points
2) nombre de rencontres jouées si même nombre de points (celui qui a le moins de rencontres en cours sera devant)
3) rencontre directe si égalité avec les deux premiers critères
4) match average si égalité avec les trois premiers critères.
    `order` determines order of clubs in the *columns*.
    It can be 'a(lphabetical)' or 'd(iagonal)' = same as rows.
    """
    # if not already available, compute the results
    if not(results := compet.get('results')):
        if results := get_results(compet):
            compet['results'] = results
        else:
            display("Pas de résultat connu pour la compet !") ; return

    # prepare club names and column headers

    if not(clubs := compet.get('clubs')): # this dict has the "shortened full names" as values
        clubs = {club_id: club_id for club_id in results}

    préfixes = { "Les foudres d'", "Team ", "Fédération ", "enne des échecs" }
    for cid,name in clubs.items():
        for prefix in préfixes:
            if prefix in name: #.startswith(prefix): ...[len(prefix):]
                clubs[cid] = clubs[cid].replace(prefix,"")

    club_headers = {club_id: clubs[club_id][:3].upper() for club_id in results}

    # make the (full) table

    table = {} ; color = {}
    for club_id, scores in results.items():
        # Initialize row using dictionary unpacking and comprehension
        row = { 'Club': clubs[club_id] } |  {
                club_headers[c]: f"<a href='{MATCH_URL}{s[3]}'>{s[ : 3 if s[2] else 2 ]}</a>"
                    for c,s in scores.items() }
        known = { c: s[2]==0 or 0 < s[2] < abs(s[0]-s[1]) for c,s in scores.items() }
        row['F'] = sum(known.values())
        row['V'] = sum(s[0]>s[1] for c,s in scores.items() if known[c] )
        row['D'] = sum(s[0]<s[1] for c,s in scores.items() if known[c] )
        row['N'] = row['F'] - row['V'] - row['D']
        row['Pts'] = row['V']*2 + row['N']
        row['MA'] = sum(s[0] for s in scores.values())
        table[club_id] = row
        color[club_id] = { club_headers[club_id]:'black', "Club": 'none' } | {
             club_headers[c]: 'lightgreen'if s[2]==0 else 'orange'if known[c]
                               else 'red' for c,s in scores.items() }

    td_element = { c : f"<td align=center style='white-space: nowrap; background: {c}'>"
                    for c in "lightgreen orange red black none".split() }

    # Sort rows:
    """pour déterminer l'ordre classement:
1) nombre de points
2) nombre de rencontres jouées si même nombre de points (celui qui a le moins de rencontres en cours sera devant)
3) rencontre directe si égalité avec les deux premiers critères
4) match average si égalité avec les trois premiers critères
"""
    keys = sorted( ( ( row['Pts'], -row['F'], row['MA'], cid )
                     for cid,row in table.items() ), reverse=1 )
    # double-check order: no equality between first two criteria?
    for i in range(1,len(keys)):
        if keys[i][0] == keys[i-1][0] and keys[i][1]==keys[i-1][1] :
          # if first two criteria are equal, compare score between the two
          s = results.get( keys[i][-1], {}).get( keys[i-1][-1], '--') # must be in increasing order
          # using 'get' above, because under mysterious circumstances the entry might not exist !
          if s[0] > s[1]: # problem: we must switch the two
              keys[i-1:i+1] = keys[i:i-2:-1]

##### Now, in order to make possibly one or more "split tables",
    # we define the function to make a table for some subset of the clubs.

    def make_HTML_table(classement, group_text=''):
        """`classement` is a list that gives the club_id's in the order they're to be listed.
        Uses `compet`, `table`, `color`, `club_headers`, `order` & `fmt` from outer scope."""
        # order of columns
        if order.startswith('a'): # alphabetic
            opponents = sorted(classement, key = lambda club_id: club_headers[club_id])
        else: # "diagonal order"
            opponents = classement

        columns = ["#", "Club"] + [club_headers[o] for o in opponents] + "F Pts V D N MA".split()
        # Generate HTML table

        html_output = [f"""<h3>Classement pour <a href='{compet['url']}'>{compet['nom']}</a>{group_text}</h3>
<table {fmt}><tr><th>""" + # width={width}
            "</th><th style='min-width: 2em;'>".join(columns) + "</th></tr>\n"]# HTML tags TH, TR

        # Number rows and add them to the table
        for i, club_id in enumerate(classement, 1):
            table[club_id]['#'] = i
            html_output.append(f"<tr>" + "</td>\n".join(
                td_element.get(color[club_id].get(c), "<td align=center>") +
                str(table[club_id].get(c,'-')) for c in columns) + "</td></tr>")
        html_output.append("</table>")
        display_HTML("\n".join(html_output))
##### end of function "make_HTML_table" #######

    make_HTML_table(classement := [k[-1]for k in keys])

    # Make subtables for groups, if any:
    done = []
    for club in table:
        if club in done: continue
        group = { club } | set( results[club] ) # all opponents of this club
        if len(group) == 1: continue # uninteresting
        for c in results[club]: group |= set( results[c] ) # "closure"
        if len(group) == len(table): break
        if not done: # premier groupe
            display_HTML("""
            *** Il semble qu'il y ait plusieurs groupes. ***
            ***    Affichage des tableaux par groupe :   ***""")
            count = 1
        else: count += 1 # groupe suivant
        make_HTML_table([club for club in classement if club in group], f" - groupe {count}")
        done.extend( group ) # mark these clubs as "processed"

#(compétitions[ 'CFE 2026 u1400' ]['results']) # 'CFE 2026 u1400' # 'LFR 2025 U1400'

#make_table(compétitions['CFE 2026 u1400']) #'LFR 2025 U1400'

#@title `tableau_classement()` : entrée menu principal pour faire un tableau de classement

def tableau_classement():
    "Etablir et afficher un tableau de classement pour une compétition choisie."
    liste = { no: compet for no,compet in enumerate(compétitions, 1) }
    while 1:
        display_HTML(f"""<h2>*** Tableau(x) de classement ***</h2>
    Choisissez d'abord l'une des compétitions ci-après:<dl><dd>
{liste}</dd></dl>
        [Entrée] pour retour au menu principal.]""")
        time.sleep(1)
        display("Entrez votre choix (numéro de la compétition ou [Entrée]):")
        i = input().strip()
        if not i: return
        # elif i.lower()=='a': actualiser_liste_rencontres()
        elif i.isdigit() and (n:=int(i)) in liste:
            compet = liste[n]
        else:
            compet = i.upper()
        if not(compet := compétitions.get(nom := compet)):
            compétitions[nom] = compet = {}

        if 'nom' not in compet: compet['nom'] = nom
        make_table(compet) # TODO : largeur en fct du nombre de participants

#add_to_main_menu(tableau_classement) # TODO

##################################################
"""
CFE_clubs.py
(c) Oct. 2025 by MFH

Part 2: rapatriement & gestion liste des équipes (= clubs)
à noter: la liste des équipes est (actuellement) "globale", 
c-à-d. commune pour toutes les compétitions. (Cela a peut-être vocation à changer...) 
Ensuite, pour une compèt donnée, on sélectionne dans la liste des rencontres de chaque équipe 
celles qui correspondent.

Functions:
- extract_club_info(url): extraction liste équipes d'une page web
- affiche_liste_clubs(clubs_info: dict|None = None, format="html"): affichage liste clubs

"""
import requests
from bs4 import BeautifulSoup   # used only here


#@title `extract_club_info()`: extraction liste équipes d'une page web

CLUB_URL_PREFIX = "https://www.chess.com/club/"
def extract_club_info(url, debug=2):
    """
    Extracts club names, URLs, and admin handles from a webpage.
    Also attempts to identify if the club name is highlighted (e.g., in green).
    It iterates through paragraph elements to find the one containing the club list.
    Returns a list of dictionaries containing club information.
    """
    if debug:
      display(f"Extraction des informations de {url = !r}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        if debug>1: display("OK, page retrieved.")
        soup = BeautifulSoup(response.content, 'html.parser')
        if debug>1: display("Page parsed successfully.")

        club_dict = {}

        if content_div := soup.find('div', class_='post-view-content'):
            if debug: display("Content div found.")
            # Find all paragraph elements within the content div
            p_elements = content_div.find_all('p')

            if not p_elements:
              if debug: display("No paragraph elements found within the content div.")

            for i, p_element in enumerate(p_elements, 1):
                if debug: display(f"\nProcessing paragraph {i}:")
                # Get the HTML content of the paragraph and split by  tags
                # Removed the initial replace(' ', ' ') on the whole paragraph
                items = str(p_element).split('<br/>') # HTML TAG BR/

                if debug: display(f"  Number of items (lines): {len(items)}")
                # display(f"  First few items: {items[:5]}...") # Optional: print first few items

                # Check if this paragraph seems to contain the club list
                contains_url = any(CLUB_URL_PREFIX in item for item in items)
                if debug: display(f"  Contains club URL pattern: {contains_url}")
                if not contains_url: continue # goto next paragraph
                if len(items) < 10:
                    if debug: display("...but not enough lines.");
                    continue

                if debug: display("Found paragraph likely containing the club list.")
                for item_html in items:
                    # Use BeautifulSoup to parse each item HTML to check for span tags
                    item_soup = BeautifulSoup(item_html, 'html.parser')
                    # Get the text and replace \xa0 with a regular space
                    text = item_soup.get_text().strip().replace('\xa0', ' ')

                    if CLUB_URL_PREFIX in text:
                        # Extract club name, URL, and admins using regex
                        # The regex should work with regular spaces now
                        match = re.search(r"(.+)\s(" + re.escape(CLUB_URL_PREFIX) + r"[^ ]+)\s*(.*)", text)
                        if match:
                            name = match.group(1).strip()
                            club_url = match.group(2).strip()
                            admins = match.group(3).strip().split() if match.group(3) else []

                            is_highlighted = item_soup.find('span', style=lambda value:
                                                            value and 'background-color' in value)
                            club_dict[ url_id :=
                                       club_url.split('/')[-1] ] = {
                                'name': name,
                                #'url': club_url,
                                'admins': admins,
                                'région': bool(is_highlighted) # REGION
                            }
                display(f"OK - information trouvée pour {len(club_dict)} clubs.")
                break # Stop after finding the list
            else:
              #if debug:
              display("Je n'ai pas trouvé de paragraphe qui contient la liste des clubs.")
        else:
            #if debug:
            display("""Le format de la page ne correspond pas au format attendu pour la
            liste des clubs (forum chess.com => ...).""")
        return club_dict
    except requests.exceptions.RequestException as e:
        display(f"Error fetching the page: {e}")
    except Exception as e:
        display(f"Error parsing the page: {e}")
    if debug:
        display("Aucune information n'a pu être extraite de la page.")
    # return None in these cases
#display("OK - Fonction définie")
     
#@title extraction liste des clubs de la page "annuaire" => clubs_info_dict {club_id: {name, admins, région}}

# rapatrier liste des clubs

if url_annuaire and not globals().get('clubs_info_dict'):
    display("Rapatriement liste des clubs depuis", url_annuaire, "...")
    global clubs_info_dict
    clubs_info_dict = extract_club_info(url_annuaire)
    display("done: found", len(clubs_info_dict), "clubs!")


#@title manage_club_list: Visualiser et/ou actualiser la liste des clubs participants

def liste_clubs_sommaire():
    "Afficher la liste sommaire des clubs (« club URL ID » avec lien hypertexte)"
    affiche_liste_clubs( format = "short")
    ask("Tapez [Entrée] pour revenir au menu. (La liste va disparaître de l'écran !)")

def liste_clubs_complete():
    "Afficher la liste complète (nom complet + admins avec liens hypertexte)"
    affiche_liste_clubs( format = "html")
    ask("Tapez [Entrée] pour revenir au menu. (La liste va disparaître de l'écran !)")

def actualiser_liste_clubs():
    "Réactualiser / rapatrier la liste des clubs de la page 'annuaire' (cf. ci-dessous)"
    # if globals().get('clubs_info_dict'):
    if cid := extract_club_info(url_annuaire):
        clubs_info_dict.clear()
        clubs_info_dict.update(cid)
        display(f"OK - actualisation effectuée: {len(cid)} clubs trouvés.")
        ask()
    else:
        display("Erreur: aucune information n'a pu être extraite de la page annuaire.")
        ask()

def modifier_url_annuaire():
    "Changer la page 'annuaire' actuelle: '{url_annuaire}'" #.split("//")[-1]
    display("Adresse de la nouvelle page annuaire: (entrez * pour la page par défaut)")
    i = input().strip().lower()
    if not i.startswith("https://"):
        if i == '*': i = default_annuaire
        else: i = "https://" + i.split('//')[-1]
    if ask(f"Etes vous sûr de votre choix: '{i}' ?"):
        globals()['url_annuaire'] = i
    else: ask("OK - opération annulée. Tapez [Entrée] pour continuer.")

def retour_menu_principal(): "Retour au menu principal."; return'return'

def manage_club_list():
    "Visualiser et/ou actualiser la liste des {num_clubs} clubs participants"
    global clubs_info_dict

    display_HTML(f"""<h2>*** Gestion de la liste des clubs ***</h2>
Actuellement la liste contient {len(clubs_info_dict)} clubs.""")
    Menu(choix = {
        1: liste_clubs_sommaire,          2: liste_clubs_complete,
        3: actualiser_liste_clubs,        4: modifier_url_annuaire,
        0: retour_menu_principal
            }, greeting = None, url_annuaire = url_annuaire)

#@title fonction affiche_liste_clubs(dict, format)
#from IPython.display import display, HTML

def affiche_liste_clubs(clubs_info: dict|None = None, format="html"):
    """
    Display club information in various formats ("html", "markdown", "text", "short", "numbered").
    Args:
        clubs_info: A dictionary where keys are club URL IDs and values are dictionaries
                    containing club information, each with keys 'name', 'url', 'admins', and 'highlighted'.
                    If `None`, the global variable `clubs_info_dict` is used.
        output_format: The desired output format.
    """
    debug=0
    if not clubs_info:
        clubs_info = globals().get('clubs_info_dict')
        if not clubs_info:
           display("\nLa liste des clubs est actuellement vide, il faut l'actualiser.\n")
           return
    if debug: display("{len(clubs_info)} clubs to display")
    format = format.lower()

    output = ["*** Liste des clubs ***" if "text"in format
        else  "<h3>Liste des clubs</h3>"] # HTML TAG H3

    if 'short'in format or 'text'in format:
        output += ["(Les « régions » (LFR) sont distinguées par une étoile (*).)\n"]
        if not 'text'in format:
            output[-1] = f"<p>{output[-1]}</p>" # HTML TAG P
    else:
        output += ['<ol>' if 'number'in format else '<ul>'] # HTML TAG OL / UL

    # no explicit numbers if HTML or markdown
    number = 'number'in format and ('text'in format or 'short'in format)

    for url_id, club in clubs_info.items():
        club_url = club.get('url', CLUB_URL_PREFIX + url_id)
        if 'short'in format or not(name := club.get('name')):
            name = url_id
        else:
            name += f" ({url_id})"

        if not'text'in format: 
            name = f'<a href="{club_url}">{name}</a>' # HTML TAG A

        if région := club.get('région'):
            région = ' (*)' if 'short' in format\
                else " (région)" if 'text'in format\
                else' <b>(région)</b>' # HTML TAG B
        else: région = ''

        name += région

        if not'short'in format:
          if admins := club.get('admins'):
            name += ", admins: " + ", ".join(admins if 'text'in format else
                                             map(fmt_user, admins))
        if not('text'in format or 'short'in format):
            name = f"<li>{name}</li>"
        else:
          if number:
              name = f"{number:d}. {name}" # not if HTML or markdown
          if 'short'in format: name += ","

        output += [name]
        if number: number += 1

    if "short" in format:
        output[-1] = output[-1].rstrip(", ") + (
            "." if 'text'in format else ".</p>")
    elif not'text'in format:
        output += ['</ol>' if 'number' in format else "</ul>"] # HTML TAG /OL /UL

    if 'text' in format:
        display(*output, sep="\n")
    else:
        display_HTML( "\n".join(output) )
     

#@title test affichage liste des clubs
if 0:
  #clubs_info_dict
  affiche_liste_clubs( format="html" )
  #affiche_liste_clubs( format="markdown" )
     
"""
fin de la partie "extraction liste clubs de la page web"
Ce n'est que dans la suite qu'on utilisera l'API.
"""

#@title fonctions `fetch_data`,`fetch_club_matches` etc. pour rapatrier données club & rencontres ("match")

API_URL = "https://api.chess.com/pub"

def fetch_data(endpoint):
  """
  Fetch data from the chess.com API, cf. chess.com/news/view/published-data-api/.
  Includes a User-Agent header in the request.
  """
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  }
  response = requests.get(f"{API_URL}/{endpoint}", headers=headers)
  response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
  return response.json()

def fetch_club_data(club_url_id) -> dict:
  """
  Fetch data for a specific club using its "URL ID", which is the same as the
  base name of the club's URL, e.g., 'martinique' for www.chess.com/club/martinique.
  An "extended" `club_url_id` can be provided, e.g., martinique/matches ...
  cf. chess.com/news/view/published-data-api#pubapi-endpoint-club-profile

  Returns: a dict with data depending on the (possibly extended) `club_url_id`.
    For a plain club_url_id, it returns the basic club data:
      {'name':..., 'club_id': API_URL/.../id, 'url': CC_URL/.../id, 'members_count':...,
       'created', 'last_activity', 'country', 'average_rating', 'icon', 'join_request',
       'visibility', 'description', 'rules', 'timezone', 'admin', "description"}

  If the club_id has a "sub-directory" appended, e.g., '{club_id}/members' or
  '{club_id}/matches', then the corresponding, more specific data is returned
  instead: see the dedicated functions below.
  """
  return fetch_data("club/" + club_url_id)

def get_club_members(club_url_id): # Pas vraiment utile
  """
  Fetch the list of members for chess.com/club/{club_url_id}.
  Returns a dictionary with three items: "weekly", "monthly" and "all_time",
  each of which is a list of dicts: {"username": (username:str), "joined": (timestamp:int)}.

  Members are grouped by club-activity frequency, the club-activity being one of:
  * Viewing the club homepage, the club's news index or a specific news article
      (but not the notification message received that the news was published),
  * Viewing the club's forums or a specific forum thread,
  * Changing their club settings, including modifying their membership; for admins,
      this includes inviting or authorizing new members;
  * Viewing the club's tournament, team match, or votechess lists;
  * Viewing club membership lists or running a related search, or viewing the leaderboards for the club
  NB: Playing a club game is not counted as a club-activity!
  """
  return fetch_club_data(club_url_id + "/members")

def fetch_club_matches(club_url_id):
  """
Fetch, store and return the dict of daily and club matches for chess.com/club/{club_url_id}.

The result is a dict with three lists of matches, grouped by status:
{"finished": [...], "in_progress": [...], "registered": [...]}. Each match is a dict
MATCH = { '@id': (URL of team match API endpoint), 'name': (name of the match),
    'opponent': (URL of club profile API endpoint),
    'start_time': (unix timestamp), 'time_class': 'daily' (or ...?),
    (and only for finished matches) 'result': "win" or "lose" or "draw" }

The result is stored in clubs_info_dict[club_url_id]['matches']. If that dict
already exists and is nonempty, it is returned instead of fetching through the API.
  """
  global clubs_info_dict
  if not(club_info := clubs_info_dict.get(club_url_id)):
      clubs_info_dict[club_url_id] = club_info = fetch_club_data(club_url_id)
  if not(matches := club_info.get('matches')):
      club_info['matches'] = matches = fetch_club_data(club_url_id + "/matches")
  return matches

# team matches
"""All team matches-based URLs use the match "ID" to specify which match you want data for.
https://api.chess.com/pub/match/{ID}

The ID is the same as found in the URL for the team match web page on www.chess.com.
For example, the ID WORLD LEAGUE Round 5: Romania vs USA Southwest is 12803.
"""

def fetch_match_data(match_id: str) -> dict:
  """
Fetch data for a specific match using its ID, which may be given with or without
the API prefix, i.e., 'https://api.chess.com/pub/match/1530241' or just '1530241'.

Returns:
    A `dict` containing match data, with keys: '@id': (with API prefix), 'url':...,
      'name':..., 'status': "finished", 'start_time', 'end_time': (unix timestamp),
      'settings': {'rules': "chess", 'time_class': "daily", 'time_control': "1/259200"},
      'boards': (number),  'teams': {'team1': TEAM, 'team2': TEAM}, ...
    TEAM = { "@id": "{API}/club/martinique", "name": "Martinique", "url": CHESSCOM/club/martinique,
      "score": 5, "result": "lose", "players": [PLAYER, ... ], "fair_play_removals": [username,...]}
    PLAYER = { "username": "durvalo", "stats": "{API}/player/durvalo/stats", "status": "basic",
          "played_as_white": "checkmated", "played_as_black": "win", "board": "{API}/match/1713457/5"}
  """
  global all_full_matches_data
  if '/'in match_id: match_id = match_id.split('/')[-1]
  if not(match_data := all_full_matches_data.get(match_id)):
      match_data = fetch_data("match/" + match_id)
      all_full_matches_data[match_id] = match_data
  return match_data


#@title fetch_board() and get_board()

if'boards'not in globals(): boards={}
# This global dict `boards` is indexed by the "full board id" = API URI
# which is also the "reference" given in matches etc.

def fetch_board(board_id):
  """
Fetch and return the BOARD with `board_id`, e.g.: "https://api.chess.com/pub/match/1358985/10",
from the global dict `boards` where it is stored after retrieving it through the API.

BOARD = { "board_scores": { "mf972": 0, "kaumish": 2 }, "games": [GAME1, GAME2] }

GAME = { "url": "https://www.chess.com/game/daily/561587639", "pgn": "[Event ...",
  "time_control": "1/259200", "rated": true, "time_class": "daily",
  "rules": "chess", "fen": "8/5pp1/8/8/4b3/5k2/2q5/4K3 w - - 10 59",
  "start_time": ..., "end_time": 1704992276,
  "white": { "username": "MF972", "@id": "https://api.chess.com/pub/player/mf972",
      "rating": 1548, "result": "resigned", "uuid": "b3ac5630-5441-11eb-922b-abb2decf0f04"
  }, "black": { ... }, "match": "https://api.chess.com/pub/match/1530241",
  "eco": "https://www.chess.com/openings/Kings-Indian-Attack-Yugoslav-Variation...4.d4-Bf5-5.O-O-e6-6.c4",
}
  """
  if board_id[0]!='h':
     display("WARNING: fetch_board expects the API endpoint, not just board number!")
     board_id = "https://api.chess.com/pub/match/"+board_id
  if not(board := boards.get(board_id)):
     boards[board_id] = board = fetch_data( board_id[ board_id.find("match/"): ])
  return board

def get_board(board: dict|str):
    """Fetch the board identified through a string given directly or as entry
'board' in a dict like {"board": "https://api.chess.com/pub/match/1358985/10"}."""
    return fetch_board(board if isinstance(board,str)else board['board'])

##################################################

"""
CFE_joueurs.py
(c) Oct. 2025 by MFH

Part 4. Liste des joueurs multi-équipes
à partir de la liste des rencontres pour un championnat donné, 
établir pour chaque joueur pour quelle équipe il a joué dans quelle rencontre 
=> équipes[joueur] = { club: [matches] }

Part 5. Liste des joueurs par club
Pour un club donné, établir la liste des joueurs qui ont joué pour ce club dans les compét

"""
#@title (3) affiche_joueurs_multiéquipe: Afficher les "joueurs multi-équipes"
def affiche_joueurs_multiéquipe():
    """Afficher les joueurs multi-équipes"""
    global pattern, rencontres

    display_HTML("<h3> Affichage joueurs multi-équipes </h3>") # HTML TAG H3

    if not rencontres.get(pattern):
        display(f"""
Ma liste des rencontres pour la compétition '{pattern}' est vide.
Voulez-vous actualiser la liste pour cette compétition (si le pattern est bon),
ou retourner dans le menu principal pour changer le 'pattern' ?

Entrez 'a' pour actualiser, [Entrée] pour retour :""") #, clear=True)
        i = input().strip().lower()
        if i.startswith('a'): actualiser_liste_rencontres()
        else: return

    if not joueurs.get(pattern):
        display("Calcul des participations aux équipes pour chaque joueur...")
        joueurs[pattern] = players_team_list() # ex - "player_teams_data"

    display_multiteam_players(joueurs[pattern])

    ask("Tapez [Entrée] pour retour au menu principal.")

"""
players_team_list(): dict(équipes => [rencontres]) pour chaque joueur
Pour une liste de rencontres donnée, créer un dict(joueur = {équipe:[rencontres]}) qui donne pour chaque joueur un dict avec les clubs pour lesquels il a joué et les rencontres où il a joué pour ce club. La fonction utilise match_data()
"""

#list(matches)

#@title `players_team_list(matches)` => player_teams = joueurs[pattern] = dict: {joueur: {équipe:[rencontres]}}
# ce dict ...

aliases = {'normandie': 'echiquier-de-normandie'}

def dict_ajout_alias( d: dict, aliases = aliases ):
    for a,b in aliases.items():
        if a in d and not b in d: d[b] = d[a]; display("OK - ajout de :", b)
        elif b in d and not a in d: d[a] = d[b]; display("OK - ajout de :", b)

def players_team_list(matches_data = None,
                      aliases = aliases):
    """
    Identifies players and the teams/matches they played for across the provided
    match data.

    Args:
        matches_data (dict): A dictionary where keys are match IDs and values are
                             dictionaries containing full match data, including 'teams'.
        aliases (dict): if a club has changed name, this allows to
                        "translate" the old name(s) to the new one.
    Returns:
        dict: A dictionary where keys are usernames and values are dictionaries
              mapping club URL IDs to lists of match IDs the player played in for that club.
    """
    if not matches_data:
        if not matches.get('pattern'):
            # this should not happen... [normally done in "actualiser..."]
            matches[pattern] = get_unique_matches( rencontres[ pattern ])
        matches_data = matches[pattern]

    player_teams = {}

    # Iterate through matches and their teams
    for match_id in matches_data:
        match_data = get_match_data( match_id.split('/')[-1] )
        if teams_data := match_data.get('teams'):
            for team_key, team in teams_data.items():
                if players := team.get('players'):
                    club_url_id = team.get('@id', '').split('/')[-1]
                    if club_url_id in aliases:
                       club_url_id = aliases[club_url_id]
                    if club_url_id:
                        for player in players:
                            username = player.get('username')
                            if username:
                                if username not in player_teams:
                                    player_teams[username] = {}

                                if club_url_id not in player_teams[username]:
                                    player_teams[username][club_url_id] = []

                                player_teams[username][club_url_id].append(match_id)
    return player_teams
     

#len(players_team_data)
     

#joueurs_CFE = players_team_list( matches[pattern] )
if 0: joueurs_CFT = players_team_list( matches[pattern] )
if 'joueurs' not in globals():
   joueurs = {} # will contain, for each competition, the players & their teams
     
"""
divers résultats: rencontres ( 'CFT.*26' ) , ...
"""
#rencontres['CFT.*26']

0 and """
  CFE_MTP = [j for j,c in joueurs_CFE.items() if len(c)>1]
  CFT_MTP = [j for j,c in joueurs_CFT.items() if len(c)>1]
  display(CFT_MTP)
"""     

#@title save/load "full match data"
filename = "all_full_matches_data.pickle"
0 and """
if 0:
  save_data(all_full_matches_data, filename)
if 0:
  if globals().get(var := 'all_full_matches_data'):
      if ask(f"are you sure you want to erase existing {var!r}? "):
        pass
      else: raise Exception("User interrupt")
  if d := load_data(filename):
     globals()[var] = d
  else: display(f"no data in file {filename!r}")
"""

#len(all_full_matches_data)
"""     
display multiteam players function
A function that will take the player-teams dictionary as input and display the information for players who played on multiple teams.
"""
#@title [26] display_multiteam_players()

def display_multiteam_players(player_teams_data: dict,
                              clubs_info_dict: dict|None = None):
    """
    Displays information for players who have played for more than one team,
    including the teams and the matches they played in for each team.

    Args:
        player_teams_data: A dictionary where keys are usernames and values are dictionaries
                                  mapping club URL IDs to lists of match IDs the player played in for that club.
        all_full_matches_data: A dictionary where keys are match IDs and values are
                                     dictionaries containing full match data.
        clubs_info_dict: A dictionary where keys are club URL IDs and values are dictionaries
                                containing club details (name, admins, highlighted).
    """
    if not clubs_info_dict:
        clubs_info_dict = globals()["clubs_info_dict"]
    output = [ f"<h3>Joueurs multi-équipe (compétition '{pattern}')</h3>\n<ul>" ] # HTML TAG H3 / UL
    #display("=" * 80)

    found_multiteam_players = False

    for username, teams in player_teams_data.items():
        if len(teams) > 1:
            found_multiteam_players = True
            output += [f"<li>Joueur: {fmt_user(username)}\n<ul>"]# HTML TAG LI / UL

            for club_id, match_ids in teams.items():
                # Get club name from clubs_info_dict if available, otherwise use the club_id
                club_name = clubs_info_dict.get(club_id, {}).get('name', club_id)
                output += [ f"""<li>Team&nbsp;: {fmt_club(club_id, club_name)} -
                    Rencontres&nbsp;:""" ]
                output += [ "<ul>" + "\n<li>".join(
                        fmt_match(match_id) for match_id in match_ids )+ "</li>\n</ul>"
                    if match_ids else "pas de rencontre trouvée" ] # shouldn't happen
            output += [ "</li></ul>" ] # fin liste teams

    if not found_multiteam_players:
        output += ["<li>pas de joueurs multi-équipe trouvés !</li>"]# HTML TAG LI

    output += [ "</li></ul>" ] # fin liste joueurs # HTML TAG /LI /UL
    display_HTML(("\n".join(output)))

# Example usage (assuming player_teams_data, all_full_matches_data, and clubs_info_dict are available)
# player_teams_data = check_multiteam_players(all_full_matches_data) # Assuming check_multiteam_players is updated to return the dict
# display_multiteam_players(player_teams_data, all_full_matches_data, clubs_info_dict)

#display_multiteam_players( joueurs_CFE )
#len(all_full_matches_data   )
#joueurs == player_teams_data
"""
Call the check_ & display_multiteam_players functions:
Call the newly defined display_multiteam_players function with the player_teams_data, all_full_matches_data, and clubs_info_dict to display the multi-team player information.

N.B.: there is no more "check..." function. The display_multiteam_players function checks and outputs accordingly. It receives the player_teams_data which is now globally stored in joueurs[pattern].
"""     


#@title player_teams_data = check_multiteam_players(all_full_matches_data)
# Call the check_multiteam_players function to get the player_teams_data
0 and """
if not globals().get('player_teams_data') or (i := input(
      "Really want to redefine 'player_teams_data'? ")
      ) and i.lower()[0]=='y':
    player_teams_data = check_multiteam_players(all_full_matches_data)
"""     

#@title display_multiteam_players(player_teams_data)
# Call the display_multiteam_players function to display the results
#display_multiteam_players(player_teams_data, all_full_matches_data, clubs_info_dict)
     
### 5. liste des joueurs par club

#@title get_club_players_list(club_id,  status): liste des joueurs ('actifs') d'un club
def get_club_players_list(club_id,  status = ('in_progress','registered')):
    """Renvoit la liste des joueurs [de compétitions en cours et à venir] d'un club donné.
    En général la liste des joueurs d'un club n'est pas publique.
    On passe donc par la liste des rencontres du club, dont on considère les joueurs.
    """
    if not(players := clubs_info_dict[club_id].get('players', set() )):
        clubs_info_dict[club_id]['players'] = players
        # attention : ceci est la liste (list !) des rencontres "aplatie" !
        match_list = get_club_matches(club_id, pattern='', status=status)
        for mat in match_list: # matches is a list
            #if mat.get('status') in status:
            if match_id := mat.get('@id'): #.split('/')[-1]
               if match_data := get_match_data( match_id ):
                  for team in match_data['teams'].values():
                      if team['@id'].endswith(club_id):
                        players |= { player['username'] for player in team['players'] }
    return players
     

#@title choix_du_club()
def choix_du_club():
    club_id = 0
    display("""Choisissez le club en donnant son `url_id` (comme 'martinique') ou son numéro
       dans la liste suivante:\n""")
    affiche_liste_clubs(format="number short")
    while not club_id:
          display("Votre choix? ")
          i = input().strip()
          if i.isdigit():
            if 0 < (i := int(i)) <= len(clubs_info_dict):
                club_id = list(clubs_info_dict)[i-1]
            else: display("Ce numéro n'est pas dans la liste !")
          elif i in clubs_info_dict:
              club_id = i
          else: display("Ce club n'est pas connu!")
    return club_id
     

#@title `list_players_by_club(club_id = None)`
def list_players_by_club(club_id = None):
    "Afficher la liste des joueurs pour un club donné."
    # la fonction est "interactive" seulement si club_id n'est pas donné
    if not club_id:
       display("""\n*** Affichage de la liste des joueurs par club. ***\n""")
       club_id = choix_du_club() ; interactif = True
    else: interactif = False
    # maintenant le club_id est défini
    players = get_club_players_list(club_id)
    display_HTML((f"<dl><dt>Joueurs du club {fmt_club(club_id)}:</dt>\n<dd>" # HTML TAG DL / DT / DD
        + ",\n".join(fmt_user(p) for p in players) + "\n</dd></dl>")) # HTML TAG /DD /DL
    if interactif: ask()

##################################################

"""
CFE_timeout.py
Module with functions to manage timeouts in LFR/CFE/CFT chess competitions.
(c) Oct. 2025 by MFH

Provides:
- afficher_liste_timeout_joueur(player)
- afficher_liste_timeout_club(club)
"""
# 8. Parties perdues par timeout pour les joueurs d'un club donné

#@title afficher_liste_timeout_joueur(player)

"""example: https://api.chess.com/pub/player/mf972/matches
  "finished": [ # our get_player_matches() returns a flattened list of {...}
    {
      "name": " Team Elite National vs Chess.com Schachmatt",
      "url": "https://www.chess.com/club/matches/1530241",
      "@id": "https://api.chess.com/pub/match/1530241",
      "club": "https://api.chess.com/pub/club/chess-com-schachmatt",
      "results": {
        "played_as_black": "resigned",
        "played_as_white": "resigned"
      },
      "board": "https://api.chess.com/pub/match/1530241/1"
    },...]
"""

def afficher_liste_timeout_joueur(player: str|None = None,
                                  selection = -31556952*2, # = 365.2425 * 86400 * 2
                                  debug:int = 1):
    "Afficher la liste des rencontres perdues au temps pour un joueur donné."
    """ # NB : la ligne ci-dessus est le titre dans le menu !!
`selection` peut être une fonction qui s'applique au match_data, ou un regex pattern
sous forme de `str` ou `re.Pattern` (compilé), ou None (selectionner tout),
ou un nombre qui indique la date "de départ" sous forme de "unix timestamp" ou
en année si entre 2000 et 2100 ou en secondes avant aujourd'hui si négatif.
Donc un argument de -31556952 = -365.2425 * 86400 indique (aujourd'hui - 1 an)."""

    # selection
    if debug>1: display(f"Utilisation de {selection = }")
    if isinstance(selection, str|re.Pattern):
        pattern = re.compile(selection)
        selection = lambda m: pattern.search(m['name'])
    elif isinstance(selection, int|float):
        # It doesn't make sense to give a "start date" in the future,
        # so it makes only sense for negative numbers to be considered
        # "relative" and added to `now`(= current timestamp).
        # We can safely consider numbers in 2000 .. 2100 as years (although only
        # between 2007 (when chess.com was created) and today really makes sense).
        # We'll consider all other nonnegative numbers as "absolute" timestamps,
        # which allows to select *all* matches with timestamp = 0 or 1 (~ 1970).
        # (To get an idea: timestamp(year 2002) ~ 32 * 365.2425 * 86400 ~ 1e9.)
        select_start_time = time.time()+selection if selection < 0 else (
            selection-1970)*31556952 if 2000 < selection < 2100 else selection
        # `player_matches` has lightweight dicts that doesn't have a "start_time"
        # which is only available in the full game data available through "boards".
        ## We retreive that only if really needed - if there's no result, we don't.
        ## 'timeout' in m.get('results',{}).values() and (N:=N+1) and
        selection = lambda m: any(g.get('end_time',0) > select_start_time
                                  for g in get_board(m).get('games'))
    else: selection = lambda m:1 # tout selectionner

    # 1 : get player name
    if player: interactive = False
    else:
        interactive = True
        display_HTML((
            "<h3>Affichage des rencontres perdues au temps pour un joueur donné.</h3>"))

        display("Entrez le nom du joueur: (Le 'username' avec ou sans '@' au début)")
        player = input().strip().lower()
        if not player: return
    if player[0]=='@': player = player[1:] #.lstrip('@')

    # 2 : get player matches
    if not(player_matches := get_player_matches(
            player, status=('in_progress','finished'), as_dict=True)):
        display_HTML((f"""Aucun match trouvé pour '{fmt_user(player)}'. {
              " (Faute de frappe ?)"if interactive else''}"""))
        if interactive: ask()
        return
    if interactive:
      display_HTML((
        f"{len(player_matches)} rencontres trouvées pour {fmt_user(player)}."))
      if ask("Afficher?"): display_HTML(("<ul><li>" + "</li>\n<li>".join( # HTML tag UL / LI
          fmt_match(m['@id']) for m in player_matches)  + "\n</ul>"))   # HTML tag /UL

    # 3 : list of timeouts
    played_as = { 'played_as_'+c for c in ('black', 'white') }
    timeouts = [] ; other_timeouts = 0 ; N = 0
    for match_data in player_matches:
        # remember that the "player/.../matches" is a "light" version of the match data.
        # but it does have an entry 'results': { "played_as_...": result }
        # if debug and 'results' not in match_data:
        #   display_HTML((f"""<dd>ERROR: no results in match of player {fmt_user(player)}:
        #      <dt>{fmt_match(match_data['@id'])}</dl>"""))
        if "timeout" in match_data.get('results',{}).values():
            N += 1
            if selection(match_data):
                if debug>2:display(f"Le nom {match_data['name']} correspond, on l'ajoute.")
                timeouts.append(match_data)
            else:
                other_timeouts += 1
                if debug>2: display(f"Le nom {match_data['name']} ne correspond pas, on l'ajoute pas")

    # 4 : display
    Nm = len(player_matches) ; pourcent = f" = {N/Nm*100:.0f}%" if N else ''
    if timeouts:
      output = [f"""<h3>Rencontres perdues au temps par {fmt_user(player)}:</h3>
({len(timeouts)} 'timeout' <b>retenus</b> sur un total de {N}{pourcent} dans {Nm} rencontres)\n<ul>"""]
      output.extend(f"<li>{fmt_match(m['@id'])}</li>" for m in timeouts)
      output += ["</ul>"]
    else: # no timeouts retenus
      output = [f"<h3>{fmt_user(player)} " + (
          f"a perdu {N}{pourcent}  (tous hors sélection)" if N else "n'a perdu aucune"
        )+f" par 'timeout', sur un total de {Nm} rencontres.</h3>"]
    #if other_timeouts:
    #  output += [f"<p><b>N.B.:</b> {other_timeouts} autres 'timeout' trouvés"
    #             " dans des rencontres hors sélection.</p>"]
    display_HTML(( '\n'.join(output) ))
    if interactive: ask()

# TESTS
#re.compile('202[56]').search("TEAM 2026ANTILLES FRANÇAISES vs Islas Malvinas")
#type(s)
#re.compile(None)
     
#@title afficher_liste_timeout_club() # limité aux rencontres avec 2025 & 2026 dans leur nom
def afficher_liste_timeout_club(club = None):
    """Liste des rencontres perdues au temps pour chaque joueur d'un club donné
     (Par défaut limité aux rencontres terminées il y a moins d'un an)."""
    display("*** Affichage des 'timeout' pour tous les joueurs d'un club ***\n")
    if club is None: club = choix_du_club()
    players = get_club_players_list(club)
    for p in players:
        afficher_liste_timeout_joueur(p, selection = -31556952*2) # (J - 2 ans)
    ask()

##################################################

#@title menu principal

def quitter():
    "Quitter le programme."
    display("Au revoir et à bientôt !")
    return'return'

