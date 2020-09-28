import pdb
from rdflib import RDF, RDFS, OWL, Namespace, Graph, Literal

# of some use: https://github.com/RDFLib/rdflib/tree/master/examples

g = Graph()

BLDG = Namespace("https://example.com/customer_1/building_1#")
g.bind("bldg", BLDG)

BRICK = Namespace("https://brickschema.org/schema/1.0.3/Brick#")
g.bind("brick", BRICK)

# # Should we use BRICK.Tag to get Spectral Timeseries Identifier in the system?
g.add((BRICK.TimeseriesUUID, RDF.type, OWL.Class))
# # We can make TimeseriesUUID a subclass of the more generic "Tag" class.
# # It is easy to change this later.
g.add((BRICK.TimeseriesUUID, RDFS.subClassOf, BRICK.Tag))

# (subject, predicate, object)
g.add((BLDG.BUILDING, RDF.type, BRICK.Building))

# Ability to add information to the nodes via a custom class...
g.add((BLDG.BUILDING, BRICK.TimeseriesUUID, Literal("UUID-1")))
print(f"The value BRICK.TimeseriesUUID on BLDG.BUILDING is {g.value(BLDG.BUILDING,BRICK.TimeseriesUUID)}")

g.add((BLDG.BLOCK_A, RDF.type, BRICK.Space))

g.add((BLDG.DISTRICT_HEATING, RDF.type, BRICK.Boiler))
g.add((BLDG.DISTRICT_HEATING, BRICK.feeds, BLDG.PRIMARY_HOT_WATER))

g.add((BLDG.PRIMARY_HOT_WATER, BRICK.isFedBy, BLDG.DISTRICT_HEATING))
g.add((BLDG.PRIMARY_HOT_WATER, RDF.type, BRICK.Water_Distribution))
g.add((BLDG.PRIMARY_COLD_WATER, RDF.type, BRICK.Water_Distribution))

g.add((BLDG.AHU_A, RDF.type, BRICK.Air_Handler_Unit))

g.add((BLDG["AHU_A.FAN_COIL"], RDF.type, BRICK.Fan_Coil_Unit))

g.add((BLDG["AHU_A.CALCULATED_SETPOINT"], RDF.type, BRICK.Air_Temperature_Setpoint))

g.add((BLDG["AHU_A.CALCULATED_SETPOINT.X1"], RDF.type, BRICK.Outside_Air_Temperature_Low_Reset_Setpoint))

g.add((BLDG["AHU_A.CALCULATED_SETPOINT.X2"], RDF.type, BRICK.Outside_Air_Temperature_High_Reset_Setpoint))
g.add((BLDG["AHU_A.CALCULATED_SETPOINT.Y1"], RDF.type, BRICK.Supply_Air_Temperature_Low_Reset_Setpoint))
g.add((BLDG["AHU_A.CALCULATED_SETPOINT.Y2"], RDF.type, BRICK.Supply_Air_Temperature_High_Reset_Setpoint))


for floor in range(9):
    g.add((BLDG[f"FLOOR_{floor}"], RDF.type, BRICK.Floor))
    g.add((BLDG.BUILDING, BRICK.hasPart, BLDG[f"FLOOR_{floor}"]))
    for sub_valve in range(3):
        g.add((BLDG[f"VAV_A_{floor}_{sub_valve}"], RDF.type, BRICK.Variable_Air_Volume_Box))
        g.add((BLDG[f"HVAC_Zone_A_{floor}_{sub_valve}"], RDF.type, BRICK.HVAC_Zone))
        g.add((BLDG[f"VAV_A_{floor}_{sub_valve}"], BRICK.feeds, BLDG[f"HVAC_Zone_A_{floor}_{sub_valve}"]))
        g.add((BLDG[f"VAV_A_{floor}_{sub_valve}.DPR"], RDF.type, BRICK.Damper))
        g.add((BLDG[f"VAV_A_{floor}_{sub_valve}.DPRPOS"], RDF.type, BRICK.Damper_Position_Setpoint))
        g.add((BLDG[f"VAV_A_{floor}_{sub_valve}.DPR"], BRICK.isControlledBy, BLDG[f"VAV_A_{floor}_{sub_valve}.DPRPOS"]))

g.add((BLDG.AHU_A, BRICK.feeds, BLDG.BLOCK_A))

g.add((BLDG["AHU_A.SUPPLY_TEMPERATURE"], RDF.type, BRICK.Supply_Air_Temperature_Sensor))
g.add((BLDG["AHU_A.CALCULATED_SETPOINT"], BRICK.isMeasuredBy, BLDG["AHU_A.SUPPLY_TEMPERATURE"]))

g.add((BLDG.AHU_A_CALCULATED_SETPOINT, BRICK.hasPoint, BLDG.AHU_A_CALCULATED_SETPOINT_X1))
g.add((BLDG.AHU_A_CALCULATED_SETPOINT, BRICK.hasPoint, BLDG.AHU_A_CALCULATED_SETPOINT_X2))
g.add((BLDG.AHU_A_CALCULATED_SETPOINT, BRICK.hasPoint, BLDG.AHU_A_CALCULATED_SETPOINT_Y1))
g.add((BLDG.AHU_A_CALCULATED_SETPOINT, BRICK.hasPoint, BLDG.AHU_A_CALCULATED_SETPOINT_Y2))

# g.parse("../Brick.ttl", format="ttl")

# basic selection
sensors = g.query(
    """SELECT ?sensor WHERE {
    ?sensor rdf:type brick:Supply_Air_Temperature_Sensor
}"""
)

def display_subject_results(subject, results):
    for row in results:
        import pdb; pdb.set_trace()
        print(f"Subject {subject} -> Predicate {row.p} -> Object {row.o}")


display_subject_results("bldg:DISTRICT_HEATING", g.query("SELECT ?p ?o {bldg:DISTRICT_HEATING ?p ?o}"))
import pdb; pdb.set_trace()

# building = g.query("""SELECT ?building WHERE {?building rdf:type brick:Building}""")
# boiler = g.query("""SELECT ?boiler WHERE {?boiler rdf:type brick:Boiler}""")

res = g.query(
            """
                SELECT ?s WHERE { 
                    ?s brick:isFedBy bldg:DISTRICT_HEATING . 
                    ?s rdf:type brick:Water_Distribution
                }
            """
        )


for row in res:
    print(row.s)

"""
We can "serialize" this model to a file if we want to load it into another program.
"""
with open("custom_brick_v103_sample_graph.ttl", "wb") as f:
    # the Turtle format strikes a balance beteween being compact and easy to read
    f.write(g.serialize(format="ttl"))
