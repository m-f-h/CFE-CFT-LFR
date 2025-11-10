#!/usr/bin/env python3                           -*- coding: utf-8 -*-
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
    if debug>1: print(f"Utilisation de {selection = }")
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
        display(HTML(
            "Affichage des rencontres perdues au temps pour un joueur donné."))

        print("Entrez le nom du joueur: (Le 'username' avec ou sans '@' au début)")
        player = input().strip().lower()
        if not player: return
    if player[0]=='@': player = player[1:] #.lstrip('@')

    # 2 : get player matches
    if not(player_matches := get_player_matches(
            player, status=('in_progress','finished'), as_dict=True)):
        display(HTML(f"""Aucun match trouvé pour '{fmt_user(player)}'. {
              " (Faute de frappe ?)"if interactive else''}"""))
        if interactive: ask()
        return
    if interactive:
      display(HTML(
        f"{len(player_matches)} rencontres trouvées pour {fmt_user(player)}."))
      if ask("Afficher?"): display(HTML("" + "\n".join(
          fmt_match(m['@id']) for m in player_matches)  + "\n"))

    # 3 : list of timeouts
    played_as = { 'played_as_'+c for c in ('black', 'white') }
    timeouts = [] ; other_timeouts = 0 ; N = 0
    for match_data in player_matches:
        # remember that the "player/.../matches" is a "light" version of the match data.
        # but it does have an entry 'results': { "played_as_...": result }
        # if debug and 'results' not in match_data:
        #   display(HTML(f"""ERROR: no results in match of player {fmt_user(player)}:
        #      {fmt_match(match_data['@id'])}"""))
        if "timeout" in match_data.get('results',{}).values():
            N += 1
            if selection(match_data):
                if debug>2:print(f"Le nom {match_data['name']} correspond, on l'ajoute.")
                timeouts.append(match_data)
            else:
                other_timeouts += 1
                if debug>2: print(f"Le nom {match_data['name']} ne correspond pas, on l'ajoute pas")

    # 4 : display
    Nm = len(player_matches) ; pourcent = f" = {N/Nm*100:.0f}%" if N else ''
    if timeouts:
      output = [f"""Rencontres perdues au temps par {fmt_user(player)}:
({len(timeouts)} 'timeout' retenus sur un total de {N}{pourcent} dans {Nm} rencontres)\n"""]
      output.extend(f"{fmt_match(m['@id'])}" for m in timeouts)
      output += [""]
    else: # no timeouts retenus
      output = [f"{fmt_user(player)} " + (
          f"a perdu {N}{pourcent}  (tous hors sélection)" if N else "n'a perdu aucune"
        )+f" par 'timeout', sur un total de {Nm} rencontres."]
    #if other_timeouts:
    #  output += [f"N.B.: {other_timeouts} autres 'timeout' trouvés"
    #             " dans des rencontres hors sélection."]
    display(HTML( '\n'.join(output) ))
    if interactive: ask()

# TESTS
#re.compile('202[56]').search("TEAM 2026ANTILLES FRANÇAISES vs Islas Malvinas")
#type(s)
#re.compile(None)
     
#@title afficher_liste_timeout_club() # limité aux rencontres avec 2025 & 2026 dans leur nom
def afficher_liste_timeout_club(club = None):
    """Liste des rencontres perdues au temps pour chaque joueur d'un club donné
     (Par défaut limité aux rencontres terminées il y a moins d'un an)."""
    print("*** Affichage des 'timeout' pour tous les joueurs d'un club ***\n")
    if club is None: club = choix_du_club()
    players = get_club_players_list(club)
    for p in players:
        afficher_liste_timeout_joueur(p, selection = -31556952*2) # (J - 2 ans)
    ask()
