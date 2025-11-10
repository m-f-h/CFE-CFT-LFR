#!/usr/bin/env python3                           -*- coding: utf-8 -*-
"""
streamlit_app.py     
A Streamlit app for managing LFR/CFE/CFT chess competitions.
(c) Oct. 2025 by MFH

Organisation:

"""
##### PART I : imports and global variable initialisations #####

import streamlit as st

print("Hello folks!")
st.write("Let's do this...")
st.title("Bienvenue dans le script d'aide à la gestion LFR/CFE/CFT!")
st.markdown("<center>(c) oct.2025 by MFH</center>", unsafe_allow_html=True)

from CFE_CFT_LFR import * # import all functions from CFE_CFT_LFR.py

print("Now the main menu...")

Menu(greeting = """<h1>Bienvenue dans le script d'aide à la gestion LFR/CFE/CFT!</h1>
<center>(c) oct.2025 by MFH</center>
       Menu principal:""",
       choix = {
       1: choix_compèt, 2:manage_club_list, 
       3: affiche_joueurs_multiéquipe,
       4: affiche_rencontres_joueur, 
       5: list_players_by_club,
       6: affiche_rencontres_joueurs_club,
       7: tableau_classement,
       8: afficher_liste_timeout_joueur,
       9: afficher_liste_timeout_club,
       0: quitter},
       # subsequent kw parameters are
       # needed to format the "dynamic" functions descriptions
       pattern = '"CFT.*26"', #.*u1400", 
       num_clubs = 'len(clubs_info_dict)'
).run()

"""
st.write(
    "Let's start building! For help and inspiration, " \
    "head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
"""