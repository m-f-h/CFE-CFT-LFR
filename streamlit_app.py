import streamlit as st
st.title("🎈 Gestion LFR/CFE/CFT 🎈")
display = st.write

#from IPython.display import HTML
def HTML(*args): return *args

from CFE_CFT_LFR import *

main_greeting = HTML("""
Bienvenue dans le script d'aide à la gestion LFR/CFE/CFT!
(c) oct.2025 by MFH
      Menu principal:""")

def quitter(): "Quitter le programme."; display(HTML("""
Au revoir et à bientôt !""")); return'return'

main_menu={
    #1: choix_compèt, 2:manage_club_list, 3:affiche_joueurs_multiéquipe,
    #       4: affiche_rencontres_joueur, 5: list_players_by_club,
    #       6: affiche_rencontres_joueurs_club,
    #       7: tableau_classement,
    #       8: afficher_liste_timeout_joueur,
    #       9: afficher_liste_timeout_club,
           0: quitter}

#@title menu principal: execution
do_menu(main_menu, main_greeting, # subsequent kw parameters are
        # needed to format the "dynamic" functions descriptions
        pattern = pattern, 
        num_clubs = len(clubs_info_dict))

st.write(
    "Let's start building! For help and inspiration, " \
    "head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

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
