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

    display(HTML(" Affichage joueurs multi-équipes "))

    if not rencontres.get(pattern):
        print(f"""
Ma liste des rencontres pour la compétition '{pattern}' est vide.
Voulez-vous actualiser la liste pour cette compétition (si le pattern est bon),
ou retourner dans le menu principal pour changer le 'pattern' ?

Entrez 'a' pour actualiser, [Entrée] pour retour :""") #, clear=True)
        i = input().strip().lower()
        if i.startswith('a'): actualiser_liste_rencontres()
        else: return

    if not joueurs.get(pattern):
        print("Calcul des participations aux équipes pour chaque joueur...")
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
        if a in d and not b in d: d[b] = d[a]; print("OK - ajout de :", b)
        elif b in d and not a in d: d[a] = d[b]; print("OK - ajout de :", b)

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

if 0:
  CFE_MTP = [j for j,c in joueurs_CFE.items() if len(c)>1]
  CFT_MTP = [j for j,c in joueurs_CFT.items() if len(c)>1]
  display(CFT_MTP)
     

#@title save/load "full match data"
filename = "all_full_matches_data.pickle"
if 0:
  save_data(all_full_matches_data, filename)
if 0:
  if globals().get(var := 'all_full_matches_data'):
      if ask(f"are you sure you want to erase existing {var!r}? "):
        pass
      else: raise Exception("User interrupt")
  if d := load_data(filename):
     globals()[var] = d
  else: print(f"no data in file {filename!r}")


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
    output = [ f"Joueurs multi-équipe (compétition '{pattern}')\n" ]
    #print("=" * 80)

    found_multiteam_players = False

    for username, teams in player_teams_data.items():
        if len(teams) > 1:
            found_multiteam_players = True
            output += [f"Joueur: {fmt_user(username)}\n"]
            for club_id, match_ids in teams.items():
                # Get club name from clubs_info_dict if available, otherwise use the club_id
                club_name = clubs_info_dict.get(club_id, {}).get('name', club_id)
                output += [ f"""Team : {fmt_club(club_id, club_name)} -
                    Rencontres :""" ]
                output += [ "" + "\n".join(
                        fmt_match(match_id) for match_id in match_ids )+ "\n"
                    if match_ids else "pas de rencontre trouvée" ] # shouldn't happen
            output += [ "" ] # fin liste teams
    if not found_multiteam_players:
        output += ["pas de joueurs multi-équipe trouvés !"]

    output += [ "" ] # fin liste joueurs
    display(HTML("\n".join(output)))
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
if 0:
  if not globals().get('player_teams_data') or (i := input(
      "Really want to redefine 'player_teams_data'? ")
      ) and i.lower()[0]=='y':
    player_teams_data = check_multiteam_players(all_full_matches_data)
     

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
    print("""Choisissez le club en donnant son `url_id` (comme 'martinique') ou son numéro
       dans la liste suivante:\n""")
    affiche_liste_clubs(format="number short")
    while not club_id:
          print("Votre choix? ")
          i = input().strip()
          if i.isdigit():
            if 0 < (i := int(i)) <= len(clubs_info_dict):
                club_id = list(clubs_info_dict)[i-1]
            else: print("Ce numéro n'est pas dans la liste !")
          elif i in clubs_info_dict:
              club_id = i
          else: print("Ce club n'est pas connu!")
    return club_id
     

#@title `list_players_by_club(club_id = None)`
def list_players_by_club(club_id = None):
    "Afficher la liste des joueurs pour un club donné."
    # la fonction est "interactive" seulement si club_id n'est pas donné
    if not club_id:
       print("""\n*** Affichage de la liste des joueurs par club. ***\n""")
       club_id = choix_du_club() ; interactif = True
    else: interactif = False
    # maintenant le club_id est défini
    players = get_club_players_list(club_id)
    display(HTML(f"Joueurs du club {fmt_club(club_id)}:\n" +
      ",\n".join(fmt_user(p) for p in players) + "\n"))
    if interactif: ask()
