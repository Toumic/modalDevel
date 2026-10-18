#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Auteur : Cabviva septembre 2023

import argparse
import contextlib
import io
from itertools import combinations
import re
import sys
from typing import NamedTuple
from pathlib import Path

from modal_data import (
    ALT_ACTIVITY,
    CHROMATIC_SIGNATURES,
    DIATONIC_POSITIONS,
    DEGREE_SIGNATURES,
    classify_scale,
    modal_state_parts,
    sign_for_value,
)
from modal_catalog import PRE_CLASSIC, PRE_PHYSIC
from modal_names import MODE_NAMES

sys.dont_write_bytecode = True
DEBUG = False
BASE_DIR = Path(__file__).resolve().parent
GLOBDICT_PATH = BASE_DIR / "globdicTcoup.txt"
CONTENT_MODE_PATH = BASE_DIR / "content_mode.txt"
MAJOR_FORMULA_POSITIONS = {0, 2, 4, 5, 7, 9, 11}


class ModalResult(NamedTuple):
    """Résultat modal conservant les métadonnées de sa source."""

    mode_info: list
    dictionary: str
    reference_formula: str
    degree: str
    notes: list
    modal_formula: str
    source_formula: str


class CatalogInhibitionMatch(NamedTuple):
    removed_degrees: tuple
    added_notes: tuple
    tonic_degree: int
    formula: str
    dictionary: str
    mode_name: str
    catalog_id: int
    modal_weight: int
    major_seventh: bool
    inhibited_catalog: bool


pre_classic = PRE_CLASSIC
pre_physic = PRE_PHYSIC
cle_classic, cle_physic = list(pre_classic.keys()), list(pre_physic.keys())


def ensure_data_files():
    """Assure que les fichiers de données nécessaires existent."""
    if not GLOBDICT_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {GLOBDICT_PATH}")
    if not CONTENT_MODE_PATH.exists():
        CONTENT_MODE_PATH.touch(encoding="utf-8")


def print_banner():
    """Affiche une bannière de présentation du programme."""
    print("\n" + "=" * 80)
    print("        MODALDEVEL - RECHERCHE DE GAMMES ET FORMES MODALES")
    print("=" * 80)
    print("Ce programme aide à trouver des gammes et des formes modales à partir d'une tonique.")
    print("Choisissez un mode de recherche : formule, stricte ou déductive.")
    print("Modes disponibles :\n    0 = formule exacte\n    1 = recherche stricte\n    2 = recherche déductive")
    print("=" * 80)


def debug_log(*args):
    """Affiche les diagnostics uniquement en mode debug."""
    if DEBUG:
        print(*args)


def run_demo():
    """Démo rapide pour s'assurer que le programme fonctionne sur un cas standard."""
    print("\nDémonstration rapide : recherche d'une gamme majeure en do.")
    print("Entrées simulées : C / vide / 1 / 1")
    print("-" * 40)
    original_stdin = sys.stdin
    try:
        sys.stdin = __import__('io').StringIO("C\n\n1\n1\n")
        print_hi()
    finally:
        sys.stdin = original_stdin


def print_pro_intro():
    """Présentation du mode pro."""
    print("\nMode Pro - recherche guidée")
    print("- Tonique : C, D, E, F, G, A, B")
    print("- Altération : +, x, ^, -, o, *")
    print("- Types de recherche : 0 = formule, 1 = stricte, 2 = déductive")
    print("- Exemple : gamme majeure, mode tonique, recherche stricte")
    print("- Appuyez sur Entrée pour accepter la valeur par défaut.")
    print("-" * 60)


def run_pro_mode():
    """Mode pro, plus lisible et guidé."""
    print_pro_intro()
    print_hi()


def run_gui():
    """Lance l'interface graphique native basée sur tkinter.ttk."""
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("ModalDevel - Recherche modale")
    root.geometry("1280x760")
    root.minsize(1080, 560)

    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")

    note_var = tk.StringVar(value="C")
    alteration_var = tk.StringVar(value="aucune")
    search_var = tk.StringVar(value="1 - Recherche stricte")
    scale_var = tk.StringVar(value="1")
    formula_var = tk.StringVar(value="102034050607")
    formula_positions = set(MAJOR_FORMULA_POSITIONS)
    formula_touched_positions = set()
    seven_notes_only_var = tk.BooleanVar(value=True)
    sign_var = tk.StringVar()
    degree_var = tk.StringVar(value="2")
    tonic_alteration_symbols = [
        "", "+", "x", "^", "+^", "x^", "^^", "+^^", "x^^", "^^^",
        "+^^^", "x^^^", "^^^^", "+^^^^", "x^^^^", "^^^^^", "+^^^^^",
        "x^^^^^", "^^^^^^", "+^^^^^^", "x^^^^^^", "^^^^^^^", "+^^^^^^^",
        "x^^^^^^^", "^^^^^^^^",
        "-", "o", "*", "-*", "o*", "**", "-**", "o**", "***", "-***", "o***",
        "****", "-****", "o****", "*****", "-*****", "o*****", "******",
        "-******", "o******", "*******", "-*******", "o*******", "********",
    ]
    tonic_alteration_values = tuple(
        "aucune" if not symbol else (
            f"{symbol} = {'#' * index}" if index <= 24 else
            f"{symbol} = {'b' * (index - 24)}"
        )
        for index, symbol in enumerate(tonic_alteration_symbols)
    )
    tonic_alteration_lookup = dict(zip(tonic_alteration_values, tonic_alteration_symbols))
    scale_parts = []

    main = ttk.Frame(root, padding=24)
    main.grid(sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main.columnconfigure(1, weight=1)
    main.rowconfigure(7, weight=1)

    ttk.Label(main, text="ModalDevel", font=("Segoe UI", 22, "bold")).grid(
        row=0, column=0, columnspan=2, sticky="w"
    )
    ttk.Label(
        main,
        text="Recherche de gammes et de formes modales",
    ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

    form = ttk.LabelFrame(main, text="Paramètres de recherche", padding=14)
    form.grid(row=2, column=0, columnspan=2, sticky="ew")
    form.columnconfigure(1, weight=1)

    ttk.Label(form, text="Tonique").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=5)
    ttk.Combobox(
        form, textvariable=note_var, values=("C", "D", "E", "F", "G", "A", "B"),
        state="readonly", width=12,
    ).grid(row=0, column=1, sticky="w", pady=5)

    ttk.Label(form, text="Altération").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=5)
    ttk.Combobox(
        form,
        textvariable=alteration_var,
        values=tonic_alteration_values,
        state="readonly",
        width=30,
    ).grid(row=1, column=1, sticky="w", pady=5)

    ttk.Label(form, text="Recherche").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=5)
    ttk.Combobox(
        form, textvariable=search_var,
        values=("0 - Formule exacte", "1 - Recherche stricte", "2 - Recherche déductive"),
        state="readonly", width=28,
    ).grid(row=2, column=1, sticky="w", pady=5)

    ttk.Checkbutton(
        form,
        text="Maintenir une gamme de 7 notes",
        variable=seven_notes_only_var,
        command=lambda: on_seven_note_limit_toggled(),
    ).grid(row=2, column=2, columnspan=2, sticky="w", padx=(8, 0), pady=5)

    def selected_search_type():
        return search_var.get().split(" ", 1)[0]

    construction_label = ttk.Label(form, text="Construire la gamme")
    construction_label.grid(
        row=3, column=0, sticky="w", padx=(0, 12), pady=5
    )
    degree_label = ttk.Label(form, text="Degré")
    degree_label.grid(row=3, column=1, sticky="w", pady=(0, 2))
    degree_combo = ttk.Combobox(
        form, textvariable=degree_var, values=("2", "3", "4", "5", "6", "7"),
        state="readonly", width=7,
    )
    degree_combo.grid(row=4, column=1, sticky="w", pady=5)

    sign_label = ttk.Label(form, text="Signe")
    sign_label.grid(row=3, column=2, sticky="w", padx=(8, 0), pady=(0, 2))
    sign_combo = ttk.Combobox(
        form,
        textvariable=sign_var,
        values=("", "+", "x", "^", "-", "o", "*"),
        state="readonly", width=7,
    )
    sign_combo.grid(row=4, column=2, sticky="w", padx=(8, 0), pady=5)

    def refresh_sign_choices(*_event):
        """Ne propose que les signes qui restent dans l'octave pour le degré choisi.

        Ex: le degré 7 ne peut pas être augmenté sans empiéter sur la tonique.
        """
        maintain_seven = seven_notes_only_var.get()
        allowed_degrees = available_degrees(scale_parts, maintain_seven)
        degree_combo.configure(values=tuple(allowed_degrees))
        if degree_var.get() not in allowed_degrees:
            degree_var.set(allowed_degrees[0] if allowed_degrees else "")
        allowed = available_signs_for_degree(
            degree_var.get(), scale_parts, maintain_seven
        )
        sign_combo.configure(values=tuple(allowed))
        if sign_var.get() not in allowed:
            sign_var.set(allowed[0] if allowed else "")

    degree_combo.bind("<<ComboboxSelected>>", refresh_sign_choices)
    refresh_sign_choices()

    scale_list_frame = ttk.Frame(form)
    scale_list_frame.grid(row=5, column=1, columnspan=2, sticky="ew", pady=(3, 5))
    scale_part_vars = {}
    solution_frame = ttk.LabelFrame(form, text="Solutions altéractives", padding=6)
    solution_frame.grid(row=6, column=1, columnspan=2, sticky="ew", pady=(0, 5))

    def refresh_scale():
        """Redessine une case à cocher par degré signé actif.

        Une case décochée signale un choix candidat au retrait via 'Retirer'.
        """
        scale_var.set("".join(scale_parts) or "1")
        for child in scale_list_frame.winfo_children():
            child.destroy()
        scale_part_vars.clear()
        if not scale_parts:
            ttk.Label(scale_list_frame, text="(aucun degré signé)").grid(row=0, column=0, sticky="w")
        for index, part in enumerate(scale_parts):
            part_var = tk.BooleanVar(value=False)
            scale_part_vars[part] = part_var
            ttk.Checkbutton(
                scale_list_frame, text=part, variable=part_var,
            ).grid(row=0, column=index, sticky="w", padx=(0, 8))
        refresh_solution_state()

    def refresh_solution_state():
        """Affiche l'état courant des signes proposés pour chaque degré."""
        for child in solution_frame.winfo_children():
            child.destroy()
        state_parts = modal_state_parts(scale_parts)
        if seven_notes_only_var.get():
            selected_degrees = {part[-1] for part in scale_parts}
            ttk.Label(
                solution_frame,
                text=(
                    f"Objectif : 7 notes (tonique incluse) — "
                    f"{len(selected_degrees)}/6 degrés réglés."
                ),
            ).grid(row=0, column=0, sticky="w")
            ttk.Label(
                solution_frame,
                text="État altéractif : " + " | ".join(state_parts),
            ).grid(row=1, column=0, sticky="w")
            return
        ttk.Label(
            solution_frame,
            text=" | ".join(state_parts),
        ).grid(row=0, column=0, sticky="w")

    def confirm_selection_reset(invalidated_parts, new_part):
        from tkinter import messagebox

        return messagebox.askokcancel(
            "Continuité des choix",
            "Le choix " + new_part + " modifie la continuité altéractive.\n\n"
            "Les choix suivants seront retirés : "
            + ", ".join(invalidated_parts)
            + ".\n\nValider la remise en cohérence ?",
            parent=root,
        )

    def add_scale_part():
        degree = degree_var.get()
        existing_degree_parts = [part for part in scale_parts if part[-1] == degree]
        validation_parts = (
            [part for part in scale_parts if part[-1] != degree]
            if seven_notes_only_var.get() and existing_degree_parts
            else scale_parts
        )
        allowed = available_signs_for_degree(
            degree, validation_parts, seven_notes_only_var.get()
        )
        if sign_var.get() not in allowed:
            write_output(
                f"Combinaison refusée : {sign_var.get()}{degree} sortirait de l'octave."
            )
            return
        if (
            seven_notes_only_var.get()
            and not can_add_seven_note_degree(scale_parts, degree)
        ):
            write_output(
                "Les sept degrés sont déjà définis (tonique incluse). "
                "Modifiez un degré déjà choisi au lieu d'en ajouter un."
            )
            return
        new_part = sign_var.get() + degree
        invalidated_parts = invalidated_parts_for_choice(validation_parts, new_part)
        if invalidated_parts:
            if not confirm_selection_reset(invalidated_parts, new_part):
                return
            validation_parts = [
                part for part in validation_parts if part not in invalidated_parts
            ]
        updated_parts = (
            validation_parts
            if seven_notes_only_var.get() or invalidated_parts
            else list(scale_parts)
        ) + [new_part]
        if seven_notes_only_var.get():
            resolved_parts = resolve_seven_note_overlaps(updated_parts, new_part)
            if resolved_parts is None:
                write_output(
                    f"Combinaison refusée : {new_part} ne laisse pas de place "
                    "à une gamme de sept notes."
                )
                return
            updated_parts = resolved_parts
        scale_parts[:] = updated_parts
        refresh_scale()
        refresh_sign_choices()

    def remove_scale_part():
        """Retire les degrés dont la case a été cochée."""
        to_remove = {part for part, var in scale_part_vars.items() if var.get()}
        if not to_remove:
            return
        scale_parts[:] = [part for part in scale_parts if part not in to_remove]
        refresh_scale()
        refresh_sign_choices()

    def clear_scale_parts():
        scale_parts.clear()
        refresh_scale()
        refresh_sign_choices()

    def reset_form():
        """Remet la saisie à son état initial pour permettre de changer de démarche."""
        note_var.set("C")
        alteration_var.set("aucune")
        search_var.set("1 - Recherche stricte")
        formula_positions.clear()
        formula_positions.update(MAJOR_FORMULA_POSITIONS)
        formula_touched_positions.clear()
        seven_notes_only_var.set(True)
        scale_parts.clear()
        refresh_scale()
        refresh_sign_choices()
        refresh_formula_grid()
        write_output("")

    def current_scale_input():
        """Retourne le cumul ou, à défaut, l'expression actuellement sélectionnée."""
        if scale_parts:
            return "".join(scale_parts)
        selected_expression = sign_var.get() + degree_var.get()
        return selected_expression if sign_var.get() or degree_var.get() != "1" else "1"

    refresh_scale()

    add_button = ttk.Button(form, text="Ajouter", command=add_scale_part)
    add_button.grid(row=4, column=3, padx=(8, 0), pady=5)
    remove_button = ttk.Button(form, text="Retirer", command=remove_scale_part)
    remove_button.grid(row=5, column=3, padx=(8, 0), pady=2)
    clear_button = ttk.Button(form, text="Effacer la gamme", command=clear_scale_parts)
    clear_button.grid(
        row=7, column=1, sticky="w", pady=(0, 5)
    )
    ttk.Button(form, text="Réinitialiser la saisie", command=reset_form).grid(
        row=7, column=2, sticky="w", pady=(0, 5)
    )
    construction_help = ttk.Label(
        form, text="Choisissez d'abord un degré, puis un signe. Cochez pour retirer."
    )
    construction_help.grid(row=8, column=0, columnspan=4, sticky="w", pady=(3, 0))
    formula_label = ttk.Label(form, text="Formule exacte")
    formula_label.grid(row=9, column=0, sticky="w", padx=(0, 12), pady=5)
    formula_grid = ttk.Frame(form)
    formula_grid.grid(row=9, column=1, columnspan=3, sticky="w", pady=5)
    construction_widgets = (
        construction_label,
        degree_label,
        degree_combo,
        sign_label,
        sign_combo,
        add_button,
        remove_button,
        scale_list_frame,
        solution_frame,
        clear_button,
        construction_help,
    )
    ttk.Label(formula_grid, text="Forme majeure").grid(
        row=0, column=0, columnspan=12, sticky="w"
    )
    major_degree_labels = {
        position: str(degree)
        for degree, position in enumerate(sorted(MAJOR_FORMULA_POSITIONS), start=1)
    }
    formula_cells = []
    for position in range(12):
        ttk.Label(
            formula_grid,
            text=major_degree_labels.get(position, ""),
            width=4,
            anchor="center",
        ).grid(row=1, column=position, padx=1)
        cell = tk.Button(
            formula_grid,
            width=4,
            relief="raised",
            borderwidth=1,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            background="#F0F0F0",
            activebackground="#E0E0E0",
            foreground="#17324D" if position in formula_positions else "#666666",
            command=lambda index=position: toggle_formula_position(index),
        )
        cell.grid(row=2, column=position, padx=1)
        formula_cells.append(cell)

    def refresh_formula_grid():
        formula = formula_from_positions(formula_positions)
        formula_var.set(formula)
        active_number = 0
        for position, cell in enumerate(formula_cells):
            if position in formula_positions:
                active_number += 1
                cell.configure(
                    text=str(active_number),
                    background="#D9EAF7" if position in formula_touched_positions else "#F0F0F0",
                    activebackground="#B8D8F0" if position in formula_touched_positions else "#E0E0E0",
                    foreground="#17324D",
                )
            else:
                cell.configure(
                    text="0",
                    background="#D9EAF7" if position in formula_touched_positions else "#F0F0F0",
                    activebackground="#B8D8F0" if position in formula_touched_positions else "#E0E0E0",
                    foreground="#666666",
                )

    def toggle_formula_position(position):
        if position in formula_positions:
            formula_positions.remove(position)
        else:
            if seven_notes_only_var.get() and len(formula_positions) >= 7:
                from tkinter import messagebox

                include_note = messagebox.askyesno(
                    "Limite de sept notes",
                    "Voulez-vous inclure cette note ?\n\n"
                    "La sélection dépassera sept notes. Vous pourrez retirer les "
                    "notes devenues inutiles avant la recherche, ou poursuivre avec "
                    "plus de sept notes ; l'option sera alors décochée au lancement.",
                    parent=root,
                )
                if not include_note:
                    return
            if len(formula_positions) >= 12:
                from tkinter import messagebox

                messagebox.showinfo(
                    "Limite de la formule",
                    "Les douze cases sont déjà sélectionnées.",
                    parent=root,
                )
                return
            formula_positions.add(position)
        formula_touched_positions.add(position)
        refresh_formula_grid()
        if seven_notes_only_var.get() and len(formula_positions) > 7:
            write_output(
                f"{len(formula_positions)} notes sélectionnées. Retirez les notes "
                "devenues inutiles en cliquant sur leurs cases avant la recherche."
            )

    def on_seven_note_limit_toggled():
        refresh_sign_choices()
        refresh_solution_state()

    refresh_formula_grid()

    def refresh_formula_visibility(*_event):
        if selected_search_type() == "0":
            formula_label.grid()
            formula_grid.grid()
            for widget in construction_widgets:
                widget.grid_remove()
        else:
            formula_label.grid_remove()
            formula_grid.grid_remove()
            for widget in construction_widgets:
                widget.grid()

    search_var.trace_add("write", refresh_formula_visibility)
    refresh_formula_visibility()

    output = tk.Text(main, height=18, wrap="none", state="disabled", font=("Consolas", 10))
    output.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=(18, 10))
    output.tag_configure(
        "uninhibited_degree",
        font=("Consolas", 10, "bold"),
        foreground="#003B70",
        background="#FFF2A8",
    )
    scrollbar = ttk.Scrollbar(main, orient="vertical", command=output.yview)
    scrollbar.grid(row=7, column=2, sticky="ns", pady=(18, 10))
    horizontal_scrollbar = ttk.Scrollbar(main, orient="horizontal", command=output.xview)
    horizontal_scrollbar.grid(row=8, column=0, columnspan=2, sticky="ew")
    output.configure(yscrollcommand=scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

    def write_output(text, bold_spans=()):
        output.configure(state="normal")
        output.delete("1.0", tk.END)
        output.insert("1.0", text)
        for start, end in bold_spans:
            output.tag_add(
                "uninhibited_degree",
                f"1.0 + {start} chars",
                f"1.0 + {end} chars",
            )
        output.configure(state="disabled")

    def handle_gui_exception(exception_type, exception, traceback_object):
        """Affiche les erreurs Tkinter dans la fenêtre au lieu d'une alerte système."""
        import traceback

        details = "".join(traceback.format_exception(exception_type, exception, traceback_object))
        write_output(f"Erreur dans l'interface :\n{details}")

    root.report_callback_exception = handle_gui_exception

    def display_result(captured_text):
        """Ne montre dans la GUI que le résumé final du moteur terminal."""
        marker = "RÉSULTAT DE LA RECHERCHE"
        if marker in captured_text:
            result_text = captured_text[captured_text.index(marker):]
        else:
            result_text = captured_text
        write_output(result_text, uninhibited_degree_spans(result_text))

    def search():
        search_type = selected_search_type()
        if (
            should_disable_seven_note_limit(search_type, len(formula_positions))
            and seven_notes_only_var.get()
        ):
            seven_notes_only_var.set(False)
            refresh_solution_state()
        scale_input = formula_var.get() if search_type == "0" else current_scale_input()
        alteration = tonic_alteration_lookup.get(alteration_var.get(), alteration_var.get())
        values = "\n".join((note_var.get(), alteration, search_type, scale_input))
        captured = io.StringIO()
        original_stdin = sys.stdin
        try:
            classic_physic.clear()
            tab_key.clear()
            sys.stdin = io.StringIO(values)
            with contextlib.redirect_stdout(captured):
                print_hi(
                    require_seven_notes=seven_notes_only_var.get(),
                    exact_formula_positions=(
                        formula_positions if search_type == "0" else None
                    ),
                )
        except Exception as error:
            write_output(f"Erreur de recherche : {error}")
            return
        finally:
            sys.stdin = original_stdin
        display_result(captured.getvalue())

    buttons = ttk.Frame(main)
    buttons.grid(row=9, column=0, columnspan=2, sticky="e", pady=(8, 0))
    ttk.Button(buttons, text="Lancer la recherche", command=search).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(buttons, text="Effacer", command=lambda: write_output("")).grid(row=0, column=1)

    root.bind("<Return>", lambda _event: search())
    root.mainloop()


def prompt_choice(prompt, valid_values, default=None):
    """Demande une valeur avec validation simple."""
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        if raw in valid_values:
            return raw
        print(f"Choix invalide. Valeurs acceptées : {', '.join(valid_values)}")


def normalize_scale_input(value):
    """Accepte les altérations avant ou après le degré et renvoie signe + degré."""
    value = value.replace(" ", "")
    if not value:
        return value

    if value[0] in "1234567":
        value = re.sub(r"([1-7])([+x^\-o*]+)", r"\2\1", value)
    tokens = re.findall(r"[+x^\-o*]*[1-7]", value)
    if "".join(tokens) != value:
        raise ValueError("utilisez uniquement les degrés 1 à 7 et les signes +, x, ^, -, o, *")
    return "".join(tokens)


def formula_from_positions(selected_positions):
    """Construit une formule chromatique en renumérotant les notes actives."""
    selected_positions = set(selected_positions)
    formula = []
    degree = 0
    for position in range(12):
        if position in selected_positions:
            degree += 1
            formula.append(str(degree))
        else:
            formula.append("0")
    return "".join(formula)


def should_disable_seven_note_limit(search_type, selected_note_count):
    """Indique si une recherche exacte porte sur un nombre de notes variable."""
    return search_type == "0" and selected_note_count != 7


def uninhibited_degree_spans(text):
    """Renvoie les positions des degrés conservés dans les lignes de définitions."""
    spans = []
    offset = 0
    inhibited_column = None
    for line in text.splitlines(keepends=True):
        columns = line.rstrip("\r\n").split(" | ")
        if columns[0].strip() == "Formule":
            inhibited_column = (
                columns.index("Inhibé")
                if "Inhibé" in columns
                else None
            )
        elif line.startswith("- "):
            separators = list(re.finditer(r" \| ", line))
            if len(separators) >= 1 and (
                inhibited_column is None or len(separators) >= inhibited_column
            ):
                formula_start = 2
                formula = line[formula_start:formula_start + 12]
                if inhibited_column is None:
                    inhibited_value = ""
                else:
                    inhibited_start = separators[inhibited_column - 1].end()
                    inhibited_end = (
                        separators[inhibited_column].start()
                        if len(separators) > inhibited_column
                        else len(line.rstrip("\r\n"))
                    )
                    inhibited_value = line[inhibited_start:inhibited_end]
                inhibited_degrees = {
                    int(degree)
                    for degree in re.findall(r"\d+", inhibited_value)
                }
                for index, character in enumerate(formula):
                    if character != "0" and int(character) not in inhibited_degrees:
                        spans.append(
                            (offset + formula_start + index,
                             offset + formula_start + index + 1)
                        )
        offset += len(line)
    return spans


def format_catalog_definition_table(definitions, headers=None):
    """Aligne les colonnes du tableau des définitions cataloguées."""
    if headers is None:
        headers = (
            "Formule",
            "Mode",
            "Tonique",
            "Ajout",
            "Inhibé",
            "Dictionnaire",
            "Poids",
            "Septième",
        )
    rows = [headers, *definitions]
    widths = [
        max(len(str(row[column])) for row in rows)
        for column in range(len(headers))
    ]
    widths[0] = max(widths[0], 12)
    return [
        "  "
        + " | ".join(
            str(value).ljust(widths[column])
            for column, value in enumerate(row)
        )
        if row_index == 0
        else "- "
        + str(row[0]).ljust(widths[0])
        + " | "
        + " | ".join(
            str(value).ljust(widths[column])
            for column, value in enumerate(row[1:], start=1)
        )
        for row_index, row in enumerate(rows)
    ]


def modal_weight_from_formula(formula, included_degrees=None):
    """Pèse seulement les altérations du résultat : un degré naturel vaut 0.

    Un degré altéré vaut ±(degré + nombre de demi-tons), comme #4 = +5 ou
    b3 = -4. Le mode tonique naturel pèse donc 0 et sert de référence.
    """
    natural_positions = {"1": 0, **DIATONIC_POSITIONS}
    if included_degrees is not None:
        included_degrees = set(included_degrees)
    weight = 0
    degree_positions = {}
    for position, degree in enumerate(formula):
        if degree != "0" and (
            included_degrees is None or degree in included_degrees
        ):
            degree_positions[degree] = position
            alteration = (position - natural_positions[degree] + 6) % 12 - 6
            if alteration:
                weight += (1 if alteration > 0 else -1) * (
                    int(degree) + abs(alteration)
                )
    return weight, degree_positions.get("7") == 11


def format_modal_table(rows):
    """Aligne les modes trouvés en colonnes sous un en-tête commun."""
    headers = ("Gamme analogique", "Forme", "Mode", "Dictionnaire")
    widths = [
        max(len(headers[column]), *(len(row[column]) for row in rows))
        for column in range(4)
    ]
    lines = [" | ".join(
        value.ljust(widths[column]) for column, value in enumerate(headers)
    )]
    lines.extend(
        " | ".join(value.ljust(widths[column]) for column, value in enumerate(row))
        for row in rows
    )
    return "\n".join(line.rstrip() for line in lines)

def signed_degrees_name(formula):
    """Nomme une formule par ses degrés altérés, comme +3+4-6o7."""
    natural_positions = {"1": 0, **DIATONIC_POSITIONS}
    parts = []
    for position, degree in enumerate(formula):
        if degree in natural_positions and degree != "0":
            alteration = position - natural_positions[degree]
            if alteration:
                parts.append(sign_for_value(alteration) + degree)
    return "".join(parts) or "majeur"


def chromatic_spellings_for_position(position):
    """Retourne les graphies majeures/sharp et enharmoniques flat d'une position."""
    spellings = {
        0: ("1",),
        1: ("+1", "-2"),
        2: ("2",),
        3: ("+2", "-3"),
        4: ("3",),
        5: ("4",),
        6: ("+4", "-5"),
        7: ("5",),
        8: ("+5", "-6"),
        9: ("6",),
        10: ("+6", "-7"),
        11: ("7",),
    }
    return spellings[position % 12]


def find_catalog_inhibition_matches(selected_positions):
    """Teste les inhibitions requises et les modes toniques des deux catalogues."""
    positions = sorted(set(selected_positions))
    matches = []
    catalogs = (("classic", pre_classic), ("physic", pre_physic))
    formulas_by_positions = {}
    for dictionary_name, catalog in catalogs:
        for formula, catalog_entry in catalog.items():
            formula_positions = frozenset(
                index for index, degree in enumerate(formula) if degree != "0"
            )
            formulas_by_positions.setdefault(formula_positions, []).append(
                (formula, dictionary_name, catalog_entry)
            )
    if len(positions) < 7:
        selected_position_set = frozenset(positions)
        seen_matches = set()
        for _dictionary_name, catalog in catalogs:
            for formula, catalog_entry in catalog.items():
                catalog_positions = {
                    degree: position
                    for position, degree in enumerate(formula)
                    if degree != "0"
                }
                if len(catalog_positions) != 7:
                    continue
                for tonic_degree, tonic_position in catalog_positions.items():
                    rotated_positions = frozenset(
                        (position - tonic_position) % 12
                        for position in catalog_positions.values()
                    )
                    if not selected_position_set.issubset(rotated_positions):
                        continue
                    added_positions = tuple(
                        sorted(rotated_positions - selected_position_set)
                    )
                    for (
                        candidate_formula,
                        matched_dictionary,
                        candidate_entry,
                    ) in formulas_by_positions.get(rotated_positions, ()):
                        match_key = (
                            candidate_formula,
                            matched_dictionary,
                            int(tonic_degree),
                        )
                        if match_key in seen_matches:
                            continue
                        seen_matches.add(match_key)
                        candidate_positions = {
                            degree: (position - tonic_position) % 12
                            for degree, position in catalog_positions.items()
                        }
                        removed_degrees = tuple(
                            int(degree)
                            for degree, position in candidate_positions.items()
                            if position not in selected_position_set
                        )
                        weight, major_seventh = modal_weight_from_formula(
                            candidate_formula
                        )
                        matches.append(CatalogInhibitionMatch(
                            removed_degrees,
                            tuple(
                                f"case {position + 1}: "
                                f"{' / '.join(chromatic_spellings_for_position(position))}"
                                for position in added_positions
                            ),
                            int(tonic_degree),
                            candidate_formula,
                            matched_dictionary,
                            candidate_entry[0],
                            candidate_entry[1],
                            weight,
                            major_seventh,
                            True,
                        ))
        return sorted(
            matches,
            key=lambda match: (
                not match.major_seventh,
                abs(match.modal_weight),
                match.removed_degrees,
                match.tonic_degree,
                match.dictionary,
                match.formula,
            ),
        )

    source_degrees = {
        position: degree for degree, position in enumerate(positions, start=1)
    }
    for remaining_positions in combinations(positions, 7):
        removed_degrees = tuple(
            source_degrees[position]
            for position in positions
            if position not in remaining_positions
        )
        for tonic_position in remaining_positions:
            rotated_positions = frozenset(
                (position - tonic_position) % 12
                for position in remaining_positions
            )
            tonic_degree = positions.index(tonic_position) + 1
            for formula, dictionary_name, catalog_entry in formulas_by_positions.get(
                rotated_positions, ()
            ):
                weight, major_seventh = modal_weight_from_formula(formula)
                matches.append(CatalogInhibitionMatch(
                    removed_degrees,
                    (),
                    tonic_degree,
                    formula,
                    dictionary_name,
                    catalog_entry[0],
                    catalog_entry[1],
                    weight,
                    major_seventh,
                    False,
                ))
    return sorted(
        matches,
        key=lambda match: (
            not match.major_seventh,
            abs(match.modal_weight),
            match.removed_degrees,
            match.tonic_degree,
            match.dictionary,
            match.formula,
        ),
    )


def format_catalog_match_analysis(source_formula, match):
    """Produit le schéma terminal des transformations ayant mené à un match."""
    if match.inhibited_catalog:
        additions = ", ".join(match.added_notes) or "aucune"
        inhibited = ", ".join(map(str, match.removed_degrees)) or "aucun"
        return (
            f"Schéma : {source_formula} -- notes à ajouter [{additions}] --> "
            f"{match.formula} -- rotation du degré tonique catalogué "
            f"{match.tonic_degree}, inhibition des degrés [{inhibited}] --> "
            f"{match.dictionary} « {match.mode_name} » "
            f"(poids {match.modal_weight})"
        )
    inhibited = ", ".join(map(str, match.removed_degrees)) or "aucun"
    return (
        f"Schéma : {source_formula} -- inhibition des degrés source "
        f"[{inhibited}] --> rotation du degré source {match.tonic_degree} --> "
        f"{match.formula} -- concordance {match.dictionary} "
        f"« {match.mode_name} » (poids {match.modal_weight})"
    )


def start_interactive_menu():
    """Menu principal, simple et lisible."""
    while True:
        print("\nBienvenue dans ModalDevel")
        print("1. Rechercher une gamme")
        print("2. Mode pro")
        print("3. Voir une démonstration")
        print("4. Quitter")
        choice = prompt_choice("Votre choix [1] : ", {"1", "2", "3", "4"}, "1")

        if choice == "2":
            run_pro_mode()
            continue
        if choice == "3":
            run_demo()
            continue
        if choice == "4":
            print("Merci, à bientôt.")
            return
        print_hi()
        again = prompt_choice("Recommencer ? [o/n] : ", {"o", "n"}, "o")
        if again.lower() == "n":
            print("Merci, à bientôt.")
            return


def build_parser():
    """Crée le parser CLI du programme."""
    parser = argparse.ArgumentParser(
        description="Recherche de gammes et formes modales selon une tonique et une recherche donnée.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Exécute une courte démonstration au lieu du mode interactif complet.",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Masque la bannière de présentation.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Affiche les messages de diagnostic de développement.",
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Démarre directement le mode pro guidé.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Démarre l'interface graphique tkinter.ttk.",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Démarre le menu interactif dans le terminal.",
    )
    return parser


def cli_main():
    """Boucle principale de l'interface interactive."""
    global DEBUG
    args = build_parser().parse_args()
    DEBUG = args.debug
    ensure_data_files()
    launch_gui = args.gui or not (args.cli or args.pro or args.demo)
    if not args.no_banner and not launch_gui:
        print_banner()
    try:
        if launch_gui:
            run_gui()
        elif args.pro:
            run_pro_mode()
        elif args.demo:
            run_demo()
        else:
            start_interactive_menu()
    except KeyboardInterrupt:
        print("\nInterruption demandée par l'utilisateur.")
    except Exception as exc:
        print(f"\nErreur pendant l'exécution : {exc}")
        raise


# # Vérification fichier des 462 modes de tétracordes couplés
"""
Dictionnaire "dic_codage" = Liste globale des modèles modaux.
Dictionnaire "pre_classic" = Clefs toniques fondamentales en version classique (sommaire).
    Sommaire = Les notes altérées par un signe forment la base hiérarchique,,,
Dictionnaire pre_physic = Clefs toniques primitives en version physique (poids).
    Physique = Les notes altérées forment des pesants gravitationnels,,,"""

"# Permettre la lecture des noms de gammes à l'envers (précaution) : variable = 'str', variable[::-1] = 'rts'."
dic_codage = {}
with GLOBDICT_PATH.open('r', encoding='utf-8') as pre_codage:
    cod = 0
    for pre_cod in pre_codage:
        cod += 1
        dic_codage[cod] = pre_cod.strip()[:12]
        '''Instructions pour chercher un mode dans le fichier 'dic_codage'
        abc = "100234005607"
        if dic_codage[cod] == abc:
            print("cod:", cod,)'''
# print('pre_codage/cod :', cod, ' Nombre de codages modaux.', dic_codage)
maj_form = dic_codage[336]
gam_form = list(maj_form)  # Construction de la liste numéraire majeure
gam_util = []
tab_key = []
classic_physic = {}
major_scale_dictionary = {}
dic_deg = DEGREE_SIGNATURES
dic_120 = CHROMATIC_SIGNATURES


def valid_signs_for_degree(degree):
    """Signes simples utilisables pour un degré sans sortir de l'octave.

    Ex: le degré 7 ne peut pas être augmenté sans empiéter sur la tonique de
    l'octave suivante ; dic_deg ne liste donc aucune entrée '+7'/'x7'/'^7'.
    """
    if degree not in dic_deg:
        return [""]
    return [entry[:-1] for entry in dic_deg[degree]]


def alteration_value(sign):
    """Classe une altération selon sa force ascendante ou descendante."""
    positive = {"+": 1, "x": 2, "^": 3}
    negative = {"-": -1, "o": -2, "*": -3}
    value = 0
    for symbol in sign:
        value += positive.get(symbol, negative.get(symbol, 0))
    return value


def forced_alteration_total(degree, selected_parts):
    """Cumule la force altéractive reçue par un degré des choix sélectionnés."""
    total = 0
    for source, propagated in forced_propagations(selected_parts):
        if propagated[-1] == degree:
            total += alteration_value(propagated[:-1])
    return total


def forced_propagations(selected_parts):
    """Liste les couples (choix source, degré entraîné) sans doublon."""
    selected = set(selected_parts)
    pairs = set()
    for chain in ALT_ACTIVITY:
        for index, item in enumerate(chain[:-1]):
            if item in selected:
                pairs.update((item, follower) for follower in chain[index + 1:])
    return pairs


def seven_note_sign_filter(degree, signs, selected_parts):
    """Retire les signes dont le cumul avec la force reçue sort des signatures du degré."""
    others = [part for part in selected_parts if part[-1] != degree]
    forced_total = forced_alteration_total(degree, others)
    if not forced_total:
        return list(signs)
    return [
        sign for sign in signs
        if sign_for_value(forced_total + alteration_value(sign)) + degree
        in dic_deg.get(degree, [degree])
    ]


def available_signs_for_degree(degree, selected_parts, maintain_seven=False):
    """Retourne les signes compatibles avec la continuité sélectionnée."""
    if maintain_seven:
        return seven_note_sign_filter(
            degree, valid_signs_for_degree(degree), selected_parts
        )
    return base_available_signs_for_degree(degree, selected_parts)


def base_available_signs_for_degree(degree, selected_parts):
    """Applique la continuité altéractive simple, sans cumul des degrés voisins."""
    selected = set(selected_parts)
    forced = set()
    for chain in ALT_ACTIVITY:
        for index, item in enumerate(chain[:-1]):
            if item in selected:
                forced.update(chain[index + 1:])
    forced_for_degree = [item[:-1] for item in forced if item[-1] == degree]
    if forced_for_degree:
        bounds = [alteration_value(sign) for sign in forced_for_degree]
        return [
            sign for sign in valid_signs_for_degree(degree)
            if all(
                alteration_value(sign) >= bound if bound > 0
                else alteration_value(sign) <= bound
                for bound in bounds
            )
        ]

    blocked = set()
    for chain in ALT_ACTIVITY:
        for index, item in enumerate(chain[:-1]):
            if item in selected:
                blocked.update(chain[index + 1:])
    allowed = [
        sign for sign in valid_signs_for_degree(degree)
        if sign + degree not in blocked
    ]
    if degree == "2" and {"-4", "-3"}.intersection(selected):
        return [sign for sign in allowed if sign in ("-", "")]
    return allowed


def seven_note_positions(selected_parts):
    """Retourne les positions chromatiques des degrés 1 à 7 de l'état altéractif."""
    positions = [0]
    for part in modal_state_parts(selected_parts)[1:]:
        positions.append(
            DIATONIC_POSITIONS[part[-1]] + alteration_value(part[:-1])
        )
    return positions


def overlap_count(selected_parts):
    """Compte les chevauchements ou sorties d'octave de l'état à sept notes."""
    positions = seven_note_positions(selected_parts)
    count = sum(
        1 for previous, current in zip(positions, positions[1:])
        if current <= previous
    )
    return count + (positions[-1] > 11)


def weakened_part(part):
    """Réduit d'un cran la force altérative d'un choix."""
    value = alteration_value(part[:-1])
    step = 1 if value > 0 else -1
    return sign_for_value(value - step) + part[-1]


def resolve_seven_note_overlaps(selected_parts, new_part):
    """Desserre les choix voisins pour que la gamme conserve ses sept notes.

    Retourne None quand aucun choix précédent ne peut libérer la place.
    """
    parts = list(selected_parts)
    while overlap_count(parts):
        current_count = overlap_count(parts)
        for index in range(len(parts) - 1, -1, -1):
            part = parts[index]
            if part == new_part or not part[:-1]:
                continue
            candidate = parts[:index] + [weakened_part(part)] + parts[index + 1:]
            if overlap_count(candidate) < current_count:
                parts = candidate
                break
        else:
            return None
    return parts


def available_degrees(selected_parts, maintain_seven=False):
    """Retourne les degrés encore sélectionnables ou entraînés."""
    if maintain_seven:
        excluded_degrees = set()
    elif any(part[:-1] and part[:-1][0] in "+x^" for part in selected_parts):
        excluded_degrees = {"7"}
    else:
        excluded_degrees = set()
    return [
        degree for degree in ("2", "3", "4", "5", "6", "7")
        if degree not in excluded_degrees
        and available_signs_for_degree(degree, selected_parts, maintain_seven)
    ]


def invalidated_parts_for_choice(selected_parts, new_part):
    """Retourne les choix précédents rendus incompatibles par un nouveau choix."""
    available_after_change = available_degrees([new_part])
    return [
        part for part in selected_parts
        if part[:-1] not in available_signs_for_degree(part[-1], [new_part])
        and part[-1] in available_after_change
    ]


def remaining_adjustable_degrees(selected_parts):
    """Retourne les degrés réglables qui ne sont pas encore sélectionnés."""
    selected_degrees = {part[-1] for part in selected_parts}
    return [degree for degree in "234567" if degree not in selected_degrees]


def can_add_seven_note_degree(selected_parts, degree):
    """Autorise au plus six degrés réglés en plus de la tonique implicite."""
    selected_degrees = {part[-1] for part in selected_parts}
    return degree in "234567" and (
        degree in selected_degrees or len(selected_degrees) < 6
    )


def print_hi(require_seven_notes=False, exact_formula_positions=None):
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
    dic_120 = CHROMATIC_SIGNATURES

    tab_inf.reverse()  # tab_inf = Liste les signes (b) cumulés de zéro à 24 bémols. tab_inf[-2] = 'o'
    tab_inf.remove(tab_inf[-1])
    gam_maj = ['1', '0', '2', '0', '3', '4', '0', '5', '0', '6', '0', '7']
    deg_rom = ["I", "II", "III", "IV", "V", "VI", "VII"]
    dic_gam, mod_bin, mod_mod = {}, [], {}
    (lineno(), "tab_inf:", tab_inf)
    message_erreur = ""
    not_dico = {}  # Dictionnaire contenant le(s) choix utilisateur.
    major_scale_dictionary.clear()
    mod_use = ""
    #
    print("\n", lineno(), "##### INPUT NOTE_TONIQUE #########################################################")
    "# Choisir la tonique par construction ou par déduction"
    note_dia = input("<return> par défaut = 'c'.\n"
                     "Choisissez la tonique [C, D, E, F, G, A, B] : ")
    if note_dia == '':
        note_dia = 'C'
    if not note_dia.isupper():  # Mettre en majuscule.
        note_dia = note_dia.upper()  # ("La note est transformée en majuscule", "note_dia")
    #
    print("\n", lineno(), "##### INPUT ALTÉRATION_NOTE ######################################################")
    "# L'utilisateur altère la tonique"
    ord_sup, ord_inf, ind_sig = "+x^", "-o*", ""
    note_sig = input("<return> par défaut = La tonique n'est pas altérée.\n"
                     "Choisissez l'altération [+, x, ^, -, o, *] : ")
    if note_sig != "":
        "# Quand not_alto contient plusieurs altérations"
        if len(note_sig) > 1:  # Reconnaissance des altérations déclarées.
            nbr_un = 0
            for un in note_sig:
                if un in ("1", "2", "3", "4", "5", "6", "7", "8"):
                    continue  # La valeur int(un) est perdue ☺.
                elif un in ord_sup:  # ord_sup = "+x^"
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
    print("\n", lineno(), "##### INPUT TYPE_RECHERCHE #######################################################")
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
                debug_log(lineno(), message_erreur, "Changez votre choix !", not_dico)
            #
            print("\n", lineno(), "##### INPUT GAMME_RECHERCHÉE #############################################")
            "# L'utilisateur choisit les notes et les altérations"
            try:
                not_type = input("############################ FAITES VOTRE CHOIX #########################\n"
                                 "<return> par défaut = majeure.\n"
                                 "[1= majeure, 2=tonale, 3=mélodique, 4=médiane, 5=dominante, 6=harmonique, 7=sensible] \n"
                                 "les signes : [+, x, ^, -, o, *]. ['b=-', '#=+']. '++'=2, '^-'=2, '*x'=-1, '++*'=-1\n"
                                 "Attention les chevauchements sont transformés.\n"
                                 "Ordre recommandé : signe puis degré, par exemple -2+5 ou o3+6.\n"
                                 "Vous pouvez aussi écrire le signe après le degré : 2-5+ devient -2+5.\n"
                                 "Pour '1' = majeur : La tonique n'est pas traitée mais son altération est valide\n"
                                 "Les degrés doivent être saisis dans l'ordre croissant, sans répétition.\n"
                                 "Choisir un type ou plusieurs types de gamme : ")
            except EOFError:
                print("\n\nAucun résultat : la gamme saisie est invalide "
                      "et aucune autre saisie n'est disponible.")
                if message_erreur:
                    print(message_erreur.strip())
                return
            try:
                not_type = normalize_scale_input(not_type)
            except ValueError as error:
                print(f"Saisie invalide : {error}.")
                continue
            if not_type:
                print(f"Saisie interprétée : {not_type}")
            #   #######################################################################################
            #
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
            debug_log(lineno(), "not_dico:", not_dico)
            for k1 in k1_dic:  # Liste les clés de not_dico.keys()
                k0 = int(k1)  # k0 = Copie le degré original.
                if not_dico[k1][0] in tab_sup:  # Le signe d’altération est parmi les signes augmentés.
                    (lineno(), "tab_sup = ['', '+', 'x', '^', '+^', 'x^', '^^', '+^^', 'x^^',,, ")
                    ndk_0 = not_dico[k1][0]
                    ind_k2 = tab_sup.index(ndk_0)  # Son emplacement parmi les signes.
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
                debug_log(lineno(), "gam_nom:", gam_nom, "SAISIE OK ---- \n")
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
                debug_log(lineno(), "* \tmod_use:", mod_use, "gam_nat:", gam_nat, "\n")
                break

    def signal(ds):
        """La fonction reçoit l'altération et retourne sa valeur."""
        if ds in (None, "", "0"):
            return 0

        if isinstance(ds, str):
            if ds in tab_sup:
                return tab_sup.index(ds)
            if ds in tab_inf:
                return tab_inf.index(ds) - 24
            return 0

        if isinstance(ds, int):
            if ds > -1:
                return tab_sup[ds] if ds < len(tab_sup) else 0
            if abs(ds) <= len(tab_inf):
                return tab_inf[ds]
            return 0

        return 0

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
        for dc in range(1, long_code + 1):  # , dic_codage provient des 462 modèles énumérés [GlobdicTcoup.txt].
            ec = str(dic_codage[dc])  # Récupération modèle[ec] du fichier [GlobdicTcoup.txt].
            for key, val in ind_dic.items():  # Lecture dictionnaire utilisateur
                ik = ec.index(key)  # Index de la clé dans le modèle[ec]. Degré = key. Val =
                (lineno(), "ik:", ik, "ec:", ec)
                if ik == val and ec not in tab_key:
                    tab_key.append(ec)
                    (lineno(), "ik:", ik, "key:", key, "ec:", ec, "val:", val)
            (lineno(), "*** ec:", ec)
        (lineno(), "ind_dic:", ind_dic, len(tab_key), "\ntab_key:", tab_key[:5])
        loc = 0
        while loc < 33:  # Répété plusieurs fois pour un meilleur nettoyage.
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
        debug_log(lineno(), "tip_rich = '0':", tip_rich)
        if exact_formula_positions is not None:
            selected_positions = sorted(set(exact_formula_positions))
        else:
            while True:
                formula_input = input(
                    "Entrez une formule chromatique de 12 positions : "
                ).strip()
                if (
                    len(formula_input) == 12
                    and all(character in "0123456789" for character in formula_input)
                ):
                    degrees = [
                        character for character in formula_input if character != "0"
                    ]
                    if degrees == [str(degree) for degree in range(1, len(degrees) + 1)]:
                        selected_positions = [
                            index for index, character in enumerate(formula_input)
                            if character != "0"
                        ]
                        break
                print("Formule invalide : utilisez 12 positions et des degrés croissants.")

        source_formula = formula_from_positions(selected_positions)

        def spell_exact_scale_notes(positions):
            """Écrit les positions de la formule selon la tonalité choisie."""
            major_positions = (0, 2, 4, 5, 7, 9, 11)
            key_notes = dic_maj[note_dia]

            def transpose_note(note, amount):
                letter = note[-1]
                alteration = signal(note[:-1])
                alteration += amount
                symbol = signal(alteration)
                if not isinstance(symbol, str):
                    raise ValueError(
                        f"Altération hors plage lors de l'écriture de {note}."
                    )
                return symbol + letter

            sharp_weight = sum(
                max(signal(note[:-1]), 0)
                for position in major_positions
                for note in (key_notes[position],)
            )
            flat_weight = sum(
                abs(min(signal(note[:-1]), 0))
                for position in major_positions
                for note in (key_notes[position],)
            )
            tonic_shift = signal(note_sig)
            if isinstance(tonic_shift, str):
                tonic_shift = signal(tonic_shift)

            note_names = []
            for position in positions:
                if position in major_positions:
                    note = key_notes[position]
                else:
                    previous_position = max(
                        major_position
                        for major_position in major_positions
                        if major_position < position
                    )
                    next_position = min(
                        major_position
                        for major_position in major_positions
                        if major_position > position
                    )
                    sharp_note = transpose_note(key_notes[previous_position], 1)
                    flat_note = transpose_note(key_notes[next_position], -1)
                    note = (
                        flat_note
                        if flat_weight > sharp_weight
                        else sharp_note
                    )
                note_names.append(transpose_note(note, tonic_shift))
            return note_names

        if len(selected_positions) > 7:
            matches = find_catalog_inhibition_matches(selected_positions)
            print("\n" + "=" * 72)
            print("RÉSULTAT DE LA RECHERCHE")
            print("=" * 72)
            print(f"Formule source : {source_formula}")
            print(f"Notes source : {len(selected_positions)}")
            print(f"Type : {classify_scale(selected_positions)}")
            print(
                "Gamme créée : "
                + " | ".join(spell_exact_scale_notes(selected_positions))
            )
            print(
                "Priorité : correspondances avec une septième majeure, puis "
                "poids modal absolu le plus faible."
            )
            print(f"Correspondances cataloguées : {len(matches)}")
            if matches:
                match_rows = [
                    (
                        match.formula,
                        ", ".join(map(str, match.removed_degrees)) or "aucun",
                        f"degré {match.tonic_degree}",
                        match.mode_name,
                        match.dictionary,
                        str(match.modal_weight),
                        "majeure" if match.major_seventh else "non majeure",
                    )
                    for match in matches
                ]
                headers = (
                    "Formule",
                    "Inhibition source",
                    "Tonique source",
                    "Mode",
                    "Dictionnaire",
                    "Poids modal",
                    "7e",
                )
                for line in format_catalog_definition_table(
                    match_rows,
                    headers=headers,
                ):
                    print(line)
                print("\nANALYSE CIRCONSTANCIELLE — SCHÉMA DES INHIBITIONS ET ROTATIONS")
                for match in matches:
                    print(format_catalog_match_analysis(source_formula, match))
            else:
                print("Aucune correspondance classic/physic trouvée.")
            print("=" * 72)
            return
        if len(selected_positions) < 7:
            matches = find_catalog_inhibition_matches(selected_positions)
            print("\n" + "=" * 72)
            print("RÉSULTAT DE LA RECHERCHE")
            print("=" * 72)
            print(f"Formule source : {source_formula}")
            print(f"Notes source : {len(selected_positions)}")
            print(f"Type : {classify_scale(selected_positions)}")
            print(
                "Gamme créée : "
                + " | ".join(spell_exact_scale_notes(selected_positions))
            )
            print(
                "Positions chromatiques actives : "
                + ", ".join(str(position + 1) for position in selected_positions)
            )
            if matches:
                definitions = {}
                for match in matches:
                    definition_key = (
                        match.formula,
                        match.mode_name,
                        match.tonic_degree,
                        match.added_notes,
                        match.removed_degrees,
                        match.modal_weight,
                        match.major_seventh,
                    )
                    definitions.setdefault(definition_key, []).append(
                        match.dictionary
                    )
                print(
                    "\nDéfinitions cataloguées contenant ces positions "
                    "(septième majeure prioritaire, puis poids modal)"
                )
                print(f"Définitions distinctes : {len(definitions)}")
                definition_rows = []
                for (
                    formula,
                    mode_name,
                    tonic_degree,
                    added_notes,
                    removed_degrees,
                    modal_weight,
                    major_seventh,
                ), dictionaries in definitions.items():
                    added = ", ".join(added_notes) or "aucun"
                    removed = ", ".join(map(str, removed_degrees)) or "aucun"
                    seventh = "7e majeure" if major_seventh else "7e non majeure"
                    definition_rows.append(
                        (
                            formula,
                            mode_name,
                            f"degré {tonic_degree}",
                            added,
                            removed,
                            ", ".join(dictionaries),
                            str(modal_weight),
                            seventh,
                        )
                    )
                for line in format_catalog_definition_table(definition_rows):
                    print(line)
            if not matches:
                print("Aucune correspondance classic/physic trouvée.")
            print("=" * 72)
            return

        mod_use = source_formula

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
        (lineno(), "\n  FOR Fonction mode:", module, type(module), "\n dic_gam:", dic_gam)

    major_mode_dictionary = {}
    # Le mode majeur doit être calculé à partir de la formule effective de la tonique
    # choisie, pas seulement à partir de la formule générique majeure (101...).
    # Cela permet d’appliquer correctement le cas G+ puis +4, où la tonique signée
    # change la structure de la gamme de référence.
    for base_formula in (maj_form, mod_use):
        if not base_formula:
            continue
        if base_formula not in dic_gam:
            mode(base_formula)
        for mode_index, major_mode in enumerate(dic_gam.get(base_formula, [])):
            major_mode_dictionary[major_mode[0]] = (deg_rom[mode_index], major_mode[1])

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
        (lineno(), "gam_util:", gam_util)
        major_scale_dictionary.setdefault((note_dia, str(note_sig), mod_use), {
            "formula": mod_use,
            "notes": gam_util.copy(),
        })
        fou = 0
        for cle in dic_gam[mod_use]:
            ind_clefs = dic_gam[mod_use].index(cle)
            deg_gam = ind_clefs
            clef = cle[1]
            classic_physic[clef] = []
            gam_util2 = gam_util.copy()
            (lineno(), "* mod_use:", mod_use, "gam_util:", gam_util)
            (lineno(), "deg_rom[deg_gam]:", deg_rom[deg_gam], deg_gam, "ind_clefs:", ind_clefs)
            if cle[1] in cle_classic:
                (lineno(), "cle[1]:", cle[1], "cle_classic:", cle_classic[cle_classic.index(cle[1])],
                    cle_classic.index(cle[1]), gam_util)
                job = cle_classic.index(cle[1])
                app = ModalResult(
                    list(pre_classic[cle_classic[job]]), "classic", cle_classic[job],
                    deg_rom[deg_gam], gam_util2, cle[0], mod_use,
                )
                classic_physic[clef].append(app)
                (lineno(), "___ cle_classic: ", app[2], app[0], "job:", job, fou, "\n* gam_util:", gam_util)
            if cle[1] in cle_physic:
                (lineno(), "cle[1]:", cle[1], "cle_physic:", cle_physic[cle_physic.index(cle[1])],
                    cle_physic.index(cle[1]), gam_util)
                job = cle_physic.index(cle[1])
                app = ModalResult(
                    list(pre_physic[cle_physic[job]]), "physic", cle_physic[job],
                    deg_rom[deg_gam], gam_util2, cle[0], mod_use,
                )
                classic_physic[clef].append(app)
                (lineno(), "___ cle_physic:  ", app[2], app[0], "job:", job, fou, "\n* gam_util:", gam_util)
            fou += 1
            if not classic_physic[clef]:
                del classic_physic[clef]
            else:
                (lineno(), "classic_physic[clef]:", classic_physic[clef], "clef:", clef)
        (lineno(), "classic_physic[clef]:", classic_physic)

    def analog_notes(formula, source_formula, source_notes):
        """Reconstruit les notes analogiques à partir d'une formule énumérée."""
        notes_by_degree = {
            degree: note
            for degree, note in zip(
                (item for item in source_formula if item != "0"), source_notes
            )
        }
        return [notes_by_degree[degree] for degree in formula if degree != "0"]

    # Fonctionnalités ☺
    tonic_formula = mod_use
    if mod_use:  # "mod_use", généralement présent d’entrée.
        dic_gam[mod_use] = []
        mode(mod_use)
        gam_util.clear()
        gamme()
        tonic_formula = mod_use
        (lineno(), "* mod_use:", mod_use, "gam_util:", gam_util)
        (lineno(), "dic_gam:", dic_gam[mod_use])
        (lineno(), "cle_classic:", cle_classic[0], "\ncle_physic:", cle_physic[0])
        (lineno(), "classic_physic[clef]:", classic_physic, "\n")
    if tab_key:  # "tab_key", utilisé pour traiter plusieurs choix de gammes.
        for m_u in tab_key:
            mod_use = m_u
            mode(mod_use)
            gam_util.clear()
            gamme()
            (lineno(), "*** mod_use:", mod_use, "gam_util:", gam_util)
            (lineno(), "dic_gam:", dic_gam[mod_use])
            (lineno(), "classic_physic[clef]:", classic_physic, "\n")
    (lineno(), "tab_key:", tab_key)
    (lineno(), "dic_gam:", dic_gam.keys(), "\n** classic_physic:", classic_physic.keys())

    # Clarification du dictionnaire 'classic_physic'
    cumul_rangs, cumul_rangs2, gam_mix = [], [], []
    for cp in classic_physic.keys():
        nom_rng2 = nom_typ2 = nom_num2 = num_deg2 = not_gam2 = ""
        var_cp = classic_physic[cp]
        nom_rng = var_cp[0][0]
        nom_typ = var_cp[0][1]
        nom_num = var_cp[0][2]
        num_deg = var_cp[0][3]
        not_gam = var_cp[0][4]
        (lineno(), "*** var_cp *** :", cp, var_cp, "[0][4]")
        if len(var_cp) == 2:
            nom_rng2 = var_cp[1][0]
            nom_typ2 = var_cp[1][1]
            nom_num2 = var_cp[1][2]
            num_deg2 = var_cp[1][3]
            not_gam2 = var_cp[1][4]
            (lineno(), "*** var_cp *** :", cp, var_cp, "[1][4]")
        if len(var_cp) < 2:
            ("len1", lineno(), "nom_rng:", nom_rng, nom_typ, nom_num, num_deg, not_gam)
        else:
            for vc in range(len(var_cp)):
                (lineno(), "nom_rng:", nom_rng, nom_typ, nom_num, num_deg, not_gam)
                (lineno(), "nom_rng2:", nom_rng2, nom_typ2, nom_num2, num_deg2, not_gam2)
                (lineno(), "vc:", vc, "*** var_cp *** :", var_cp[vc])
                (lineno(), "vc:", vc, "len(var_cp):", len(var_cp), "var_cp:", var_cp)
        if nom_rng == nom_rng2 and nom_rng not in cumul_rangs:  # Les types classic et physic sont égaux.
            cum_app = nom_rng, nom_typ
            cumul_rangs.append(cum_app)
            i_rom = deg_rom.index(num_deg)
            # j_rom = 7 - i_rom # Obtenir le rang_degré de la tonique.
            gam_mix = not_gam[i_rom:] + not_gam[:i_rom]
            cum_app = "Mixtes", nom_rng
            gam_mix.append(cum_app)
            debug_log(lineno(), "Mixtes:", gam_mix[:7], gam_mix[7], "cp:", cp)
            if cp in dic_gam.values():
                (lineno(), "CP dic_gam:", dic_gam.values())
        elif nom_rng not in cumul_rangs2:  # Les types classic et physic sont différents.
            cumul_rangs2.append(nom_rng)
            i_rom = deg_rom.index(num_deg)
            # j_rom = 7 - i_rom # Obtenir le rang_degré de la tonique.
            gam_mix = not_gam[i_rom:] + not_gam[:i_rom]
            cum_app = nom_typ, nom_rng
            gam_mix.append(cum_app)
            debug_log(lineno(), "Séries:", gam_mix[:7], gam_mix[7], "cp:", cp)
        elif nom_rng2 not in cumul_rangs2:
            cum_app = nom_rng2, nom_typ2
            cumul_rangs2.append(cum_app)
            i_rom = deg_rom.index(num_deg2)
            # j_rom = 7 - i_rom # Obtenir le rang_degré de la tonique.
            gam_mix = not_gam2[i_rom:] + not_gam2[:i_rom]
            cum_app = nom_typ2, nom_rng2
            gam_mix.append(cum_app)
            debug_log(lineno(), "Séries2:", gam_mix[:7], gam_mix[7], "cp:", cp)
    (lineno(), "cumul_rangs:", cumul_rangs)
    (lineno(), "cumul_rangs2:", cumul_rangs2)

    note_label = "" if note_sig in (None, "", "0", 0) else str(note_sig)
    print("\n" + "=" * 72)
    print("RÉSULTAT DE LA RECHERCHE")
    print("=" * 72)
    print(f"Tonique : {note_label}{note_dia}")
    print(f"Formule : {mod_use}")
    display_results = []
    for formula, results in classic_physic.items():
        for result in results:
            mode_notes = analog_notes(
                result.reference_formula, result.source_formula, result.notes
            )
            if not require_seven_notes or len(mode_notes) == 7:
                display_results.append((formula, result, mode_notes))

    display_scale = gam_util and (not require_seven_notes or len(gam_util) == 7)
    if display_scale:
        print(f"Gamme : {' | '.join(gam_util)}")
        print(f"Type : {classify_scale(gam_util)}")
    else:
        if require_seven_notes:
            print("Gamme : aucune note correspondant au filtre")
        else:
            print("Gamme : aucune note reconstruite")
    displayed_formulas = {entry[0] for entry in display_results}
    print(f"Formes modales trouvées : {len(displayed_formulas)}")
    if tab_key:
        print(f"Formules candidates : {len(tab_key)}")
    if require_seven_notes and not display_results:
        print("Aucune forme modale ne correspond au filtre des 7 notes.")
    if display_results:
        print("\nFORMES MODALES TROUVÉES")
        tonic_match_found = False
        tonic_rows, non_tonic_rows = {}, {}
        for formula, result, mode_notes in display_results:
            reference_formula = result.reference_formula
            target_degree = result.degree
            degree_index = deg_rom.index(target_degree)

            rotated_notes = mode_notes[degree_index:] + mode_notes[:degree_index]
            mode_name = result.mode_info[0]
            dictionary_name = result.dictionary

            is_tonic_mode = (
                dictionary_name in ("classic", "physic")
                or rotated_notes[0] == note_dia
                or rotated_notes[0].endswith(note_dia)
            )
            if is_tonic_mode:
                tonic_match_found = True
                tonic_rows.setdefault(
                    (
                        " | ".join(rotated_notes),
                        reference_formula,
                        f"degré I : {rotated_notes[0]} {mode_name or '?'}",
                    ),
                    [],
                ).append(dictionary_name)
                if result.source_formula != reference_formula:
                    requested_entry = (
                        pre_classic.get(result.source_formula)
                        or pre_physic.get(result.source_formula)
                    )
                    requested_name = (
                        requested_entry[0] if requested_entry
                        else MODE_NAMES.get(result.source_formula, '?')
                    )
                    non_tonic_rows.setdefault(
                        (
                            " | ".join(result.notes),
                            result.source_formula,
                            f"degré {target_degree} : {result.notes[0]} "
                            f"{requested_name}",
                        ),
                        [],
                    ).append(dictionary_name)
            elif target_degree != "I":
                non_tonic_rows.setdefault(
                    (
                        " | ".join(rotated_notes),
                        reference_formula,
                        f"degré {target_degree} : {rotated_notes[0]} "
                        f"{mode_name or '?'}",
                    ),
                    [],
                ).append(dictionary_name)
        if tonic_match_found:
            table_rows = [
                (*key, ", ".join(dict.fromkeys(dictionaries)))
                for key, dictionaries in (
                    *tonic_rows.items(), *non_tonic_rows.items()
                )
            ]
            print(format_modal_table(table_rows))
        elif display_scale:
            tonic_name = pre_classic.get(mod_use, pre_physic.get(mod_use, [
                MODE_NAMES.get(mod_use, "non référencé")
            ]))[0]
            print(format_modal_table([(
                " | ".join(gam_util),
                mod_use,
                f"degré I : {gam_util[0]} {tonic_name}",
                "construction",
            )]))
    print("=" * 72)


if __name__ == '__main__':
    import inspect
    from typing import Callable

    '# lineno() Pour consulter le programme grâce au suivi des prints lors du mode debug'
    lineno: Callable[[], str] = lambda: (inspect.currentframe().f_back.f_lineno if DEBUG else '')

    cli_main()
