#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Auteur : Cabviva septembre 2023

# Ce programme consiste à recueillir des identités modales.
# Sous une forme numérique de la tonalité avec zéro pour un intervalle.


# # Vérification fichier des 462 modes de tétracordes couplés
dic_codage = {}
pre_codage = open('globdicTcoup.txt', 'r')
cod = 0
for pre_cod in pre_codage:
    cod += 1
    dic_codage[cod] = pre_cod[:12]
# print('pre_codage/cod :', cod, ' Nombre de codages modaux.', dic_codage)
pre_codage.close()
maj_form = dic_codage[336]
gam_form = list(maj_form)  # Construction de la liste numéraire majeure


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
    dic_gam, mod_bin, mod_mod = {}, [], {}
    lis_gam1, lis_gam2 = "1234567", "12345678"  # Afin de comparer l'ordre des chiffres de l'utilisateur.
    zer_zer, gam_gam = False, False
    (lineno(), "tab_inf:", tab_inf)
    message_erreur = ""
    not_dico = {}  # Dictionnaire contenant le(s) choix utilisateur.
    mod_use = ""
    #
    print(lineno(), "\n##### INPUT TONIQUE ############################################################")
    "# Choisir la tonique par construction ou par déduction"
    note_dia = input("Choisissez la tonique [C, D, E, F, G, A, B] : ")
    if note_dia == '':
        note_dia = 'c'
    if not note_dia.isupper():  # Mettre en majuscule.
        note_dia = note_dia.upper()  # ("Note transformée en majuscule", note_dia)
    #
    print(lineno(), "\n##### INPUT ALTÉRATION #########################################################")
    "# L'utilisateur altère la tonique"
    note_sig = input("Choisissez l'altération [+, x, ^, -, o, *] : ")
    if note_sig in tab_inf:
        ind_sig = tab_inf.index(note_sig) - 24
    else:
        ind_sig = tab_sup.index(note_sig)
    #
    print(lineno(), "\n##### INPUT TYPE RECHERCHE #####################################################")
    "# Choix d'une définition stricte ou déductive"
    tip_rich = input("0 = Recherche formule. 1 = Recherche stricte. 2 = Recherche déductive : ")
    if tip_rich == "":
        tip_rich = "1"
    '''Tonique constructive : Crée une formule numéraire stricte.
    En suivant les choix de l'utilisateur du dictionnaire not_dico'''
    #   ###############################################################################################
    #
    tip_form = ["1", "", "", "", "", "", "", "", "", "", "", ""]
    if tip_rich in ("1", "2"):  # dic_codage[336] = Gamme majeure.
        while 1:
            "# Choisir le type de tonalité (pouvant être une mélodique diminuée (o3))"
            '''# Plage des signes portés sur les degrés :  # Dictionnaire {dic_deg}
            deg2[-2, +^2], deg3[o3, ^3], deg4[o4, ^4], deg5[*5, x5], deg6[-*6, +6], deg7[o*7, 7]'''
            tab_type = ["", "majeure", "tonale", "mélodique", "médiane", "dominante", "harmonique", "sensible"]
            if message_erreur:
                print("################################################################################")
                print(lineno(), message_erreur, "Changez votre choix !", not_dico)
            #
            print(lineno(), "\n##### INPUT TYPE RECHERCHE #############################################")
            "# L'utilisateur choisit les notes et les altérations"
            not_type = input("############################ FAITES VOTRE CHOIX #########################\n"
                             "[1= majeure, 2=tonale, 3=mélodique, 4=médiane, 5=dominante, 6=harmonique, 7=sensible] \n"
                             "les signes : [+, x, ^, -, o, *]. Une mélo (-3). Une mélo + diminuée harmone (-3o6)\n"
                             "Attention les chevauchements sont transformés.\n"
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
            if len(not_copa) > 1:
                for nt in not_copa:
                    (lineno(), "NT:", nt, "not_dico:", not_dico)
                    if nt.isdigit():
                        '''nt = not_type = Tonalité des degrés.
                        Quand nt = 1. La gamme reste majeure, sa tonalité est affectée par le signe d'altération.'''
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
                        (lineno(), "nt signe:", nt, "not_alto:", not_alto)
            # ############################# CONTRÔLE SAISIE ###############################################
            "# Contrôle de l'entrée utilisateur"
            k1_dic = list(not_dico.keys())
            k1_dic.sort()  # k1_dic = Liste des clés des degrés choisis par l'utilisateur.
            gam_nat = []  # Recueil les degrés inchangés et hors tip_form
            mod_use = ''
            (lineno(), "not_dico:", not_dico)
            for k1 in k1_dic:  # Liste les clés de not_dico.keys()
                k0 = int(k1)  # k0 = Copie le degré original.
                if not_dico[k1][0] in tab_sup:  # Le signe d'altération est parmi les signes augmentés.
                    (lineno(), "tab_sup = ['', '+', 'x', '^', '+^', 'x^', '^^', '+^^', 'x^^',,, ")
                    ind_k2 = tab_sup.index(not_dico[k1][0])  # Son emplacement parmi les signes.
                    gam_k20 = gam_maj.index(str(k0))  # Son emplacement dans la gamme avant d'avoir été altéré.
                    gam_k21 = gam_maj.index(str(k0)) + ind_k2  # Son emplacement dans la gamme après avoir été altéré.
                    (lineno(), "K0:", k0, "gam_k20:", gam_k20, "gam_k21:", gam_k21)
                    if tip_form[gam_k21] == "":
                        if str(k0) in tip_form:
                            lis_f = [i for i in tip_form if i not in ("", "1")]  # La tonique est omise ici
                            if not_dico[k1][1] in dic_120[gam_k21]:
                                tip_form[gam_k21] = str(int(max(lis_f))+1)
                                (lineno(), "tip_form:", tip_form)
                            (lineno(), "dic_120:", dic_120[gam_k21], "not_dico[k1][0]:", not_dico[k1][1])
                            (lineno(), "\t* Présent_tip_form:", tip_form, "*\nstr(k0):", str(k0), "lis_f:", lis_f)
                        else:
                            tip_form[gam_k21] = str(k0)
                            (lineno(), "tip_form:", tip_form, "str(k0):", str(k0))
                    else:
                        ok_saisie = False
                        message_erreur = "DEUX NOTES ARRIVENT AU MÊME EMPLACEMENT (tab_sup): "
                        print(lineno(), message_erreur, tip_form[gam_k21], "et : ", not_dico[k1][1])
                        print(lineno(), "Case occupée K0 : ", k0, tip_form)
                        print(lineno(), "Erreur")
                    k0 += 1  # Pour inspecter les degrés supérieurs.
                    # Bouclage jusqu'à ce que k0 n'atteigne plus les notes naturelles...
                    "# Le nouveau degré se trouve aussi dans le choix de l'utilisateur."
                    k10 = True
                    while k0 < 8:  # str(k0) not in k1_dic and
                        gam_k22 = gam_maj.index(str(k0))  # Index degré k0+=1
                        gam_k21 += 1
                        (lineno(), "\tK0:", k0, "gam_k22:", gam_k22, "gam_k21:", gam_k21)
                        if gam_k22 > gam_k21 or tip_form[gam_k21] != "":
                            k10 = False
                            (lineno(), "***\t K0:", k0, "tip_form[gam_k21]:", tip_form[gam_k21])
                        if k10 and str(k0) not in (tip_form, k1_dic):
                            tip_form[gam_k21] = str(k0)
                            (lineno(), "k10:", k10, "tip_form:", tip_form, "str(k0):", str(k0))
                        k0 += 1
                        (lineno(), "Addition tip_form:", tip_form)
                elif not_dico[k1][0] in tab_inf:  # Le signe d'altération est parmi les signes diminués.
                    (lineno(), "tab_inf = ['', '-', 'o', '*', '-*', 'o*', '**', '-**', 'o**', '***',,, ")
                    ind_k2 = tab_inf.index(not_dico[k1][0]) - 24  # Son emplacement parmi les signes.
                    gam_k20 = gam_maj.index(str(k0))  # Son emplacement dans la gamme avant avoir été altéré.
                    gam_k21 = gam_maj.index(str(k0)) + ind_k2  # Son emplacement dans la gamme après avoir été altéré.
                    (lineno(), "K0:", k0, "gam_k20:", gam_k20, "gam_k21:", gam_k21, "tip_form:", tip_form[gam_k21])
                    if tip_form[gam_k21] == "":
                        if str(k0) in tip_form:
                            lis_f = [i for i in tip_form if i not in ("", "1")]
                            if not_dico[k1][1] in dic_120[gam_k21] and int(min(lis_f))-1 != 1:
                                tip_form[gam_k21] = str(int(min(lis_f))-1)
                            (lineno(), "dic_120:", dic_120[gam_k21], "not_dico[k1][0]:", not_dico[k1][1])
                            (lineno(), "\t* Présent_tip_form:", tip_form, "*\nstr(k0):", str(k0), "lis_f:", lis_f)
                            # Erreur avec o5x3
                        else:
                            tip_form[gam_k21] = str(k0)
                            (lineno(), "tip_form:", tip_form, "str(k0):", str(k0))
                    else:
                        ok_saisie = False
                        message_erreur = "DEUX NOTES ARRIVENT AU MÊME EMPLACEMENT  (tab_inf): "
                        print(lineno(), message_erreur, tip_form[gam_k21], "et : ", not_dico[k1][1])
                        print(lineno(), "Case occupée K0:", k0, tip_form)
                        print(lineno(), "Erreur")
                    k0 -= 1  # Pour inspecter les degrés inférieurs.
                    # Le nouveau degré ne se trouve pas dans le choix de l'utilisateur.
                    "# k0 n'est pas dans le dictionnaire saisi par l'utilisateur."
                    k10 = True
                    while k0 > 1:  # str(k0) not in k1_dic and
                        gam_k22 = gam_maj.index(str(k0))  # Index degré k0-=1
                        gam_k21 -= 1
                        (lineno(), "str(k0):", str(k0), "\tgam_k22:", gam_k22)
                        if gam_k22 < gam_k21 or tip_form[gam_k21] != "":
                            k10 = False
                            (lineno(), "***\t K0:", k0, "tip_form[gam_k21]:", tip_form[gam_k21])
                        if gam_k22 > gam_k21 >= gam_maj.index(str(k0)):
                            tip_form[gam_k21] = str(k0)
                            (lineno(), "tip_form:", tip_form, "str(k0):", str(k0), "22.21:", gam_k22, gam_k21)
                        if k10 and str(k0) not in tip_form:
                            tip_form[gam_k21] = str(k0)
                            print(lineno(), "tip_form:", tip_form, "str(k0):", str(k0))
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
            print(lineno(), "F tip_form:", tip_form, "gam_nat:", gam_nat)

            if ok_saisie:  # Le format de la saisie est accepté.
                mem_nom, gam_nom = "", "| "
                for qi in not_dico.keys():
                    mem_nom += not_dico[qi][1]
                    gam_nom += tab_type[int(qi)] + " | "
                (lineno(), "mem_nom:", mem_nom, "gam_nom:", gam_nom, "SAISIE OK ----\n\n", tip_form)
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

    if "1" in not_dico.keys():
        '''Quand dans le choix, il y a [signé majeur] = le signé majeur remplace la valeur de note_sig'''
        note_sig = not_dico["1"][0]
        if note_sig in tab_sup:
            ind_sig = tab_sup.index(note_sig)
        elif note_sig in tab_inf:
            ind_sig = tab_inf.index(note_sig) - 24
        print(lineno(), "note_sig:", note_sig)
    (lineno(), "Tonalité signée not_dico:", not_dico)
    (lineno(), "note_dia:", note_dia, "\t\tind_sig:", ind_sig)
    #

    '''Tonique déductive : Cherche les formules numéraires similaires dans globdicTcoup.txt {dic_codage}'''
    if tip_rich == "2":
        """Condition utilisant la gamme recherchée dans le fichier[globdicTcoup.txt/dic_codage (dictionnaire)]"""
        print(lineno(), "not_dico:", not_dico, "\ntip_form:", tip_form)
        for iu in range(6):
            print(iu)

    print(lineno(), "tip_rich:", tip_rich)
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
        for mb in module:
            if mb != '0':
                mod_bin.append('1')
            else:
                mod_bin.append('0')
        print(lineno(), "mod_bin:", mod_bin, "\n\tmodule:", module)

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
                    else:
                        mo += 1
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
            dic_gam[mod_use].append(jeu_jeu)
            (lineno(), "mod_mod:", mod_mod[xm], "mod_jeu:", mod_jeu, "mid_jeu:", mid_jeu)
        (lineno(), "FOR Fonction mode:", module, type(module))

    # Définir la gamme analogique qui est en relation avec la saisie utilisateur.
    def gamme():
        """Fonction chargée de transformer une forme numéraire en une forme analogique"""
        print(lineno(), "dic_maj:", dic_maj[note_dia], "\nnote_dia:", note_dia)
        print(lineno(), "dic_maj:", dic_gam, "\n:", )
        print(lineno(), ":", )

    # Fonction principale ☺
    if mod_use:
        dic_gam[mod_use] = []
        mode(mod_use)
        gamme()
    print(lineno(), ":", )
    (lineno(), "mod_mod:", mod_mod)
    print(lineno(), "dic_gam:", dic_gam)


#
if __name__ == '__main__':
    import inspect
    from typing import Callable

    '# lineno() Pour consulter le programme grâce au suivi des prints'
    lineno: Callable[[], int] = lambda: inspect.currentframe().f_back.f_lineno

    print_hi()
