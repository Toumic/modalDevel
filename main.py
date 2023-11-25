#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Auteur : Cabviva septembre 2023

# Ce programme consiste à recueillir des identités modales,
# sous une forme numérique de la tonalité avec zéro pour un intervalle.


# # Vérification fichier des 462 modes de tétracordes couplés
"""
Dictionnaire "dic_codage" = Liste globale des modèles modaux.
Dictionnaire "pre_classic" = Clefs toniques fondamentales en version classique (sommaire).
    Sommaire = Les notes altérées par un signe forment la base hiérarchique,,,
Dictionnaire pre_physic = Clefs toniques primitives en version physique (poids).
    Physique = Les notes altérées forment des pesants gravitationnels,,,"""

"# Permettre la lecture des noms de gammes à l'envers (précaution) : variable = 'str', variable[::-1] = 'rts'."
pre_classic = {
    "102034050607": ["0", 336], "120034050607": ["-2", 210], "100234050607": ["+2", 392],
    "102304050607": ["-3", 301], "102034500607": ["-5", 341], "102034056007": ["-6", 330],
    "102034050067": ["+6", 339], "120304050607": ["-23", 175], "120034500607": ["-25", 215],
    "120034005607": ["-25+", 201], "120034056007": ["-26", 204], "120034050067": ["-26+", 213],
    "100234500607": ["+25-", 397], "100234056007": ["+26-", 386], "100234050067": ["+26", 395],
    "102340050607": ["-4", 272], "102304500607": ["-35", 306], "102304005607": ["-35+", 292],
    "102304056007": ["-36", 295], "102304050067": ["-36+", 304], "102034506007": ["-56", 338],
    "102034500067": ["-36+", 342], "102034005067": ["+56", 333], "120340050607": ["-24", 146],
    "102030045067": ["x46+", 356], "102030400567": ["+45x", 343], "100234000567": ["+25x", 379],
    "123004500607": ["o35-", 110], "102003400567": ["+35x", 358], "120034560007": ["-26o", 206],
    "102340005607": ["-45+", 258], "102340050067": ["-46+", 278], "102300045607": ["-34x", 320],
    "102003045607": ["+34", 370], "102340500607": ["-45", 281], "102034000567": ["x5", 323],
    "102030040567": ["x45+", 353], "102340560007": ["-46o", 265], "100200345607": ["+23x", 431],
    "120345000607": ["-25o", 160], "102000345067": ["x36+", 376], "123040050607": ["-34", 76],
    "102000345607": ["x3", 375], "123045000607": ["o63-", 90], "123004050607": ["o3", 105],
    "102345060007": ["o65-", 277], "123405000607": ["o54-", 50], "102030004567": ["^4", 357],
    "102003004567": ["+34x", 372], "123400050607": ["o4", 27], "123400500607": ["o45-", 41],
    "123400056007": ["o46-", 12], "102345000607": ["o5", 286], "123004050067": ["o36+", 108],
    "123004005607": ["o35+", 96], "102345600007": ["*6", 267], "123400050067": ["o46+", 37],
    "123450000607": ["*5", 55], "123004000567": ["o35x", 92], "123000045607": ["o34x", 124],
    "102340000567": ["-45x", 253], "102034560007": ["o6", 332], "100023456007": ["x26-", 440],
    "100002345607": ["^2", 458], "102000034567": ["^3", 378], "123400000567": ["o45x", 1]}
pre_physic = {
    "102034050607": ["0", 336], "120034050607": ["-2", 210], "100234050607": ["+2", 392],
    "102304050607": ["-3", 301], "102034500607": ["-5", 341], "102034056007": ["-6", 330],
    "102034050067": ["+6", 339], "120304050607": ["-23", 175], "120034500607": ["-25", 215],
    "120034005607": ["-25+", 201], "100234005607": ["+25", 383], "120034050067": ["-26+", 213],
    "100234500607": ["+25-", 397], "100234056007": ["+26-", 386], "100234050067": ["+26", 395],
    "102340050607": ["-4", 272], "102304500607": ["-35", 306], "102304005607": ["-35+", 292],
    "102034005607": ["+5", 327], "102304050067": ["-36+", 304], "102034506007": ["-56", 338],
    "102034500067": ["-36+", 342], "100203450607": ["+23", 422], "120340050607": ["-24", 146],
    "102030045067": ["x46+", 356], "102030400567": ["+45x", 343], "100023450067": ["x26+", 444],
    "123004500607": ["o35-", 110], "102003400567": ["+35x", 358], "100023400567": ["x25", 435],
    "102340005607": ["-45+", 258], "102340050067": ["-46+", 278], "102300045607": ["-34x", 320],
    "102003045607": ["+34", 370], "102340500607": ["-45", 281], "100023450607": ["x2", 443],
    "102030040567": ["x45+", 353], "100023045607": ["x24+", 447], "100200345607": ["+23x", 431],
    "120345000607": ["-25o", 160], "102000345067": ["x36+", 376], "123040050607": ["-34", 76],
    "102304000567": ["x53-", 288], "100020345607": ["x23+", 452], "123004050607": ["o3", 105],
    "102345060007": ["o65-", 277], "102000304567": ["x34+", 377], "102030004567": ["^4", 357],
    "102003004567": ["+34x", 372], "123400050607": ["o4", 27], "123400500607": ["o45-", 41],
    "100234560007": ["+26o", 388], "102345000607": ["o5", 286], "123004050067": ["o36+", 108],
    "102345006007": ["o56-", 283], "100002304567": ["^24+", 460], "100020034567": ["x23", 455],
    "100002034567": ["^23+", 461], "120030004567": ["^42-", 231], "102345000067": ["+65o", 287],
    "102340000567": ["-45x", 253], "102034560007": ["o6", 332], "100023456007": ["x26-", 440],
    "102300004567": ["^43-", 322], "102000034567": ["^3", 378], "100000234567": ["+^2", 462]}
cle_classic, cle_physic = list(pre_classic.keys()), list(pre_physic.keys())
dic_codage = {}
pre_codage = open('globdicTcoup.txt', 'r')
cod = 0
for pre_cod in pre_codage:
    cod += 1
    dic_codage[cod] = pre_cod[:12]
    '''abc = "100234005607"
    if dic_codage[cod] == abc:
        print("cod:", cod,)'''
# print('pre_codage/cod :', cod, ' Nombre de codages modaux.', dic_codage)
pre_codage.close()
maj_form = dic_codage[336]
gam_form = list(maj_form)  # Construction de la liste numéraire majeure
gam_util = []
tab_key = []
classic_physic = {}


def print_hi():
    """Outil de saisie pour les formes modales numériques"""
    # , tab_sup = Liste les signes (#) cumulés de zéro à 24 dièses. tab_sup[2] = 'x'.
    tab_sup = ['', '+', 'x', '^', '+^', 'x^', '^^', '+^^', 'x^^', '^^^', '+^^^', 'x^^^', '^^^^', '+^^^^', 'x^^^^',
               '^^^^^', '+^^^^^', 'x^^^^^', '^^^^^^', '+^^^^^^', 'x^^^^^^', '^^^^^^^', '+^^^^^^^', 'x^^^^^^^',
               '^^^^^^^^']
    # , tab_inf = Liste les signes (b) cumulés de zéro à 24 bémols. Cette liste va être inversée.
    tab_inf = ['', '-', 'o', '*', '-*', 'o*', '**', '-**', 'o**', '***', '-***', 'o***', '****', '-****', 'o****',
               '*****', '-*****', 'o*****', '******', '-******', 'o******', '*******', '-*******', 'o*******',
               '********']
    # , dic_maj = Liste les gammes majeures de DO à SI
    dic_maj = {'C': ['C', '', 'D', '', 'E', 'F', '', 'G', '', 'A', '', 'B'],
               'D': ['D', '', 'E', '', '+F', 'G', '', 'A', '', 'B', '', '+C'],
               'E': ['E', '', '+F', '', '+G', 'A', '', 'B', '', '+C', '', '+D'],
               'F': ['F', '', 'G', '', 'A', '-B', '', 'C', '', 'D', '', 'E'],
               'G': ['G', '', 'A', '', 'B', 'C', '', 'D', '', 'E', '', '+F'],
               'A': ['A', '', 'B', '', '+C', 'D', '', 'E', '', '+F', '', '+G'],
               'B': ['B', '', '+C', '', '+D', 'E', '', '+F', '', '+G', '', '+A']}
    # , dic_deg = Liste les espaces des signatures par degré
    dic_deg = {"2": ["-2", "2", "+2", "x2", "^2", "+^2"],
               "3": ["o3", "-3", "3", "+3", "x3", "^3"],
               "4": ["o4", "-4", "4", "+4", "x4", "^4"],
               "5": ["*5", "o5", "-5", "5", "+5", "x5"],
               "6": ["-*6", "*6", "o6", "-6", "6", "+6"],
               "7": ["o*7", "-*7", "*7", "o7", "-7", "7"]}
    # , dic_120 = Les listes dic_deg en zone chromatique
    dic_120 = {0: ["1"],
               1: ["-2"],
               2: ["2", "o3"],
               3: ["+2", "-3", "o4"],
               4: ["x2", "3", "-4", "*5"],
               5: ["^2", "+3", "4", "o5", "-*6"],
               6: ["+^2", "x3", "+4", "-5", "*6", "o*7"],
               7: ["^3", "x4", "5", "o6", "-*7"],
               8: ["^4", "+5", "-6", "*7"],
               9: ["x5", "6", "o7"],
               10: ["+6", "-7"],
               11: ["7"]}

    tab_inf.reverse()  # tab_inf = Liste les signes (b) cumulés de zéro à 24 bémols. tab_inf[-2] = 'o'
    tab_inf.remove(tab_inf[-1])
    gam_maj = ['1', '0', '2', '0', '3', '4', '0', '5', '0', '6', '0', '7']
    deg_rom = ["I", "II", "III", "IV", "V", "VI", "VII"]
    dic_gam, mod_bin, mod_mod = {}, [], {}
    lis_gam1, lis_gam2 = "1234567", "12345678"  # Afin de comparer l’ordre des chiffres de l’utilisateur.
    zer_zer, gam_gam = False, False
    (lineno(), "tab_inf:", tab_inf)
    message_erreur = ""
    not_dico = {}  # Dictionnaire contenant le(s) choix utilisateur.
    mod_use = ""
    #
    print(lineno(), "##### INPUT NOTE_TONIQUE #########################################################")
    "# Choisir la tonique par construction ou par déduction"
    note_dia = input("<return> par défaut = 'c'.\n"
                     "Choisissez la tonique [C, D, E, F, G, A, B] : ")
    if note_dia == '':
        note_dia = 'c'
    if not note_dia.isupper():  # Mettre en majuscule.
        note_dia = note_dia.upper()  # ("La note est transformée en majuscule", "note_dia")
    #
    print(lineno(), "\n##### INPUT ALTÉRATION_NOTE ####################################################")
    "# L'utilisateur altère la tonique"
    ord_sup, ord_inf, ind_sig = "+x^", "-o*", ""
    note_sig = input("<return> par défaut = non-altéré.\n"
                     "Choisissez l'altération [+, x, ^, -, o, *] : ")
    if note_sig != "":
        "# Quand not_alto contient plusieurs altérations"
        if len(note_sig) > 1:  # Reconnaissance des altérations déclarées.
            nbr_un = 0
            for un in note_sig:
                if un in ord_sup:  # ord_sup = "+x^"
                    nbr_un += tab_sup.index(un)
                else:  # ord_inf = "-o*"
                    nbr_un += tab_inf.index(un) - 24
            if nbr_un > -1:
                ind_sig = tab_sup[nbr_un]
            elif nbr_un < 0:
                ind_sig = tab_inf[nbr_un]
            if not ind_sig:
                ind_sig = "0"
            (lineno(), "INF nbr_un:", nbr_un, "ind_sig:", ind_sig)
        else:
            ind_sig = note_sig
            (lineno(), "note_sig:", note_sig, "ind_sig:", ind_sig)
    else:
        ind_sig = "0"
    note_sig = ind_sig
    #
    print(lineno(), "\n##### INPUT TYPE_RECHERCHE #####################################################")
    "# Choix d'une définition stricte ou déductive"
    tip_rich = input("<return> par défaut = '1'.\n"
                     "0 = Recherche formule. 1 = Recherche stricte. 2 = Recherche déductive : ")
    if tip_rich == "":
        tip_rich = "1"
    '''Tonique constructive : Crée une formule numéraire stricte.
    En suivant les choix de l'utilisateur du dictionnaire not_dico'''
    #   ###############################################################################################
    #
    tip_form, k1_dic = ["1", "", "", "", "", "", "", "", "", "", "", ""], None

    if tip_rich in ("1", "2"):  # dic_codage[336] = Gamme majeure.
        while 1:
            "# Choisir le type de tonalité (pouvant être une mélodique diminuée (o3))"
            '''# Plage des signes portés sur les degrés :  # Dictionnaire {dic_deg}
            deg2[-2, +^2], deg3[o3, ^3], deg4[o4, ^4], deg5[*5, x5], deg6[-*6, +6], deg7[o*7, 7]'''
            tab_type = ["", "majeure", "tonale", "mélodique", "médiane", "dominante", "harmonique", "sensible"]
            if message_erreur:
                print("\n##### ERREUR EN COURS ########################################################")
                print(lineno(), message_erreur, "Changez votre choix !", not_dico)
            #
            print(lineno(), "\n##### INPUT GAMME_RECHERCHÉE ###########################################")
            "# L'utilisateur choisit les notes et les altérations"
            not_type = input("############################ FAITES VOTRE CHOIX #########################\n"
                             "<return> par défaut = majeure.\n"
                             "[1= majeure, 2=tonale, 3=mélodique, 4=médiane, 5=dominante, 6=harmonique, 7=sensible] \n"
                             "les signes : [+, x, ^, -, o, *]. 'b=-', '#=+', '++'=2, '^-'=2, '*x'=-1, '++*'=-2\n"
                             "Attention les chevauchements sont transformés.\n"
                             "Comment écrire vos notes (signe + degré, signe + degré, signe + degré,,,)\n"
                             "Pour '1' = majeur : La tonique n'est pas traitée mais son altération est valide\n"
                             "Vérifiez votre sélection pour éviter les erreurs (Les notes se suivent dans l'ordre)\n"
                             "Choisir un type ou plusieurs types de gamme : ")
            #   #######################################################################################
            #
            print(lineno())
            "# Traitement des demandes des tonalités signées"
            "# Signer le niveau majeur, c'est comme signer la note tonique (note_sig/ind_sig)"
            ok_saisie = True
            tip_form = ["1", "", "", "", "", "", "", "", "", "", "", ""]
            not_alto, not_copa, deg_duo = "", not_type, []
            not_dico.clear()  # not_dico = {'1': ['o', 'o1'], '5': ['*', '*5']}
            copa = list(not_copa)
            (lineno(), "copa:", copa)
            if len(not_copa) > 1:
                for nt in not_copa:
                    (lineno(), "NT:", nt, "not_dico:", not_dico)
                    if nt.isdigit():
                        '''nt = not_type = Tonalité des degrés.
                        Quand nt = 1. La gamme reste majeure, sa tonalité est affectée par le signe d'altération.'''
                        #
                        "# Quand not_alto contient plusieurs altérations"
                        if len(not_alto) > 1:  # Reconnaissance des altérations déclarées.
                            nbr_un = 0
                            for un in not_alto:
                                if un in ord_sup:  # ord_sup = "+x^"
                                    nbr_un += tab_sup.index(un)
                                else:  # ord_inf = "-o*"
                                    nbr_un += tab_inf.index(un) - 24
                            if nbr_un > -1:
                                not_alto = tab_sup[nbr_un]
                            else:
                                not_alto = tab_inf[nbr_un]
                            (lineno(), "INF nbr_un:", nbr_un, "not_alto:", not_alto)
                        #
                        if nt in deg_duo:
                            continue
                        deg_duo.append(nt)
                        not_type = nt
                        not_glob = not_alto + nt
                        # Vérification de la disponibilité du type choisi (sauf 1, car sans référent).
                        "# Permet de respecter les plages altératives des degrés. Ligne 35 : dic_deg[]"
                        if nt != "1":
                            if not_glob not in dic_deg[str(nt)]:
                                if not_alto in tab_sup:
                                    not_glob = dic_deg[str(nt)][-1]
                                    not_alto = not_glob[:len(not_glob) - 1]
                                elif not_alto in tab_inf:
                                    not_glob = dic_deg[str(nt)][0]
                                    not_alto = not_glob[:len(not_glob) - 1]
                                (lineno(), "not_glob:", not_glob, "dic_deg:", dic_deg[str(nt)])
                        not_dico[not_type] = [not_alto]
                        not_dico[not_type].append(not_glob)
                        (lineno(), "not_dico:", not_dico, "not_alto:", not_alto)
                        not_alto = ""
                        (lineno(), "not_type:", not_type, "not_glob:", not_glob, "NT:", nt)
                    else:
                        not_alto += nt
                        (lineno(), "*** *** nt signe:", nt, "not_alto:", not_alto, "nt:", nt)
            # ############################# CONTRÔLE SAISIE ###############################################
            "# Contrôle de l'entrée utilisateur"
            k1_dic = list(not_dico.keys())
            k1_dic.sort()  # k1_dic = Liste des clés des degrés choisis par l’utilisateur.
            gam_nat = []  # Recueil les degrés inchangés et hors "tip_form"
            mod_use = ''
            print(lineno(), "not_dico:", not_dico)
            for k1 in k1_dic:  # Liste les clés de not_dico.keys()
                k0 = int(k1)  # k0 = Copie le degré original.
                if not_dico[k1][0] in tab_sup:  # Le signe d’altération est parmi les signes augmentés.
                    (lineno(), "tab_sup = ['', '+', 'x', '^', '+^', 'x^', '^^', '+^^', 'x^^',,, ")
                    ind_k2 = tab_sup.index(not_dico[k1][0])  # Son emplacement parmi les signes.
                    gam_k20 = gam_maj.index(str(k0))  # Son emplacement dans la gamme avant d’avoir été altéré.
                    gam_k21 = gam_k20 + ind_k2  # Son emplacement dans la gamme après avoir été altéré.
                    (lineno(), "^^^^^^^^ K0:", k0, "ind_k2:", ind_k2, "gam_k20:", gam_k20, "gam_k21:", gam_k21)
                    if tip_form[gam_k21] == "":
                        if str(k0) in tip_form:
                            lis_f = [i for i in tip_form if i not in ("", "1")]  # La tonique est omise ici
                            if str(k0) != "1" and not_dico[k1][1] in dic_120[gam_k21]:
                                tip_form[gam_k21] = str(int(max(lis_f)) + 1)
                                (lineno(), "tip_form:", tip_form)
                                (lineno(), "dic_120:", dic_120[gam_k21], "not_dico[k1][0]:", not_dico[k1][1])
                            (lineno(), "\t*Présent_tip_form:", tip_form, "*str(k0):", str(k0), "lis_f:", lis_f)
                        else:
                            tip_form[gam_k21] = str(k0)
                            (lineno(), "tip_form:", tip_form, "str(k0):", str(k0))
                    elif str(k0) != "1":
                        ok_saisie = False
                        message_erreur = "DEUX NOTES ARRIVENT AU MÊME EMPLACEMENT (tab_sup): "
                        print(lineno(), message_erreur, tip_form[gam_k21], "et : ", not_dico[k1][1])
                        print(lineno(), "Case occupée K0 : ", k0, tip_form)
                        print(lineno(), "Erreur \n")

                    # Bouclage jusqu’à ce que "k0" n’atteigne plus les notes naturelles…
                    if str(k0) != "1":
                        k0 += 1  # Pour inspecter les degrés supérieurs.
                        while k0 < 8:  # str(k0) not in k1_dic and
                            gam_k22 = gam_maj.index(str(k0))  # Index degré k0+=1 majeur
                            gam_k21 += 1  # Incrémentation de l'index par demi-ton
                            (lineno(), "________\tK0:", k0, "gam_k22(maj):", gam_k22, "gam_k21:", gam_k21)
                            if gam_k22 > gam_k21 or tip_form[gam_k21] != "" or str(k0) in k1_dic:
                                (lineno(), "*BREAK_sup*\t K0:", k0, "tip_form[gam_k21]:", tip_form[gam_k21])
                                break
                            elif gam_k22 <= gam_k21:
                                tip_form[gam_k21] = str(k0)
                                (lineno(), "tip_form:", tip_form, "str(k0):", str(k0), "k1_dic:", k1_dic)
                            k0 += 1
                            (lineno(), "Addition tip_form:", tip_form)
                elif not_dico[k1][0] in tab_inf:  # Le signe d’altération est parmi les signes diminués.
                    (lineno(), "tab_inf = ['', '-', 'o', '*', '-*', 'o*', '**', '-**', 'o**', '***',,, ")
                    ind_k2 = tab_inf.index(not_dico[k1][0]) - 24  # Son emplacement parmi les signes.
                    gam_k20 = gam_maj.index(str(k0))  # Son emplacement dans la gamme avant avoir été altéré.
                    gam_k21 = gam_maj.index(str(k0)) + ind_k2  # Son emplacement dans la gamme après avoir été altéré.
                    (lineno(), "K0:", k0, "gam_k20:", gam_k20, "gam_k21:", gam_k21, "tip_form:", tip_form)
                    if tip_form[gam_k21] == "":
                        if str(k0) in tip_form:
                            lis_f = [i for i in tip_form if i not in ("", "1")]
                            if str(k0) != "1" and not_dico[k1][1] in dic_120[gam_k21]:
                                tip_form[gam_k21] = str(int(min(lis_f)) - 1)
                                (lineno(), "tip_form:", tip_form)
                                (lineno(), "dic_120:", dic_120[gam_k21], "not_dico[k1][0]:", not_dico[k1][1])
                            (lineno(), "\t*Présent_tip_form:", tip_form, "*str(k0):", str(k0), "lis_f:", lis_f)
                        else:
                            tip_form[gam_k21] = str(k0)
                            (lineno(), "tip_form:", tip_form, "str(k0):", str(k0))
                    elif str(k0) != "1":
                        ok_saisie = False
                        message_erreur = "DEUX NOTES ARRIVENT AU MÊME EMPLACEMENT  (tab_inf): "
                        print(lineno(), message_erreur, tip_form[gam_k21], "et : ", not_dico[k1][1])
                        print(lineno(), "Case occupée K0:", k0, tip_form)
                        print(lineno(), "Erreur \n")
                    # Le nouveau degré ne se trouve pas dans le choix de l'utilisateur.
                    "# k0 n'est pas dans le dictionnaire saisi par l'utilisateur."
                    if str(k0) != "1":
                        k0 -= 1  # Pour inspecter les degrés inférieurs.
                        while k0 > 1:  # str(k0) not in k1_dic and
                            gam_k22 = gam_maj.index(str(k0))  # Index degré k0-=1
                            gam_k21 -= 1
                            # print(lineno(), "str(k0):", str(k0), "\tgam_k22:", gam_k22, "gam_k21:", gam_k21)
                            if gam_k22 < gam_k21 or tip_form[gam_k21] != "" or str(k0) in k1_dic:
                                (lineno(), "*BREAK_inf*\t K0:", k0, "tip_form[gam_k21]:", tip_form[gam_k21])
                                break
                            if gam_k22 >= gam_k21:
                                tip_form[gam_k21] = str(k0)
                                (lineno(), "tip_form:", tip_form, "str(k0):", str(k0), "22.21:", gam_k22, gam_k21)
                            k0 -= 1
                            (lineno(), "\tK0:", k0, "20:", gam_k20, "21:", gam_k21, "22:", gam_k22)
                        (lineno(), "Soustraction tip_form:", tip_form)
                else:
                    ok_saisie = False
                    (lineno(), "L'altération est inconnue : ", not_dico[k1][0],)
                (lineno(), "K1:", k1, "not_dico[k1]:", not_dico[k1])
            for i in range(1, 8):
                if i not in gam_nat and str(i) not in tip_form:
                    gam_nat.append(i)
            gam_nat.sort()
            (lineno(), "F tip_form:", tip_form, "gam_nat:", gam_nat)

            if ok_saisie:  # Le format de la saisie est accepté.
                mem_nom, gam_nom = "", "| "
                for qi in not_dico.keys():
                    mem_nom += not_dico[qi][1]
                    gam_nom += tab_type[int(qi)] + " | "
                print(lineno(), "mem_nom:", mem_nom, "gam_nom:", gam_nom, "SAISIE OK ----")
                for ind in range(len(tip_form)):
                    ind1 = tip_form[ind]  # Données construites
                    ind2 = gam_maj[ind]  # Données majeures
                    if ind1 != '':
                        mod_use += ind1
                    elif int(ind2) in gam_nat:
                        mod_use += ind2
                    else:
                        mod_use += "0"
                        (lineno(), "ind2:ok", ind2)
                    (lineno(), "ind1:", ind1, "           \t\t\tind2:", ind2)
                print(lineno(), "\tmod_use:", mod_use, "gam_nat:", gam_nat)
                break

    def signal(ds):
        """La fonction reçoit l'altération et retourne sa valeur"""
        ind_ds = None  # Déclaration de la variable.
        if isinstance(ds, str):
            if ds == "0":
                ds = ""
            if ds in tab_sup:
                ind_ds = tab_sup.index(ds)
            else:
                ind_ds = tab_inf.index(ds) - 24
        elif isinstance(ds, int):
            if ds > -1:
                ind_ds = tab_sup[ds]
            else:
                ind_ds = tab_inf[ds]
        (lineno(), "note_sig", note_sig, "ind_ds:", ind_ds, "ds:", ds)
        return ind_ds

    if "1" in not_dico.keys() and not_dico["1"][0] != "":  # Un choix est porté sur la tonique altérée
        '''Quand dans le choix, il y a [signé majeur] = le signé majeur remplace la valeur de note_sig'''
        note_sig0, ind_sig0 = note_sig, 0
        note_sig = not_dico["1"][0]
        if note_sig != "":
            if note_sig in tab_sup:
                ind_sig = tab_sup.index(note_sig)
            elif note_sig in tab_inf:
                ind_sig = tab_inf.index(note_sig) - 24
            (lineno(), "note_dia:", note_dia, "\t\tind_sig:", ind_sig)
        else:
            ind_sig = "0"
        if note_sig0 != "":
            ind_sig0 = signal(note_sig0)
            ind_sig += ind_sig0
            (lineno(), "note_sig0:", note_sig0, "ind_sig0:", ind_sig0, "ind_sig:", ind_sig)
        note_sig = ind_sig
    (lineno(), "note_sig:", note_sig, "tip_form:", tip_form)
    (lineno(), "Tonalité signée not_dico:", not_dico)
    #

    '''Tonique déductive : Cherche les formules numéraires similaires dans globdicTcoup.txt {dic_codage}'''
    if tip_rich == "2":
        """Condition utilisant la gamme recherchée dans le fichier[globdicTcoup.txt/dic_codage (dictionnaire)]"""
        (lineno(), "not_dico:", not_dico, "\ntip_form:", tip_form, "k1_dic:", k1_dic)
        ind_dic = {}
        for iu in k1_dic:  # Construction dictionnaire ind_dic[clé=degré, valeur=index]
            kiu = mod_use.index(iu)  # Index du degré dans le mode utilisateur
            ind_dic[iu] = kiu  # Dictionnaire
        long_code, long_key, ko = len(dic_codage), len(ind_dic.keys()), 0
        tab_key.clear()
        for dc in range(1, long_code + 1):
            ec = str(dic_codage[dc])  # Récupération modèle[ec] du fichier.
            for key, val in ind_dic.items():  # Lecture dictionnaire utilisateur
                ik = ec.index(key)  # Index de la clé dans le modèle[ec].
                (lineno(), "ik:", ik, "ec:", ec)
                if ik == val and ec not in tab_key:
                    tab_key.append(ec)
                    (lineno(), "ik:", ik, "key:", key, "ec:", ec, "val:", val)
            (lineno(), "*** ec:", ec)
        (lineno(), len(tab_key), "tab_key:", tab_key, "ind_dic:", ind_dic)
        loc = 0
        while loc < 13:  # Répété plusieurs fois pour un meilleur nettoyage.
            loc += 1
            for tk in tab_key:
                for key, val in ind_dic.items():
                    ik = tk.index(key)
                    (lineno(), "tk:", tk, "key:", key, "ik:", ik, "val:", val)
                    if ik != val or tab_key.count(tk) > 1:
                        tab_key.remove(tk)
                        (lineno(), "   REMOVE tk:", tk, "key:", key, " : ", ik, val)
                        break
        (lineno(), "tab_key", tab_key, "len(tab_key):", len(tab_key))

    (lineno(), "tip_rich:", tip_rich)
    if tip_rich == "0":
        print(lineno(), "tip_rich = '0':", tip_rich)
        while 1:
            '''Norme de saisie :
            Chaque note a son numéro de 1 à 8, et l'ordre croissant doit-être respecté (12345678).
            Chaque intervalle est compté, il doit y en avoir cinq (ni moins, ni plus).
            Exemple de gamme majeure : 102034050607 ou 1020340506078'''
            mod_use = input("Entrez une formule de 1 à 7 ou 8 avec 5 zéros : ")
            zero = list(mod_use).count('0')
            if zero != 5:
                reste = zero - 5
                print(lineno(), "Réparer les zéros :", reste)
            else:
                zer_zer = True
            long = ''.join(xl for xl in mod_use if xl != '0')
            if len(long) == 7:
                if lis_gam1 == str(long):
                    gam_gam = True
            elif len(long) == 8:
                if lis_gam2 == str(long):
                    gam_gam = True
            else:
                print(lineno(), "Réparer les degrés :", mod_use)
            if zer_zer and gam_gam:
                if len(long) == 7:
                    mod_use = mod_use  # Pas de retrait.
                else:
                    mod_use = mod_use[:12]  # Retrait du chiffre 8 pour l'algo.
                (lineno(), "mod_use:", mod_use)
                break

    # Réception 102034050607 et développement diatonique.
    def mode(module):
        """Réception 102034050607"""
        "# 1 Transformation en mode binaire"
        dic_gam[module] = []
        mod_bin.clear()
        for mb in module:
            if mb != '0':
                mod_bin.append('1')
            else:
                mod_bin.append('0')
        (lineno(), "mod_bin:", mod_bin, "\tmodule:", module, len(module))

        "# 2 Transformation en mode unaire"
        mod_jeu, mid_mod, mid_jeu = "", [], []
        for xm in range(7):
            mod_mod[xm] = []
            mid_mod.clear()
            while mod_bin[0] == '0':
                deg_mod = mod_bin.pop(0)
                mod_bin.append(deg_mod)
            else:
                mo = 0
                ind_mj = -1
                for mb in mod_bin:
                    if mb == '0':
                        mid_mod.append('0')
                        mod_mod[xm].append('0')
                        ind_mj += 1
                        (lineno(), "       mo:", mo, "mb:", mb, "mid_mod:", mid_mod)
                    elif mo < 7:
                        mo += 1
                        (lineno(), "mo:", mo, "mb:", mb)
                        ind_mj += 1  # Index cycle chrono
                        ind_mo = gam_maj.index(str(mo))  # Index chiffre unaire.
                        res_ind = ind_mj - ind_mo
                        if res_ind > 0:
                            sig_mo = tab_sup[res_ind]
                            mo0 = sig_mo + str(mo)
                        elif res_ind < 0:
                            sig_mo = tab_inf[res_ind]
                            mo0 = sig_mo + str(mo)
                        else:
                            mo0 = str(mo)
                        mid_mod.append(str(mo))
                        mod_mod[xm].append(mo0)
                        (lineno(), "mo:", mo, "ind_mj:", ind_mj, "ind_mo:", ind_mo, "res_ind:", res_ind)
                    mod_jeu = ''.join(mm for mm in mod_mod[xm])
                    mid_jeu = ''.join(mm for mm in mid_mod)
                    (lineno(), "mid_jeu:", mid_jeu)
                deg_mod = mod_bin.pop(0)
                mod_bin.append(deg_mod)
            jeu_jeu = mod_jeu, mid_jeu
            dic_gam[module].append(jeu_jeu)
            (lineno(), "mod_mod:", mod_mod[xm], "mod_jeu:", mod_jeu, "mid_jeu:", mid_jeu)
        (lineno(), "FOR Fonction mode:", module, type(module), "\n dic_gam:", dic_gam)

    # Définir la gamme analogique qui est en relation avec la saisie utilisateur.
    def gamme():
        """Fonction chargée de transformer une forme numéraire en une forme analogique"""
        (lineno(), "note_dia:", note_dia, "note_sig:", note_sig)
        (lineno(), "gam_maj:", gam_maj)
        for yo in range(12):
            if mod_use[yo] != "0":
                ind_maj = gam_maj.index(mod_use[yo])  # Emplacement majeur du degré
                sig_loc = yo - ind_maj  # Différence avec l'emplacement du degré majeur
                deg_maj = dic_maj[note_dia][ind_maj]
                if len(deg_maj) > 1:  # Le degré majeur est altéré.
                    deg_sig = deg_maj[:len(deg_maj) - 1]  # Récupération de l'altération
                    val_sig = signal(deg_sig)
                    sig_loc += val_sig
                    deg_maj = deg_maj[len(deg_maj) - 1:]
                    (lineno(), "deg_maj:", deg_maj, "deg_sig:", deg_sig, "val_sig:", val_sig, "sig_loc:", sig_loc)
                note_sig2 = signal(note_sig)
                if isinstance(note_sig2, str):
                    note_sig2 = signal(note_sig2)
                sig_loc += int(note_sig2)
                val_sig = signal(sig_loc)
                deg_maj = val_sig + deg_maj
                gam_util.append(deg_maj)
                (yo, lineno(), "gam_maj:", gam_maj[yo], "deg_maj:", deg_maj, "mod_use:", mod_use[yo])
                (yo, lineno(), "dic_maj:", dic_maj[note_dia][yo], "ind_maj:", ind_maj, "sig_loc:", sig_loc)
        fou = 0
        for cle in dic_gam[mod_use]:
            ind_clefs = dic_gam[mod_use].index(cle)
            if ind_clefs == 0:
                deg_gam = 0
            else:
                deg_gam = 7 - ind_clefs
            clef = cle[1]
            classic_physic[clef] = []
            (lineno(), "mod_use:", mod_use, "cle:", cle)
            if cle[1] in cle_classic:
                job = cle_classic.index(cle[1])
                app = list(pre_classic[cle_classic[job]]), "classic", mod_use, deg_rom[deg_gam]
                classic_physic[clef].append(app)
                (lineno(), "cle_classic: ", cle_classic[job], pre_classic[cle_classic[job]], "job:", job, fou)
            if cle[1] in cle_physic:
                job = cle_physic.index(cle[1])
                app = list(pre_physic[cle_physic[job]]), "physic", mod_use, deg_rom[deg_gam]
                classic_physic[clef].append(app)
                (lineno(), "cle_physic:  ", cle_physic[job], pre_physic[cle_physic[job]], "job:", job, fou)
            fou += 1
            if not classic_physic[clef]:
                del classic_physic[clef]
        print("\n", lineno(), "\n gam_util:", gam_util)

    # Fonctionnalités ☺
    if mod_use:  # "mod_use", généralement présent d’entrée.
        dic_gam[mod_use] = []
        mode(mod_use)
        gam_util.clear()
        gamme()
        (lineno(), "* mod_use:", mod_use, "gam_util:", gam_util)
        (lineno(), "mod_mod:", mod_mod)
        (lineno(), "cle_classic:", cle_classic[0], "\ncle_physic:", cle_physic[0])
    if tab_key:  # "tab_key", utilisé pour traiter plusieurs choix de gammes.
        for m_u in tab_key:
            mod_use = m_u
            mode(mod_use)
            gam_util.clear()
            gamme()
            (lineno(), "*** mod_use:", mod_use, "gam_util:", gam_util)
    (lineno(), "tab_key:", tab_key)
    print(lineno(), "\ndic_gam:", dic_gam.keys(), "\n classic_physic:", classic_physic)


if __name__ == '__main__':
    import inspect
    from typing import Callable

    '# lineno() Pour consulter le programme grâce au suivi des prints'
    lineno: Callable[[], int] = lambda: inspect.currentframe().f_back.f_lineno

    print_hi()
