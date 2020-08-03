import re
import sys
import json
import rdflib
from warnings import warn
from rdflib import RDF, RDFS, Namespace, BNode, OWL

sys.path.append("..")
from bricksrc.namespaces import BRICK, SKOS  # noqa: E402


g = rdflib.Graph()
g.parse("Brick.ttl", format="turtle")

g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("brick", BRICK)
g.bind("owl", OWL)

# Grouping terms
groups = [
    ["High_", "Low_"],
    ["Highest_", "Lowest_"],
    ["On_", "Off_"],
    ["Heating_", "Cooling_"],
    ["Min_", "Max_"],
    ["Discharge_", "Supply_"],
]

# Similar constructs of these groups should be equivalent
equivalency_pairs = [
    ["Discharge_", "Supply_"],
    ["PV_", "Photovoltaic_"],
]

# Do not expect constructs involving the following
exceptions = [
    "Emergency_Power_On_System",
    "Off_Timer_Sensor",
    "Heating_Tower_Fan",
    "Max_Fresh_Air",
    "Max_Outside_Air",
    "High_Outside_Air",
    "Low_CO2",
    "High_Suction_Pressure_Alarm",
]


"""
Warn if similar constructs are missing
For example: BRICK.Supply_Hot_Water exists but BRICK.Discharge_Hot_Water doesn't
"""


def test_missing_constructs():
    missing_constructs = {}

    # For every group
    for group in groups:
        exists = set()
        expected = set()

        # For every term, find constructs made using that term
        for member in group:
            constructs = g.query(
                f"""SELECT DISTINCT ?construct WHERE {{
                      ?construct (rdfs:subClassOf|a)+ owl:Class .
                      FILTER regex(str(?construct), "{member}") .
                }}"""
            )
            for construct in constructs:
                exists.add(str(construct[0]))

                # For every other term in the group, expect a construct
                for element in group:
                    if element not in str(construct[0]):
                        expected_class = re.sub(
                            member, element, str(construct[0])
                        )

                        # Only expect constructs that make sense
                        if not any(
                            [
                                exception in expected_class
                                for exception in exceptions
                            ]
                        ):
                            expected.add(expected_class)
        missing_constructs = list(expected.difference(exists))
        missing_constructs["".join(group)] = missing_constructs

    # Remove groups that have no missing constructs
    missing_constructs = dict(
        [(k, v) for k, v in missing_constructs.items() if v]
    )

    # If there are any missing constructs, store the details on a file and throw a warning
    if missing_constructs:
        with open("tests/missing_constructs.json", "w") as fp:
            json.dump(
                missing_constructs, fp, indent=2,
            )
        warn(
            UserWarning(
                f"Missing constructs in the following group(s): {list(missing_constructs)}"
                f"For more information, see ./tests/missing_constructs.json"
            )
        )


"""
Throw assertion error if an equivalency is missing.
For example: Brick.Discharge_Air and BRICK.Supply_Air exist but are not defined as equivalent classes
"""


def test_equivalencies():
    missing_equivalencies = []
    construct_pairs = []

    # For every equivalency pair, find all the constructs
    for equivalency_pair in equivalency_pairs:
        constructs = g.query(
            f"""SELECT DISTINCT ?construct WHERE {{
                  ?construct (rdfs:subClassOf|a)+ owl:Class .
                  FILTER regex(str(?construct), "{equivalency_pair[0]}") .
            }}"""
        )
        for construct in constructs:
            equivalent_construct = re.sub(
                equivalency_pair[0], equivalency_pair[1], str(construct[0])
            )
            construct_pairs.append([construct[0], equivalent_construct])

        # Find constructs where the equivalency triple is missing
        for construct_pair in construct_pairs:
            constructs = g.query(
                f"""SELECT DISTINCT ?construct WHERE {{
                      ?construct (rdfs:subClassOf|a)+ owl:Class .
                      <{construct_pair[1]}> (rdfs:subClassOf|a)+ owl:Class .
                      FILTER NOT EXISTS {{
                            ?construct owl:equivalentClass|^owl:equivalentClass <{construct_pair[1]}> .
                      }}
                      BIND(<{construct_pair[0]}> AS ?construct)
                }}"""
            )

            # List all these pairs
            for construct in constructs:
                equivalent_construct = re.sub(
                    equivalency_pair[0], equivalency_pair[1], str(construct[0])
                )
                if str(construct[0]) != equivalent_construct:
                    missing_equivalencies.append(
                        [construct[0], equivalent_construct]
                    )

    # If there are any missing equivalencies, store the details on a file and throw an error
    with open("tests/missing_equivalencies.json", "w") as fp:
        json.dump(
            missing_equivalencies, fp, indent=2,
        )
    assert not missing_equivalencies, (
        f"{len(missing_equivalencies)} equivalencies were missing. "
        f"For more information, see ./tests/missing_equivalencies.json"
    )
