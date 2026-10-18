"""Reference tables for ModalDevel's degree and alteration rules."""

DEGREE_SIGNATURES = {
    "2": ["-2", "2", "+2", "x2", "^2", "+^2"],
    "3": ["o3", "-3", "3", "+3", "x3", "^3"],
    "4": ["o4", "-4", "4", "+4", "x4", "^4"],
    "5": ["*5", "o5", "-5", "5", "+5", "x5"],
    "6": ["-*6", "*6", "o6", "-6", "6", "+6"],
    "7": ["o*7", "-*7", "*7", "o7", "-7", "7"],
}

CHROMATIC_SIGNATURES = {
    0: ["1"],
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
    11: ["7"],
}

ALT_ACTIVITY = (
    ("x2", "+3", "+4"),
    ("^2", "x3", "x4", "+5"),
    ("+^2", "^3", "^4", "x5", "+6"),
    ("+3", "+4"),
    ("x3", "x4", "+5"),
    ("^3", "^4", "x5", "+6"),
    ("x4", "+5"),
    ("^4", "x5", "+6"),
    ("x5", "+6"),
    ("o*7", "-*6", "*5", "o4", "o3", "-2"),
    ("-*7", "*6", "o5", "-4", "-3"),
    ("*7", "o6", "-5"),
    ("o7", "-6"),
    ("-*6", "*5", "o4", "o3", "-2"),
    ("*6", "o5", "-4", "-3"),
    ("o6", "-5"),
    ("*5", "o4", "o3", "-2"),
    ("o5", "-4", "-3"),
    ("o4", "o3", "-2"),
    ("-4", "-3"),
    ("o3", "-2"),
)

ASCENDING_SIGNS = [
    "", "+", "x", "^", "+^", "x^", "^^", "+^^", "x^^", "^^^",
    "+^^^", "x^^^", "^^^^", "+^^^^", "x^^^^", "^^^^^", "+^^^^^",
    "x^^^^^", "^^^^^^", "+^^^^^^", "x^^^^^^", "^^^^^^^", "+^^^^^^^",
    "x^^^^^^^", "^^^^^^^^",
]
DESCENDING_SIGNS = [
    "", "-", "o", "*", "-*", "o*", "**", "-**", "o**", "***",
    "-***", "o***", "****", "-****", "o****", "*****", "-*****",
    "o*****", "******", "-******", "o******", "*******", "-*******",
    "o*******", "********",
]
DIATONIC_POSITIONS = {"2": 2, "3": 4, "4": 5, "5": 7, "6": 9, "7": 11}


def alteration_value(sign):
    """Convertit un signe composé en force altéractive."""
    positive = {"+": 1, "x": 2, "^": 3}
    negative = {"-": -1, "o": -2, "*": -3}
    return sum(positive.get(symbol, negative.get(symbol, 0)) for symbol in sign)


def sign_for_value(value):
    """Retourne l'écriture canonique d'une force altéractive."""
    if value > 0:
        return ASCENDING_SIGNS[min(value, len(ASCENDING_SIGNS) - 1)]
    if value < 0:
        return DESCENDING_SIGNS[min(abs(value), len(DESCENDING_SIGNS) - 1)]
    return ""


def classify_scale(notes):
    """Classe une gamme selon le nombre de notes distinctes."""
    cardinality = len(notes)
    names = {
        1: "monotonique",
        2: "bitonique",
        3: "tritonique",
        4: "tétratonique",
        5: "pentatonique",
        6: "hexatonique",
        7: "heptatonique",
        8: "octotonique",
    }
    return names.get(cardinality, f"{cardinality}-tonique")


def alteration_strengths(selected_parts):
    """Retourne le rang normalisé des choix dans leurs chaînes d'activité."""
    strengths = {}
    for chain in ALT_ACTIVITY:
        denominator = sum(range(1, len(chain) + 1))
        for position, item in enumerate(chain):
            if item in selected_parts:
                rank = len(chain) - position
                strengths[item] = max(strengths.get(item, 0.0), rank / denominator)
    return strengths


def modal_state_parts(selected_parts):
    """Construit l'état diatonique complet affiché pour les degrés 1 à 7."""
    values = {degree: 0 for degree in "234567"}
    direct_signs = {}
    direct_order = []
    for part in selected_parts:
        degree = part[-1]
        value = alteration_value(part[:-1])
        position = DIATONIC_POSITIONS[degree] + value
        for previous_degree in direct_order:
            previous_position = DIATONIC_POSITIONS[previous_degree] + values[previous_degree]
            if previous_position == position:
                values[previous_degree] = 0
                direct_signs.pop(previous_degree, None)
        values[degree] = value
        direct_signs[part[-1]] = part[:-1]
        direct_order.append(degree)

    applied_propagations = set()
    pending_sources = list(direct_signs.items())
    while pending_sources:
        degree, requested_sign = pending_sources.pop(0)
        source = requested_sign + degree
        for chain in ALT_ACTIVITY:
            if source not in chain[:-1]:
                continue
            for propagated in chain[chain.index(source) + 1:]:
                propagation = (source, propagated)
                if propagation in applied_propagations:
                    continue
                applied_propagations.add(propagation)
                values[propagated[-1]] += alteration_value(propagated[:-1])
                propagated_degree = propagated[-1]
                if propagated_degree in direct_signs:
                    updated_source = sign_for_value(values[propagated_degree]) + propagated_degree
                    if updated_source != direct_signs[propagated_degree] + propagated_degree:
                        pending_sources.append((propagated_degree, sign_for_value(values[propagated_degree])))

    parts = ["1"]
    for degree in "234567":
        parts.append(sign_for_value(values[degree]) + degree if values[degree] else degree)
    return parts
