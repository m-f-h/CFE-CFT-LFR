"""
CFE_data.py
The module holding all global data for CFE/CFT/LFR chess competitions.
(c) Oct. 2025 by MFH
"""
import __main__

for name in ( 'clubs_info_dict',    # dict { club_url: club_info_dict }
                    # this is a dict of all clubs, with their 'name', 'admins', etc.
              'joueurs',            # dict { user: player_data }
                    # this is a dict of all players, with their 'finished',
                    # 'ongoing' and 'registered' matches (each of which is a list)  
              'club_matches_data',  # dict { club_url: [ match_data, ... ] }
                    # this is a dict of club's matches (list), indexed by club
              'matches',            # dict { match_id: match_data }
                    # this is a "flat" dict of all matches, for easy access
              'rencontres',         # dict { pattern: [ match_id, ... ] }
                    # dict of matches lists, indexed by pattern
              ):
    if name not in globals():
        if hasattr(__main__, name):
            globals()[name] = __main__.__dict__[name]
        else:
            print(f"`{name}` undefined in `CFE_data` and `__main__` - creating empty dict.")
            __main__.__dict__[name] = globals()[name] = {}


#@title clubs_info_dict : copie locale (désactivée au profit de rapatriement du web)

if 0:
  clubs_info_dict = {'team-ajaccio': {'name': 'Ajaccio',
  'admins': ['@Corsicachess2a', '@Deiffsalas2', '@Kaeros69']},
 'les-foudres-de-auvergne-rhone-alpes': {'name': 'Auvergne Rhône Alpes', 'région': True, 'admins': ['@mauvais_perdant', '@Floalexis', '@Fredd_42', '@Panpan1001']},
 'team-french-antilles': {'name': 'Antilles françaises', 'admins': ['@anderstood', '@MF972']},
 'team-bastia-squadra-corsa': {'name': 'Bastia', 'admins': ['@Kaeros69']},
 'bordeaux': {'name': 'Bordeaux', 'admins': ['@rookover', '@Cheztreize']},
 'cercle-boulonnais-des-echecs': {'name': 'Boulogne', 'admins': ['@rclboris', '@bryanflr']},
 'team-bourgogne-franche-comte': {'name': 'Bourgogne Franche Comté', 'région': True, 'admins': ['@JSR_dijon', '@benpig21']},
 'bretagne-echecs': {'name': 'Bretagne', 'région': True, 'admins': ['@Kookaburrra', '@euf']},
 'k6-echecs': {'name': 'Cassis', 'admins': ['@mario_kart_tahitien', '@jackoulecrocquant']},
 'team-centre-val-de-loire-1': {'name': 'Centre Val de Loire', 'région': True, 'admins': ['@HungryAirplane', '@captainfrance41', '@davy37330', '@irisblue45']},
 'chambery-savoie-echecs': {'name': 'Chambéry Savoie échecs', 'admins': ['@capitaine873718']},
 'team-cholet': {'name': 'Cholet', 'admins': ['@The-Conan', '@Alphega49099']},
 'le-plateau-de-gergovie': {'name': 'Clermont-Ferrand:', 'admins': ['@mauvais_perdant', '@LESMAUG']},
 'cojeli': {'name': 'Cojeli', 'admins': ['@malpblu', '@Olive95300', '@sandydeswarte']},
 'isula-corsica': {'name': 'Corse', 'région': True, 'admins': ['@Jean-Luk', '@Puzzle_Blogueur25']},
 'lechiquier-dieppois': {'name': 'Dieppe', 'admins': ['@Musckin', '@luckynike']},
 'team-dijon': {'name': 'Dijon', 'admins': ['@benpig21', '@jsr_dijon', '@Ml_tss']},
 'region-grand-est': {'name': 'Grand Est', 'région': True, 'admins': ['@gueguette8', '@Juldu68', '@IamRasta', '@Masterjules12']},
 'grenoble-echecs-metropole': {'name': 'Grenoble', 'région': True, 'admins': ['@mauvais_perdant', '@Floalexis']},
 'team-guadeloupe': {'name': 'Guadeloupe', 'région': True, 'admins': ['@Keithsmith971', '@anderstood']},
 'team-guyane-francaise': {'name': 'Guyane Française', 'région': True, 'admins': ['@anderstood', '@Jean973', '@GrandmasterHush']},
 'la-tour-infernale': {'name': 'Isbergues', 'admins': ['@jl1202', '@biloute3323']},
 'cavaliers-de-kourou': {'name': 'Kourou', 'admins': ['@CDK_Titouan', '@Pikaplop']},
 'team-hauts-de-france': {'name': 'Hauts de France', 'région': True, 'admins': ['@rclboris', '@nidnag']},
 'ile-de-france-club': {'name': 'Ile de France', 'région': True, 'admins': ['@pacou93', '@Puzzle_Blogueur25', '@elenacormier']},
 'team-lille-metropole': {'name': 'Lille', 'admins': ['@jonjon59', '@L0ul0u_11kub', '@nidnag', '@claire59000']},
 'lyon-echecs': {'name': 'Lyon', 'admins': ['@felinferoce', '@ludovic69']},
 'team-marseille-massilia': {'name': 'Marseille', 'région': True, 'admins': ['@idbsystem', '@13Sheriff']},
 'martinique': {'name': 'Martinique', 'région': True, 'admins': ['@anderstood', '@mf972']},
 'region-mayotte': {'name': 'Mayotte:', 'région': True, 'admins': ['@Acram976', '@OlevLeBihannic']},
 'team-montpellier': {'name': 'Montpellier', 'admins': ['@RomainL34', '@Sakyo34', '@dudubito']},
 'metz-the-chess-tt-team': {'name': 'Metz', 'admins': ['@blastingchess', '@SamVimaire']},
 'la-dame-noire': {'name': 'Montigny le Bretonneux (la dame noire):', 'admins': ['@foveau', '@HonkakuboMiiDera', '@michelrodon']},
 'team-nantes-1': {'name': 'Nantes:', 'admins': ['@pierreloupb', '@The-Conan', '@leflaneurbreton']},
 'team-nice-1': {'name': 'Nice', 'admins': ['@Alexisdu06', '@oliv_from_nice', '@Igins06']},
 'echiquier-de-normandie': {'name': 'Normandie', 'région': True, 'admins': ['@mauvais_perdant', '@Gambit_infernal']},
 'team-nouvelle-aquitaine': {'name': 'Nouvelle aquitaine', 'région': True, 'admins': ['@rookover', '@maximaths']},
 'team-nouvelle-caledonie': {'name': 'Nouvelle calédonie:', 'admins': ['@Momojojojo', '@GeniusTrump147', '@GRROOOAAAAARRRRRHHHHH']},
 'chess-occitanie': {'name': 'Occitanie', 'région': True, 'admins': ['@deep-blou', '@captainmorue', '@samvimaire']},
 'team-orleans': {'name': 'Orléans', 'admins': ['@Irisblue45']},
 'paris-neuf-trois': {'name': 'Paris neuf-trois', 'admins': ['@pacou93', '@elenacormier']},
 'la-reine-danjou': {'name': "Pays de Loire (reine d'Anjou)", 'région': True, 'admins': ['@finlande1214', '@The-Conan', '@leflaneurbreton']},
 'team-provence': {'name': "Provence Alpes Côte d'Azur", 'région': True, 'admins': ['@bardada', '@Philfidefer']},
 'reims-echec-et-mat': {'name': 'Reims',  'admins': ['@masterjules12']},
 'rennes': {'name': 'Rennes',  'admins': ['@Kookaburrra', '@euf']},
 'team-reunion': {'name': 'La Réunion', 'région': True, 'admins': ['@pedr0974', '@Mnemosis']},
 'les-cavaliers-de-brume': {'name': 'Saint Pierre et Miquelon', 'admins': ['@jl7722184']},
 'team-strasbourg': {'name': 'Strasbourg', 'admins': ['@Juldu68', '@Capatof51', '@IamRasta']},
 'federation-tahitienne-des-echecs': {'name': 'Fédération Tahitienne des échecs', 'admins': ['@thibaudgs', '@Bloodlycosa', '@Cheztreize']},
 'team-toulouse-equipa-tolosa': {'name': 'Toulouse', 'admins': ['@deep-blou', '@captainmorue']},
 }

