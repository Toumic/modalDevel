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

    tab_inf.reverse()  # tab_inf = Liste les signes (b) cumulés de zéro à 24 bémols. tab_inf[-2] = 'o'
    tab_inf.remove(tab_inf[-1])
    gam_maj = ['1', '0', '2', '0', '3', '4', '0', '5', '0', '6', '0', '7']
    dic_gam, mod_bin, mod_mod = {}, [], {}
    lis_gam1, lis_gam2 = "1234567", "12345678"  # Afin de comparer l'ordre des chiffres de l'utilisateur.
    zer_zer, gam_gam = False, False
    (lineno(), "tab_inf:", tab_inf)
    message_erreur = ""
    not_dico = {}  # Dictionnaire contenant le(s) choix utilisateur.

    "# Choisir la tonique par construction ou par déduction"
    note_dia = "d"  # input("Choisissez la tonique [C, D, E, F, G, A, B] : ")
    if not note_dia.isupper():  # Mettre en majuscule.
        note_dia = note_dia.upper()  # ("Note transformée en majuscule", note_dia)

    "# L'utilisateur altère la tonique"
    note_sig = ""  # input("Choisissez l'altération [+, x, ^, -, o, *] : ")
    if note_sig in tab_inf:
        ind_sig = tab_inf.index(note_sig) - 24
    else:
        ind_sig = tab_sup.index(note_sig)

    ok_saisie = True
    while 1:
        "# Choisir le type de tonalité (pouvant être une mélodique diminuée (o3))"
        '''# Plage des signes portés sur les degrés :  # Dictionnaire {dic_deg}
        deg2[-2, +^2], deg3[o3, ^3], deg4[o4, ^4], deg5[*5, x5], deg6[-*6, +6], deg7[o*7, 7]'''
        tab_type = ["majeure", "tonale", "mélodique", "médiane", "dominante", "harmonique", "sensible"]
        if message_erreur:
            print("############################################################################")
            print(lineno(), message_erreur, "Changez votre choix !", not_dico)
        not_type = input("############################ FAITES VOTRE CHOIX ############################\n"
                         "[1= majeure, 2=tonale, 3=mélodique, 4=médiane, 5=dominante, 6=harmonique, 7=sensible] \n"
                         "les signes : [+, x, ^, -, o, *]. Une mélo (-3). Une mélo + diminuée harmone (-3o6)\n"
                         "Attention les chevauchements sont transformés, exp (x5o6) devient (5 6)\n"
                         "Vérifiez votre sélection pour éviter les erreurs (Les notes se suivent dans l'ordre)\n"
                         "Choisir un type ou plusieurs types de gamme : ")
        print(lineno(), "\n")
        "# Traitement des demandes des tonalités signées"
        "# Signer le niveau majeur, c'est comme signer la note tonique (note_sig/ind_sig)"
        not_alto, not_copa, deg_duo = "", not_type, []
        not_dico.clear()  # not_dico = {'1': ['o', 'o1'], '5': ['*', '*5']}
        if len(not_copa) > 1:
            for nt in not_copa:
                print(lineno(), "NT:", nt, "not_dico:", not_dico)
                if nt.isdigit():
                    '''nt = not_type = Tonalité des degrés.
                    Quand nt = 1. La gamme reste majeure, mais sa tonalité est affectée par le signe d'altération.'''
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
                            print(lineno(), "not_glob:", not_glob, "dic_deg:", dic_deg[str(nt)])
                    not_dico[not_type] = [not_alto]
                    not_dico[not_type].append(not_glob)
                    print(lineno(), "not_dico:", not_dico, "not_alto:", not_alto)
                    not_alto = ""
                    print(lineno(), "not_type:", not_type, "not_glob:", not_glob, "NT:", nt)
                else:
                    not_alto += nt
                    print(lineno(), "nt signe:", nt, "not_alto:", not_alto)
        # ############################# CONTRÔLE SAISIE ###############################################
        "# Contrôle de l'entrée utilisateur"
        k1_dic = list(not_dico.keys())
        k1_dic.sort()  # k1_dic = Liste des clés des degrés choisis par l'utilisateur.
        k2 = k3 = 0
        for k1 in k1_dic:  # Liste les clés de not_dico.keys()
            gam_k20, gam_k21, gam_k30, gam_k31, ind_k2, ind_k3 = "", "", "", "", None, None
            k0 = int(k1)  # k0 = Copie le degré original.
            print(lineno(), "not_dico:", not_dico)
            if not_dico[k1][0] in tab_sup:  # Le signe d'altération est parmi les signes augmentés.
                ind_k2 = tab_sup.index(not_dico[k1][0])  # Son emplacement parmi les signes.
                gam_k20 = gam_maj.index(str(k0))  # Son emplacement dans la gamme avant avoir été altéré.
                gam_k21 = gam_maj.index(str(k0)) + ind_k2  # Son emplacement dans la gamme après avoir été altéré.
                k0 += 1  # Pour inspecter les degrés supérieurs.
                if str(k0) in k1_dic:  # Le nouveau degré se trouve aussi dans le choix de l'utilisateur.
                    if not_dico[str(str(k0))][0] in tab_sup:  # Le nouveau degré est augmenté.
                        ind_k3 = tab_sup.index(not_dico[str(k0)][0])
                        gam_k31 = '0'
                        print(lineno(), "\t\tK1:", k1, "K0:", k0, "ind_k2.3:", ind_k2, ind_k3)
                    else:  # Le nouveau degré est diminué.
                        ind_k3 = tab_inf.index(not_dico[str(k0)][0]) - 24
                        gam_k30 = gam_maj.index(str(k0))  # Son emplacement dans la gamme avant avoir été altéré.
                        gam_k31 = gam_maj.index(str(k0)) + ind_k3  # Le nouveau dans la gamme après avoir été altéré.
                        print(lineno(), "\t\tK1:", k1, "K0:", k0, "ind_k2.3:", ind_k2, ind_k3)
                (lineno(), "gam_k21.3:", gam_k21, ind_k2, gam_k31, ind_k3)
                print(lineno(), "k1:", k1, "K2:", k2, "k3:", k3, "\n... gam_k21:", gam_k21, "gam_k31:", gam_k31)

            elif not_dico[k1][0] in tab_inf:  # Le signe d'altération est parmi les signes diminués.
                if not_dico[k1][0] in tab_sup:  # Le signe d'altération est parmi les signes augmentés.
                    print(lineno(), "AUG\t\tK1:", k1)
                else:  # Le nouveau degré est diminué.
                    ind_k2 = tab_inf.index(not_dico[k1][0]) - 24  # Son emplacement parmi les signes.
                    gam_k20 = gam_maj.index(str(k0))  # Son emplacement dans la gamme avant avoir été altéré.
                    gam_k21 = gam_maj.index(str(k0)) + ind_k2  # Son emplacement dans la gamme après avoir été altéré.
                    k0 -= 1  # Pour inspecter les degrés inférieurs.
                    if str(k0) not in k1_dic:
                        print(lineno(), "DIM not\t\tK0:", k0)
                    else:
                        print(lineno(), "DIM yes\t\tK0:", k0)
            else:
                ok_saisie = False
                print(lineno(), "L'altération est inconnue : ", not_dico[k1][0], gam_k21, gam_k31)

            if gam_k21 and gam_k21 == gam_k31:
                ok_saisie = False
                message_erreur = "DEUX NOTES ARRIVENT AU MÊME EMPLACEMENT"
                print(lineno(), "ATTENTION Deux notes ont le même emplacement", not_dico[k1], "et:", not_dico[str(k0)])

            (lineno(), "K1:", k1, "not_dico[k1]:", not_dico[k1])
        if ok_saisie:  # Le format de la saisie est accepté.
            mem_nom = ""
            for qi in not_dico.keys():
                mem_nom += not_dico[qi][1]
            print(lineno(), "mem_nom:", mem_nom,  "SAISIE OK ---------------------------------\n\n")
            break

    #   ###############################################################################################
    "# Choix d'une définition stricte ou déductive"
    tip_rich = input("0 = Recherche formule. 1 = Recherche stricte. 2 = Recherche déductive : ")
    '''Tonique constructive : Crée une formule numéraire stricte.
    En suivant les choix de l'utilisateur du dictionnaire not_dico'''

    #   ###############################################################################################
    #
    if "1" in not_dico.keys():
        '''Quand dans le choix, il y a [signé majeur] = le signé majeur remplace la valeur de note_sig'''
        note_sig = not_dico["1"][0]
        if note_sig in tab_sup:
            ind_sig = tab_sup.index(note_sig)
        elif note_sig in tab_inf:
            ind_sig = tab_inf.index(note_sig) - 24
        print(lineno(), "note_sig:", note_sig)
    (lineno(), "Tonalité signée not_dico:", not_dico)
    (lineno(), "note_dia:", note_dia, "ind_sig:", ind_sig)
    #
    #
    tip_form = ["", "", "", "", "", "", "", "", "", "", "", ""]
    if tip_rich in ("1", "2"):  # dic_codage[336] = Gamme majeure.
        maj_form = dic_codage[336]
        lis_form = list(maj_form)
        cle_dic = list(not_dico.keys())
        tab_form = cle_dic.copy()
        cle_dic.sort()
        print(lineno(), "***   cle_dic:", cle_dic)
        for cd in cle_dic:
            val_cd = not_dico[cd][0]  # Le signe altératif supporté.
            if val_cd in tab_sup:
                ind_cd = tab_sup.index(val_cd), "aug"
            else:
                ind_cd = tab_inf.index(val_cd) - 24, "dim"
            print(lineno(), "val_cd:", val_cd, "not_dico[cd]:", not_dico[cd], "CD:", cd)
            ind_deg = maj_form.index(cd)
            pos_deg = ind_deg + ind_cd[0]
            tip_form[pos_deg] = cd
            cd2 = int(cd)  # cd2 = Reprise du degré original.
            print(lineno(), "pos_deg:", pos_deg, "ind_deg:", ind_deg, "ind_cd:", ind_cd)
            if ind_cd[1] == "aug":
                for pa in range(pos_deg, 12):
                    cd2 += 1  # Degré original augmenté.
                    if str(cd2) in not_dico.keys():
                        print("\t*** CD2 in dico_keys:", "CD2:", cd2, lineno())
                        break
                    if cd2 < 8:
                        ind_cd2 = lis_form.index(str(cd2))
                        if ind_cd2 == pa + 1:
                            tip_form[ind_cd2] = str(cd2)
                            tab_form.append(str(cd2))
                        print("\t", lineno(), "PA:", pa, "CD2:", cd2, "ind_cd2:", ind_cd2)
            elif ind_cd[1] == "dim":
                print(lineno(), "lis_form:", lis_form)
                for pd in range(pos_deg, 1, -1):
                    cd2 -= 1  # Degré original diminué.
                    if str(cd2) in not_dico.keys():
                        print("\t*** CD2 in dico_keys:", "CD2:", cd2, lineno())
                        break
                    ind_cd2 = lis_form.index(str(cd2))
                    print("\t", lineno(), "PD:", pd, "CD2:", cd2, "ind_cd2:", ind_cd2)
            print(lineno(), "ind_deg:", ind_deg, "ind_cd:", ind_cd, "pos_deg:", pos_deg, "tab_form:", tab_form)
        #
        for lg in lis_gam1:
            (lineno(), "LG", lg)
        print(lineno(), "not_dico:", not_dico, "\nlis_form:", lis_form, "\ntip_form:", tip_form)
        (lineno(), "tip_form:", tip_form, "type:", tab_type[int(not_type) - 1], "Exemple mélodique : 102304050607")
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
        (lineno(), "mod_bin:", mod_bin, "\n")

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
