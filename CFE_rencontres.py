#!/usr/bin/env python3                           -*- coding: utf-8 -*-
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
import __main__ as GLOBALS
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
          print(end = f"Lecture liste des rencontres pour {club_url_id!r}...")
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
                # print(f"{status}: {matches}") # usually a comment
            filtered_matches.extend(match for match in matches
                                    if regex.search(match['name']))
        if filtered_matches:
          if debug:
             print(f" Success: {len(filtered_matches)} matches.")
        else:
          if debug:
            print("No match data available.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching matches for club {club_url_id}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching matches for club {club_url_id}: {e}")

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
    if not pattern: pattern = globals()['pattern']

    print(f"Recherche rencontres '{pattern}' pour {len(clubs_to_process)} clubs...")
    print("-" * 80)

    for url_id in clubs_to_process:
        filtered_matches = get_club_matches(url_id, pattern = pattern)
        if filtered_matches:
            club_matches_data[url_id] = filtered_matches

    print("-" * 80)
    print(f"Finished processing match data for {len(club_matches_data)} clubs with filtered matches.")

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

    if not pattern : pattern = globals()['pattern']

    global club_matches_data
    if 'club_matches_data' not in globals(): club_matches_data = {}

    if pattern not in club_matches_data:
        club_matches_data[pattern] = {}

    elif club_matches_data[pattern]:
        print(f"""La liste des rencontres '{pattern}' existe déjà ({
            len(club_matches_data[pattern])} entrées).
        Etes vous sûr de vouloir la recharger ?""")
        while not(i := input().strip().lower()): continue
        if i.startswith('n'):
            print("OK -- opération annulée. Appuyez sur [Entrée] pour continuer.")
            input(); return
        #    raise Exception("User interrupt")
    if cmd := make_club_matches_data(pattern=pattern):
        print("OK -", len(cmd), " rencontres trouvées.")
        club_matches_data[pattern] |= cmd
    else: print(f"Aucune rencontre trouvée pour '{pattern}'.")

    global matches
    matches[ pattern ] = get_unique_matches( club_matches_data[ pattern ])

    return club_matches_data[pattern]

if 0:
  print("compétition / pattern =", pattern)# := 'CFE *2025')
  if 'matches'not in vars(): matches={}
  print(f'Found {len(matches[pattern])} matches for {pattern!r}.')

if 0: # Fetch *all* matches for a specific list of clubs ### OBSOLETE / UNUSED ####
   selected_clubs = ["la-reine-danjou"] #"martinique", "bretagne-echecs"]
   all_matches_for_selected_clubs = make_club_matches_data(clubs=selected_clubs)
   for c,m in all_matches_for_selected_clubs.items():
      print(f"Found {len(m)} matches for {c!r}.")
if 0: # Fetch matches for a given list of clubs & pattern ### OBSOLETE / UNUSED ####
   matches_for_selected_clubs = make_club_matches_data(selected_clubs,
                                                       pattern := "LFR2025")
   print("Adding these to global 'club_matches_data':")
   for c,m in matches_for_selected_clubs.items():
      print(f"Adding {len(m)} matches for {c!r}, with {pattern = !r}.")
      club_matches_data[c] = club_matches_data.get(c,[]) + m
'''
#@title divers essais
if 0:
  print(len(cmd := dict(club_matches_data)))
  club_matches_data.clear()
  club_matches_data['LFR2025']=cmd

if 0:
  cmd = club_matches_data[pattern]
  print(pattern, ":", len(cmd), "clubs.")
if 0:
  for match in cmd['team-ajaccio']:
    print(match['name'])
if 0: cmd['team-ajaccio']
if 0: print("Found", s := sum(len(m)for m in cmd.values()),
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
                      print("WARNING: inconsistent data for {match_id}:")
                      print(club_id, match, m)
                else: # if not yet present, add "teams" information
                  m = match | { 'teams': teams } # NB: do NOT re-initialize 'match'!!
                  m.pop('opponent')
                  unique_matches[match_id] = m
            else:
                print(f"Warning! no '@id' in {match} of {club_id}!")

    return unique_matches

# Example usage (assuming club_matches_data is available from a previous step):
# all_unique_ids = get_unique_match_ids(club_matches_data)
# print(f"Found {len(all_unique_ids)} unique match IDs.")
     

#list(matches)
#list(club_matches_data)
     

if 0:
  print("compétition / pattern =", pattern)# := 'CFE *2025')
  if 'matches'not in vars(): matches={}
  matches[ pattern ] = get_unique_matches( club_matches_data[ pattern ])
  print(f'Found {len(matches[pattern])} matches for {pattern!r}.')
     

#display( club_matches_data[ pattern ]['team-provence'])
# len(club_matches_data[ pattern ])
# len( player_teams_data )

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
        if debug: print(f"Returning cached data for match ID: {match_id}")
        return all_full_matches_data[match_id]

    # If not in the dictionary, fetch the data using get_match_data
    try:
        print(f"Fetching full data for match ID {match_id}...", end="")
        full_data = fetch_match_data(match_id)
        # Store the fetched data in the global dictionary
        print(f" Success.")
        return full_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for match ID {match_id}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching data for match ID {match_id}: {e}")

# Example usage:
# match_id_example = "1713457" # Replace with an actual match ID
# full_match_info = get_match_data(match_id_example)
# if full_match_info:
#     print("\nFull match data example:")
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
           print("Aucune liste de rencontres établie. Veuillez 'a'ctualiser la compétition !")
           return ask()
        if len(gm) > 1 :
            print(f"""Afficher les rencontres pour la compèt {pattern!r} actuellement choisie,
  ou pour toutes les rencontres: {", ".join(
      f'{p} ({len(m)})' for p,m in gm.items() )} ? [a = actuel / t = toutes]""")
            if( input().strip().lower().startswith('t')):
                matches = sum((list(m) for m in gm.values()), [])
            elif not(matches := gm.get(pattern)):
                print(f"""Aucun match connu pour la compèt '{pattern}' !
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

    print("Rencontres triées par date de départ :",
          "=" * 60,
          "Début - Fin  -  Résultat  -  Nom de la rencontre", sep="\n")
    #      2025-10-10 - ?  1 - 0
    for match in sorted_matches:
        # Print in the desired format
        print('-'.join(fmt_date(match.get(t+'_time'))for t in('start','end')),
              ' - '.join(get_score('team'+i) for i in'12'),
              match.get('name'), sep=', ')

    print("=" * 60)

#affiche_rencontres()#( matches[pattern] )

#@title essais obscurs
if 0:
  # Fetch LFR2025 matches for all clubs and store in a championship-specific dictionary
  lfr_2025_club_matches_data = make_club_matches_data(pattern="LFR2025.*")

  # Get the unique match IDs for the LFR2025 championship
  lfr_2025_unique_match_ids = get_unique_match_ids(lfr_2025_club_matches_data)

  print(f"\nTotal unique match IDs found for LFR2025 championship: {len(lfr_2025_unique_match_ids)}")

  # Now lfr_2025_unique_match_ids contains the set of unique match IDs for LFR2025 matches.
  # We can proceed to fetch full data for these IDs if needed and display them.

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
        if len(status) < len(old): print(f"Warning: some in {old} were ignored.")
        elif len(status) > 3 : # there must be duplicates -- should not happen
            print(f"Warning: duplicates in {status = } -- should not happen! {old =}")
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
        if debug: print(end = f"Fetching data for player '{username}'... ")
        try: player_matches = fetch_data(f'player/{username}/matches')
        except:
            print(f"ERROR: can't get data for {player = }. Do they exist?)")
            ask(); return()
        if player_matches:
          if debug: print("success:", ' + '.join(f'{len(m)} {s}' for s,m
                                                 in player_matches.items()))
          if debug > 1: print(player_matches)
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
        print("Entrez le nom du joueur: (Le 'username' avec ou sans '@' au début)")
        username = input().strip().lower()
        if not username: return

    if username[0]=='@': username = username[1:] #.lstrip('@')

    if not(player_matches := get_player_matches(username, status = status)):
        print(f"Aucun match trouvé pour '{username}'. (Faute de frappe ?)")
        ask() ; return

    output = f"Joueur {fmt_user(username)} — Rencontres :\n\n"

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
    display(HTML(output + "\n"))
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
    print(f"Weird - this should not happen: match {match_id!r} not found in data for {username!r}.")
    return True # so it shows up in the list - just in case
     

#affiche_rencontres_joueur("deep-blou")
if 0: all_full_matches_data['1848645' if 0 else '1776070']
if 0: display( min(all_full_matches_data.items()))
#joueurs['madameapprentie']#.clear()
#list(matches)#players_team_list
     

#@title `affiche_rencontres_joueurs_club()`
def affiche_rencontres_joueurs_club():
    "Affiche la liste des rencontres pour chaque joueur d'un club donné."
    print("*** Affichage des rencontres pour tous les joueurs d'un club ***\n")
    club_id = choix_du_club()
    players = get_club_players_list(club_id)
    for p in players:
        affiche_rencontres_joueur(p)
    ask()
