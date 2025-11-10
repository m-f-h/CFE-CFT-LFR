#!/usr/bin/env python3                           -*- coding: utf-8 -*-
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
display, HTML = make_global('display', 'HTML')

# sous-routine : pour le(s) paragraphe(s) de la page qui contient une liste des
# noms et url des clubs, extraire le nom et le club_id = basename(url).

def extract_id_and_name(src: str, debug=0):
    """
    Extract the name (= pure text with punctuation trimmed)
    `html` should contain exactly one href="...".
    The line is assumed to be of the form, as in ...)
    Bordeaux: https://www.chess.com/club/bordeauxGrenoble: https://www.chess.com/club/grenoble-echecs-metropoleIsbergues: https://www.chess.com/club/la-tour-infernaleMontpellier: https://www.chess.com/club/team-montpellier Paris neuf trois: https://www.chess.com/club/paris-neuf-trois Rennes: https://www.chess.com/club/rennes Strasbourg: https://chess.com/club/team-strasbourg Toulouse: https://www.chess.com/club/team-toulouse-equipa-tolosa 
    sometimes no ':', sometimes   interspersed ...
    or as in https://www.chess.com/fr/announcements/view/calendrier-lfr2025-en-moins-de-1400 :
    BretagneNormandieHauts de FranceOccitaniePACACentre Val de LoireIle de FranceLes foudres d'Auvergne Rhône AlpesRégion Grand EstTeam Nouvelle Aquitaine
    """
    if debug: print("extracting from", src)
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
       print(f"Problem retrieving page '{URL}'.")
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
        clubs.update(T for L in line.split('</a>')
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
    print("Considering", nom,":", url)
    clubs[compet] = get_clubs_from_page(url)
    print("Found:"); display(clubs[compet])
if 0:
  display(clubs_lfr25_u1400 :=
        get_clubs_from_page("https://www.chess.com/fr/announcements/view/calendrier-lfr2025-en-moins-de-1400"
        ))
'''


#print(list(classement_data))
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
          print('Erreur: compèt ne contient ni nom, ni pattern !')
          ask() ; return
    if 'nom' not in compet and (pattern := compet.get('pattern')):
        # pattern could be '' but this doesn't allow to construct a name
        compet['nom'] = pattern2nom(pattern)
        # mais `nom` n'est pas vraiment requis

    # établir la liste des clubs si nécessaire

    if not(clubs := compet.get('clubs')):
        if url := compet.get('url'):
            print(f"""Tentative de rapatriement de la liste des clubs à partir de
la page '{url}'... """)
            if clubs := get_clubs_from_page(url):
               compet['clubs'] = clubs ; print("fini !")
            else:
                print("\nERREUR: N'ai pu déterminer la liste des clubs!")
    # is it now set ?!
    if clubs := compet.get('clubs'):
        display(HTML(
        f"Les {len(clubs)} clubs participant à la compète sont:\n"
        + ", ".join(fmt_club(c) for c in clubs) + "\n\n"))
    else:
        print("ERREUR: liste des clubs inconnue - ne peux procéder.")
        ask() ; return

    print("Rapatriement des rencontres pour ces clubs...")

    cmd = make_club_matches_data(clubs, compet['pattern'])
    if matches := get_unique_matches(cmd) :
       if ask(f"{len(matches)} rencontres trouvées. Afficher la liste ?"):
          display(HTML("Liste des rencontres trouvées:"
          + "\n".join(fmt_match(m)for m in matches) + "\n" ))
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
                        p=matches.pop(m); print(f"Correction: removed {p['name']}:", m)
                elif action=='add':
                    for match_id, name in tasks.items():
                        if matches_pattern(name, compet['pattern']): # and match_id.split('/')[-1] not in matches :
                            print(end = f"Correction: adding match {match_id}... ")
                            if match_data := get_match_data(match_id):
                               matches[match_id] = match_data
                               print(f"done: added {name}")
                            else:
                                 print(f"ERROR: Couldn't add {name}.")
     

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
            print(f"Pas de rencontres connues pour la compet '{compet.get('nom','?')}' !")
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
    debug = lambda a0: a0 in show or show.add(a0) or print(debug_string)
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
            print("Pas de résultat connu pour la compet !") ; return

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
                club_headers[c]: f"{s[ : 3 if s[2] else 2 ]}" for c,s in scores.items() }
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
            "</th><th style='min-width: 2em;'>".join(columns) + "</th></tr>\n"]

        # Number rows and add them to the table
        for i, club_id in enumerate(classement, 1):
            table[club_id]['#'] = i
            html_output.append(f"<tr>" + "</td>\n".join(
                td_element.get(color[club_id].get(c), "<td align=center>") +
                str(table[club_id].get(c,'-')) for c in columns) + "</td></tr>")
        html_output.append("</table>")
        display(HTML("\n".join(html_output)))
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
            print("""
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
        display(HTML(f"""*** Tableau(x) de classement ***
    Choisissez d'abord l'une des compétitions ci-après:
{liste}
        [Entrée] pour retour au menu principal.]"""))
        time.sleep(1)
        print("Entrez votre choix (numéro de la compétition ou [Entrée]):")
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
