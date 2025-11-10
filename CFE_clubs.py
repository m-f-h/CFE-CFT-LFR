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

display = __main__.display

global display, HTML #= make_global('display', 'HTML')

#@title manage_club_list: Visualiser et/ou actualiser la liste des clubs participants

if not globals().get('default_annuaire'):
    default_annuaire = "https://www.chess.com/fr/announcements/view/annuaire-des-equipes-locales"
    url_annuaire = default_annuaire

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
        print(f"OK - actualisation effectuée: {len(cid)} clubs trouvés.")
        ask()
    else:
        print("Erreur: aucune information n'a pu être extraite de la page annuaire.")
        ask()

def modifier_url_annuaire():
    "Changer la page 'annuaire' actuelle: '{url_annuaire}'" #.split("//")[-1]
    print("Adresse de la nouvelle page annuaire: (entrez * pour la page par défaut)")
    i = input().strip().lower()
    if not i.startswith("https://"):
        if i == '*': i = default_annuaire
        else: i = "https://" + i.split('//')[-1]
    if ask(f"Etes vous sûr de votre choix: '{i}' ?"):
        globals()['url_annuaire'] = i
    else: ask("OK - opération annulée. Tapez [Entrée] pour continuer.")

def retour_menu_principal(): "Retour au menu principal."; return'return'

def manage_club_list():
    """Visualiser et/ou actualiser la liste des {num_clubs} clubs participants"""
    if 'do_menu'not in globals():
        print(""""Ne peux afficher ce menu, la fonction 'do_menu' n'est pas encore définie!
        (Et probablement la liste des clubs n'a pas encore été rapatriée...""")
        return # ask() # ne pas interrompre le script en cas de test prématuré

    clubs_info_dict = globals().get('clubs_info_dict', {}) # affiche une liste vide si non définie

    display(HTML(f"""*** Gestion de la liste des clubs ***
Actuellement la liste contient {len(clubs_info_dict)} clubs."""))
    do_menu({
        1: liste_clubs_sommaire,          2: liste_clubs_complete,
        3: actualiser_liste_clubs,        4: modifier_url_annuaire,
        0: retour_menu_principal
            }, None, url_annuaire = url_annuaire)
     

#@title test du menu `manage_club_list` - possible si `do_menu`, `clubs_info_dict` etc. sont bien définis (plus loin)!
# ce qui n'est a priori pas le cas ici, si certaines cellules plus loin n'ont pas encore été exéctuées.
if 'test'*0:            # une vérification que  'do_menu' et 'clubs_info_dict' sont
  if 'do_menu'in globals():  # bien définis a été intégrée dans 'manage_club_list', mais
    manage_club_list()  # dans le cas contraire cela interrompt le script !
  else: print("Test impossible, fonctions et données nécessaires pas encore définies!")


#@title `extract_club_info()`: extraction liste équipes d'une page web

CLUB_URL_PREFIX = "https://www.chess.com/club/"
def extract_club_info(url, debug=1):
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
        if debug>1: print("OK, page retrieved.")
        soup = BeautifulSoup(response.content, 'html.parser')
        if debug>1: print("Page parsed successfully.")

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
                items = str(p_element).split('')
                if debug: display(f"  Number of items (lines): {len(items)}")
                # print(f"  First few items: {items[:5]}...") # Optional: print first few items

                # Check if this paragraph seems to contain the club list
                contains_url = any(CLUB_URL_PREFIX in item for item in items)
                if debug: display(f"  Contains club URL pattern: {contains_url}")
                if not contains_url: continue # goto next paragraph
                if len(items) < 10:
                    if debug: display("...but not enough lines.");
                    continue

                if debug: print("Found paragraph likely containing the club list.")
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
#print("OK - Fonction définie")
     

     

#@title extraction liste des clubs de la page "annuaire" => clubs_info_dict {club_id: {name, admins, région}}

# URL of the page with the list of clubs
default_annuaire = url_annuaire = "https://www.chess.com/fr/announcements/view/annuaire-des-equipes-locales"

# Extract the list / dict of clubs + information, if not yet defined
if not globals().get('clubs_info_dict'):
    globals()['clubs_info_dict'] = extract_club_info(url_annuaire)

if 0:
  région = "région"
  for t,c in clubs_info_dict.items():
    if région in c and not c[région]: del c[région]
    else: c[région]=True
  clubs_info_dict
     

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
           print("\nLa liste des clubs est actuellement vide, il faut l'actualiser.\n")
           return
    if debug: print("{len(clubs_info)} clubs to display")
    format = format.lower()

    output = ["*** Liste des clubs ***" if "text"in format else
      "Liste des clubs"]

    if 'short'in format or 'text'in format:
        output += ["(Les « régions » (LFR) sont distinguées par une étoile (*).)\n"]
        if not 'text'in format: output[-1] = f"{output[-1]}"
    else:
        output += ['' if 'number'in format else '']

    # no explicit numbers if HTML or markdown
    number = 'number'in format and ('text'in format or 'short'in format)

    for url_id, club in clubs_info.items():
        club_url = club.get('url', CLUB_URL_PREFIX + url_id)
        if 'short'in format or not(name := club.get('name')):
            name = url_id
        else:
            name += f" ({url_id})"

        if not'text'in format: name = f'{name}'

        if région := club.get('région'):
            région = ' (*)' if 'short' in format else " (région)" if 'text'in format else' (région)'
        else: région = ''

        name += région

        if not'short'in format:
          if admins := club.get('admins'):
            name += ", admins: " + ", ".join(admins if 'text'in format else
                                             map(fmt_user, admins))
        if not('text'in format or 'short'in format):
            name = f"{name}"
        else:
          if number:
              name = f"{number:d}. {name}" # not if HTML or markdown
          if 'short'in format: name += ","

        output += [name]
        if number: number += 1

    if "short" in format:
        output[-1] = output[-1].rstrip(", ") + ("." if 'text'in format else ".")
    elif not'text'in format:
        output += ['' if 'number' in format else ""]

    if 'text' in format:
        print(*output, sep="\n")
    else:
        display(HTML( "\n".join(output) ))
     

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
     print("WARNING: fetch_board expects the API endpoint, not just board number!")
     board_id = "https://api.chess.com/pub/match/"+board_id
  if not(board := boards.get(board_id)):
     boards[board_id] = board = fetch_data( board_id[ board_id.find("match/"): ])
  return board

def get_board(board: dict|str):
    """Fetch the board identified through a string given directly or as entry
'board' in a dict like {"board": "https://api.chess.com/pub/match/1358985/10"}."""
    return fetch_board(board if isinstance(board,str)else board['board'])
