import contextlib
import io
import itertools
import re
import sys
import unittest

import modalDevel
from modal_data import (
    ALT_ACTIVITY,
    CHROMATIC_SIGNATURES,
    DEGREE_SIGNATURES,
    DIATONIC_POSITIONS,
    alteration_strengths,
    alteration_value,
    classify_scale,
    modal_state_parts,
    sign_for_value,
)

_SIGN = r"(?:-\*|\+\^|o\*|[-+xo^*])"
_CHAINS = {chain[0]: chain[1:] for chain in ALT_ACTIVITY}
_ALL_SIGNS = sorted({s[:-1] for signs in DEGREE_SIGNATURES.values() for s in signs} - {""})


def _valid_signs(degree):
    return set(DEGREE_SIGNATURES[degree])


def _name_values(name):
    """Décode un nom modal : somme sur le degré, puis chaîne d'altéractivité."""
    values = {degree: 0 for degree in "234567"}
    for part in name.split("."):
        single = re.fullmatch(rf"({_SIGN})([1-7]+)", part)
        if single:
            steps = [(single.group(1), d) for d in single.group(2)]
        else:
            first, degrees, last = re.fullmatch(
                rf"({_SIGN})([1-7]{{2}})({_SIGN})", part
            ).groups()
            steps = [(first, degrees[0]), (last, degrees[1])]
        for sign, degree in steps:
            values[degree] += alteration_value(sign)
            source = sign_for_value(values[degree]) + degree
            for target in _CHAINS.get(source, ()):
                values[target[-1]] = alteration_value(target[:-1])
    return values


def _name_signs(name):
    values = _name_values(name)
    return frozenset(sign_for_value(v) + d for d, v in values.items() if v)


def _name_positions(name):
    values = _name_values(name)
    return {0} | {(DIATONIC_POSITIONS[d] + v) % 12 for d, v in values.items()}


def _part_is_canonical(part):
    """Un signe : degrés dans le sens de l'altération ; deux signes : jamais
    identiques, même sens = même règle, sens opposés = degrés croissants."""
    if part == "0":
        return True
    single = re.fullmatch(rf"({_SIGN})([1-7]+)", part)
    if single:
        sign, degrees = single.groups()
        return list(degrees) == sorted(degrees, reverse=alteration_value(sign) < 0)
    first, degrees, last = re.fullmatch(
        rf"({_SIGN})([1-7]{{2}})({_SIGN})", part
    ).groups()
    if first == last:
        return False
    if (alteration_value(first) > 0) != (alteration_value(last) > 0):
        return list(degrees) == sorted(degrees)
    return list(degrees) == sorted(degrees, reverse=alteration_value(first) < 0)


def _whole_forms():
    """Toutes les formes entières canoniques, groupées par état de signes."""
    forms = {}
    for sign in _ALL_SIGNS:
        for size in range(1, 7):
            for degrees in itertools.combinations("234567", size):
                ordered = "".join(sorted(degrees, reverse=alteration_value(sign) < 0))
                if all(sign + d in _valid_signs(d) for d in ordered):
                    name = sign + ordered
                    forms.setdefault(_name_signs(name), set()).add(name)
    for first, last in itertools.product(_ALL_SIGNS, repeat=2):
        for degrees in itertools.permutations("234567", 2):
            name = first + "".join(degrees) + last
            if (
                first + degrees[0] in _valid_signs(degrees[0])
                and last + degrees[1] in _valid_signs(degrees[1])
                and _part_is_canonical(name)
            ):
                forms.setdefault(_name_signs(name), set()).add(name)
    return forms


class ModalRuleTests(unittest.TestCase):
    def test_degree_two_supports_compound_augmented_signature(self):
        self.assertIn("+^", modalDevel.valid_signs_for_degree("2"))

    def test_ascending_chain_keeps_only_ascending_margin(self):
        self.assertEqual(
            modalDevel.available_signs_for_degree("4", ["+3"]),
            ["+", "x", "^"],
        )

    def test_descending_chain_reaches_degree_two(self):
        self.assertEqual(
            modalDevel.available_signs_for_degree("2", ["o*7"]),
            ["-"],
        )

    def test_degree_seven_is_octave_boundary_after_ascending_choice(self):
        self.assertNotIn("7", modalDevel.available_degrees(["+^2"]))
        self.assertIn("7", modalDevel.available_degrees([]))

    def test_selection_reset_identifies_previous_incompatible_choice(self):
        self.assertEqual(
            modalDevel.invalidated_parts_for_choice(["+4"], "^3"),
            ["+4"],
        )

    def test_seven_note_mode_suggests_unselected_degrees(self):
        self.assertEqual(
            modalDevel.remaining_adjustable_degrees(["+2", "o4"]),
            ["3", "5", "6", "7"],
        )

    def test_seven_note_mode_allows_replacing_but_not_adding_an_eighth_degree(self):
        selected = ["+2", "-3", "+4", "-5", "+6", "-7"]
        self.assertTrue(modalDevel.can_add_seven_note_degree(selected, "4"))
        self.assertFalse(modalDevel.can_add_seven_note_degree(selected, "8"))

    def test_formula_positions_start_with_the_major_scale_and_renumber_after_changes(self):
        self.assertEqual(
            modalDevel.formula_from_positions(modalDevel.MAJOR_FORMULA_POSITIONS),
            "102034050607",
        )
        self.assertEqual(
            modalDevel.formula_from_positions({0, 1, 4, 5, 7, 9, 11}),
            "120034050607",
        )

    def test_formula_grid_can_represent_all_twelve_positions(self):
        self.assertEqual(
            modalDevel.formula_from_positions(range(12)),
            "123456789101112",
        )

    def test_variable_cardinality_exact_search_disables_seven_note_limit(self):
        self.assertTrue(modalDevel.should_disable_seven_note_limit("0", 8))
        self.assertTrue(modalDevel.should_disable_seven_note_limit("0", 6))
        self.assertFalse(modalDevel.should_disable_seven_note_limit("0", 7))
        self.assertFalse(modalDevel.should_disable_seven_note_limit("1", 8))

    def test_result_highlight_spans_include_only_uninhibited_degrees(self):
        rows = modalDevel.format_catalog_definition_table([
            ("102034050607", "mode", "degré 1", "aucun", "3, 6", "classic, physic", "28", "7e majeure"),
        ])
        text = "\n".join(rows) + "\n"
        formula_start = text.index("102034050607")
        spans = modalDevel.uninhibited_degree_spans(text)
        highlighted_degrees = [
            text[start:end]
            for start, end in spans
        ]
        self.assertEqual(highlighted_degrees, ["1", "2", "4", "5", "7"])
        self.assertNotIn(
            (formula_start + 4, formula_start + 5),
            spans,
        )
        self.assertNotIn(
            (formula_start + 9, formula_start + 10),
            spans,
        )

    def test_catalog_definition_table_aligns_each_column(self):
        rows = modalDevel.format_catalog_definition_table([
            ("123040050607", "-34", "degré 1", "case 2: +1 / -2", "2", "classic, physic", "6", "7e majeure"),
            ("102030040567", "x45+", "degré 1", "case 11: +6 / -7", "6", "classic, physic", "33", "7e majeure"),
        ])
        separator_positions = [
            [index for index, char in enumerate(row) if char == "|"]
            for row in rows
        ]
        self.assertTrue(all(positions == separator_positions[0] for positions in separator_positions))

    def test_replacing_a_major_position_preserves_seven_selected_notes(self):
        selected = set(modalDevel.MAJOR_FORMULA_POSITIONS)
        selected.remove(4)
        selected.add(3)
        formula = modalDevel.formula_from_positions(selected)
        self.assertEqual(sum(character != "0" for character in formula), 7)
        self.assertEqual(formula, "102304050607")

    def test_seven_note_mode_limits_cumulated_alterations(self):
        selected = ["-3", "x4", "-6"]
        self.assertIn(
            "+", modalDevel.available_signs_for_degree("5", selected, True)
        )
        self.assertIn("", modalDevel.available_signs_for_degree("5", selected, True))
        self.assertNotIn(
            "x5", modalDevel.available_signs_for_degree("5", selected, True)
        )
        self.assertIn("7", modalDevel.available_degrees(["x4"], True))

    def test_seven_note_mode_shifts_neighbours_instead_of_overlapping(self):
        self.assertEqual(
            modalDevel.resolve_seven_note_overlaps(["-3", "x4", "-6"], "-6"),
            ["-3", "+4", "-6"],
        )

    def test_seven_note_mode_accepts_changing_mind_after_a_forced_choice(self):
        self.assertIn("*", modalDevel.available_signs_for_degree("7", ["+^2"], True))
        self.assertEqual(
            modalDevel.available_degrees(["+^2"], True),
            ["2", "3", "4", "5", "6", "7"],
        )
        resolved = modalDevel.resolve_seven_note_overlaps(["+^2", "*7"], "*7")
        self.assertEqual(
            modal_state_parts(resolved),
            ["1", "+2", "3", "4", "-5", "o6", "*7"],
        )

    def test_requested_mode_is_reported_as_diatonic_to_its_tonic_mode(self):
        output = io.StringIO()
        original_lineno = getattr(modalDevel, "lineno", None)
        modalDevel.lineno = lambda: ""
        original_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO("C\n\n1\n-3-6\n")
            with contextlib.redirect_stdout(output):
                modalDevel.print_hi(require_seven_notes=True)
        finally:
            sys.stdin = original_stdin
            if original_lineno is None:
                del modalDevel.lineno
            else:
                modalDevel.lineno = original_lineno
        self.assertIn("degré III : C -36", output.getvalue())
        self.assertIn("degré I : -E +5", output.getvalue())

    def test_invalid_scale_input_reports_no_result_instead_of_eof(self):
        output = io.StringIO()
        original_lineno = getattr(modalDevel, "lineno", None)
        modalDevel.lineno = lambda: ""
        original_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO("C\n\n1\n-3x4-6\n")
            with contextlib.redirect_stdout(output):
                modalDevel.print_hi(require_seven_notes=True)
        finally:
            sys.stdin = original_stdin
            if original_lineno is None:
                del modalDevel.lineno
            else:
                modalDevel.lineno = original_lineno
        self.assertIn("Aucun résultat", output.getvalue())

    def test_natural_mode_weights_follow_degree_signatures(self):
        natural_positions = modalDevel.MAJOR_FORMULA_POSITIONS
        weights = []
        for tonic_position in sorted(natural_positions):
            rotated_positions = {
                (position - tonic_position) % 12
                for position in natural_positions
            }
            formula = modalDevel.formula_from_positions(rotated_positions)
            weights.append(modalDevel.modal_weight_from_formula(formula)[0])
        self.assertEqual(weights, [0, -12, -22, 5, -8, -19, -28])

    def test_natural_degrees_weigh_nothing(self):
        self.assertEqual(
            modalDevel.modal_weight_from_formula("102034050607"),
            (0, True),
        )

    def test_sharp_four_weighs_five(self):
        self.assertEqual(
            modalDevel.modal_weight_from_formula("102030450607"),
            (5, True),
        )

    def test_inhibited_catalog_weights_count_only_retained_altered_degrees(self):
        self.assertEqual(
            modalDevel.modal_weight_from_formula(
                "102034050607", {"1", "2", "4", "6", "7"}
            ),
            (0, True),
        )
        self.assertEqual(
            modalDevel.modal_weight_from_formula("102034050607", {"7"}),
            (0, True),
        )

    def test_eight_degree_inhibitions_keep_all_ranked_catalog_matches(self):
        positions = [
            position
            for position, degree in enumerate("102304056078")
            if degree != "0"
        ]
        matches = modalDevel.find_catalog_inhibition_matches(positions)
        self.assertEqual(len(matches), 16)
        self.assertEqual(matches[0].formula, "102034050607")
        self.assertEqual(matches[0].modal_weight, 0)
        self.assertTrue(matches[0].major_seventh)
        self.assertEqual(
            {match.removed_degrees for match in matches},
            {(degree,) for degree in range(1, 9)},
        )
        self.assertTrue(all(match.major_seventh for match in matches))
        self.assertEqual(
            [abs(match.modal_weight) for match in matches],
            sorted(abs(match.modal_weight) for match in matches),
        )
        self.assertEqual(
            [
                (not match.major_seventh, abs(match.modal_weight))
                for match in matches
            ],
            sorted(
                (not match.major_seventh, abs(match.modal_weight))
                for match in matches
            ),
        )

    def test_eight_note_exact_results_keep_aligned_table_and_analysis(self):
        positions = {
            position
            for position, degree in enumerate("102304056078")
            if degree != "0"
        }
        captured = io.StringIO()
        original_stdin = sys.stdin
        original_lineno = getattr(modalDevel, "lineno", None)
        modalDevel.lineno = lambda: ""
        try:
            sys.stdin = io.StringIO("C\n\n0\n")
            with contextlib.redirect_stdout(captured):
                modalDevel.print_hi(exact_formula_positions=positions)
        finally:
            sys.stdin = original_stdin
            if original_lineno is None:
                del modalDevel.lineno
            else:
                modalDevel.lineno = original_lineno
        output = captured.getvalue()
        lines = output.splitlines()
        header_index = next(
            index for index, line in enumerate(lines)
            if line.startswith("  Formule")
        )
        table_lines = [lines[header_index], *(
            line for line in lines[header_index + 1:]
            if line.startswith("- ")
        )]
        separators = [
            [index for index, character in enumerate(line) if character == "|"]
            for line in table_lines
        ]
        self.assertEqual(len(table_lines), 17)
        self.assertTrue(
            all(columns == separators[0] for columns in separators)
        )
        table_text = "\n".join(table_lines)
        highlighted_degrees = [
            table_text[start:end]
            for start, end in modalDevel.uninhibited_degree_spans(table_text)
        ]
        self.assertEqual(len(highlighted_degrees), 16 * 7)
        self.assertTrue(all(degree in "1234567" for degree in highlighted_degrees))
        self.assertIn("ANALYSE CIRCONSTANCIELLE", output)
        self.assertIn("rotation du degré source", output)

    def test_fewer_than_seven_notes_match_by_inhibiting_catalog_degrees(self):
        positions = {0, 2, 5, 9, 11}
        matches = modalDevel.find_catalog_inhibition_matches(positions)
        self.assertTrue(matches)
        self.assertTrue(all(match.inhibited_catalog for match in matches))
        self.assertEqual(len(matches[0].removed_degrees), 2)
        self.assertEqual(matches[0].modal_weight, 0)
        self.assertTrue(matches[0].major_seventh)
        major_seventh_matches = [
            match for match in matches if match.major_seventh
        ]
        other_matches = [
            match for match in matches if not match.major_seventh
        ]
        self.assertEqual(
            [match.major_seventh for match in matches],
            sorted(
                (match.major_seventh for match in matches),
                reverse=True,
            ),
        )
        self.assertEqual(len(major_seventh_matches) + len(other_matches), len(matches))
        self.assertEqual(
            [abs(match.modal_weight) for match in major_seventh_matches],
            sorted(abs(match.modal_weight) for match in major_seventh_matches),
        )
        self.assertEqual(
            [abs(match.modal_weight) for match in other_matches],
            sorted(abs(match.modal_weight) for match in other_matches),
        )

    def test_small_exact_formula_search_reports_catalog_inhibitions(self):
        positions = {0, 2, 5, 9, 11}
        captured = io.StringIO()
        original_stdin = sys.stdin
        original_lineno = getattr(modalDevel, "lineno", None)
        modalDevel.lineno = lambda: ""
        try:
            sys.stdin = io.StringIO("C\n\n0\n")
            with contextlib.redirect_stdout(captured):
                modalDevel.print_hi(exact_formula_positions=positions)
        finally:
            sys.stdin = original_stdin
            if original_lineno is None:
                del modalDevel.lineno
            else:
                modalDevel.lineno = original_lineno
        output = captured.getvalue()
        self.assertIn("Formule source : 102003000405", output)
        self.assertIn("Notes source : 5", output)
        self.assertIn("Type : pentatonique", output)
        self.assertIn(
            "Positions chromatiques actives : 1, 3, 6, 10, 12",
            output,
        )
        self.assertIn("Définitions cataloguées contenant ces positions", output)
        self.assertIn("classic, physic", output)
        self.assertNotIn("ANALYSE CIRCONSTANCIELLE", output)

    def test_hexatonic_exact_formula_reports_its_actual_cardinality(self):
        positions = {0, 2, 4, 7, 9, 11}
        captured = io.StringIO()
        original_stdin = sys.stdin
        original_lineno = getattr(modalDevel, "lineno", None)
        modalDevel.lineno = lambda: ""
        try:
            sys.stdin = io.StringIO("C\n\n0\n")
            with contextlib.redirect_stdout(captured):
                modalDevel.print_hi(exact_formula_positions=positions)
        finally:
            sys.stdin = original_stdin
            if original_lineno is None:
                del modalDevel.lineno
            else:
                modalDevel.lineno = original_lineno
        output = captured.getvalue()
        self.assertIn("Formule source : 102030040506", output)
        self.assertIn("Notes source : 6", output)
        self.assertIn("Type : hexatonique", output)
        self.assertIn("Gamme créée : C | D | E | G | A | B", output)
        self.assertIn(
            "Positions chromatiques actives : 1, 3, 5, 8, 10, 12",
            output,
        )
        self.assertIn("Définitions distinctes : 4", output)
        self.assertEqual(
            sum(line.startswith("- ") for line in output.splitlines()),
            4,
        )
        self.assertIn("| case 6: 4", output)
        self.assertIn("| classic, physic |", output)
        self.assertNotIn("ANALYSE CIRCONSTANCIELLE", output)
        self.assertNotIn("Type : heptatonique", output)

    def test_terminal_analysis_schema_shows_source_inhibition_and_catalog_match(self):
        positions = [
            position
            for position, degree in enumerate("102304056078")
            if degree != "0"
        ]
        match = modalDevel.find_catalog_inhibition_matches(positions)[0]
        analysis = modalDevel.format_catalog_match_analysis("102304056078", match)
        self.assertIn("102304056078", analysis)
        self.assertIn("inhibition des degrés source", analysis)
        self.assertIn("rotation du degré source", analysis)
        self.assertIn(match.formula, analysis)
        self.assertIn(match.dictionary, analysis)

    def test_more_than_eight_degrees_inhibits_enough_notes_for_seven(self):
        matches = modalDevel.find_catalog_inhibition_matches(range(9))
        self.assertTrue(matches)
        self.assertTrue(all(len(match.removed_degrees) == 2 for match in matches))

    def test_reference_tables_are_loaded_from_shared_data(self):
        self.assertIs(modalDevel.dic_deg, DEGREE_SIGNATURES)
        self.assertIs(modalDevel.dic_120, CHROMATIC_SIGNATURES)

    def test_scale_cardinality_is_classified(self):
        self.assertEqual(classify_scale(["C", "D", "E", "F", "G", "A"]), "hexatonique")
        self.assertEqual(classify_scale(["C", "D", "E", "F", "G", "A", "B"]), "heptatonique")

    def test_alteration_strength_is_normalized(self):
        strengths = alteration_strengths(["+3", "+4"])
        self.assertGreater(strengths["+3"], strengths["+4"])

    def test_modal_state_line_contains_propagated_degrees(self):
        self.assertEqual(modal_state_parts(["x2"]), ["1", "x2", "+3", "+4", "5", "6", "7"])
        self.assertEqual(modal_state_parts(["x2", "+5"]), ["1", "x2", "+3", "+4", "+5", "6", "7"])

    def test_repeated_degree_request_adds_altteractive_force(self):
        self.assertEqual(
            modal_state_parts(["+3", "+4"]),
            ["1", "2", "+3", "x4", "+5", "6", "7"],
        )

    def test_later_enharmonic_choice_has_priority(self):
        self.assertEqual(
            modal_state_parts(["+2", "+4", "-5"]),
            ["1", "+2", "3", "4", "-5", "6", "7"],
        )
        self.assertEqual(
            modal_state_parts(["+2", "-5", "+4"]),
            ["1", "+2", "3", "+4", "5", "6", "7"],
        )

    def test_report_names_cover_every_catalogued_formula(self):
        from modal_names import MODE_NAMES
        self.assertEqual(len(MODE_NAMES), 462)
        self.assertEqual(MODE_NAMES["102034050607"], "0")
        self.assertEqual(MODE_NAMES["120304056070"], "-7632")
        for formula in (*modalDevel.pre_classic, *modalDevel.pre_physic):
            self.assertIn(formula, MODE_NAMES)

    def test_every_mode_name_decodes_to_its_formula(self):
        from modal_names import MODE_NAMES

        for formula, name in MODE_NAMES.items():
            if name == "0":
                continue
            occupied = {i for i, c in enumerate(formula) if c != "0"}
            self.assertEqual(_name_positions(name), occupied, f"{formula} {name}")

    def test_name_degrees_follow_alteration_direction(self):
        from modal_names import MODE_NAMES

        for name in MODE_NAMES.values():
            for part in name.split("."):
                self.assertTrue(_part_is_canonical(part), name)

    def test_decimal_name_only_when_no_whole_form_exists(self):
        from modal_names import MODE_NAMES

        whole = _whole_forms()
        for name in MODE_NAMES.values():
            if name == "0":
                continue
            if "." in name:
                self.assertNotIn(_name_signs(name), whole, name)
            else:
                self.assertIn(name, whole[_name_signs(name)], name)
                shortest = min(len(form) for form in whole[_name_signs(name)])
                self.assertEqual(len(name), shortest, name)

    def test_non_tonic_mode_without_catalog_entry_uses_report_name(self):
        output = io.StringIO()
        original_lineno = getattr(modalDevel, "lineno", None)
        modalDevel.lineno = lambda: ""
        original_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO("C\n\n1\n-7-6\n")
            with contextlib.redirect_stdout(output):
                modalDevel.print_hi(require_seven_notes=True)
        finally:
            sys.stdin = original_stdin
            if original_lineno is None:
                del modalDevel.lineno
            else:
                modalDevel.lineno = original_lineno
        self.assertIn("degré IV : C -76", output.getvalue())


if __name__ == "__main__":
    unittest.main()
