import pdb
from py2neo import Graph
from py2neo.matching import *

"""
docker run --publish=7474:7474 --publish=7687:7687 --volume=$HOME/neo4j/data:/data --env='NEO4JLABS_PLUGINS=["apoc", "n10s"]' --env=NEO4J_AUTH=none neo4j:latest
"""

# g = Graph("bolt://localhost:7687", user="neo4j", password="neo")
g = Graph("bolt://localhost:7687")
try:
    g.run('CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE')
except Exception:
    print("Unique Constrain on r:Resource already exists")


graph_config = g.run('call n10s.graphconfig.show()').data()
handleRDFTypes = [c for c in graph_config if c.get('param') == 'handleRDFTypes']

# if len(handleRDFTypes) == 1 and handleRDFTypes[0].get('value') == 'LABELS':
#     pass
# else:
#    g.run('call n10s.graphconfig.init()')

g.run('MATCH (n) DETACH DELETE n')
g.run('call n10s.graphconfig.drop')
# g.run('call n10s.graphconfig.init({handleVocabUris: "IGNORE", handleMultival: "ARRAY"})')
g.run("call n10s.graphconfig.init({handleVocabUris: 'SHORTEN_STRICT'})")

# # Is this necessary?
# load_brick_1_1_ontology = 'CALL n10s.onto.import.fetch("https://brickschema.org/schema/1.1/Brick.ttl", "Turtle", {addResourceLabels: true, typesToLabels: true});'
# # load_brick_1_0_3_ontology = 'CALL n10s.onto.import.fetch("https://brickschema.org/schema/1.0.3/Brick.ttl", "Turtle", {addResourceLabels: "true", typesToLabels: "true"});'

# load_brick_results = g.run(load_brick_1_1_ontology).data()

# How to preview import...
# stream_triples = 'CALL n10s.rdf.stream.fetch("https://github.com/neo4j-labs/neosemantics/raw/3.5/docs/rdf/nsmntx.ttl","Turtle");'
# results = g.run(stream_triples)

# This works. . . 
# import_brick_example = 'CALL n10s.rdf.import.fetch("https://raw.githubusercontent.com/BrickSchema/brick-server/master/examples/data/bldg.ttl", "Turtle");'
# results = g.run(import_brick_example).data()

# TODO why doesn't this work? umm duh it's not on the docker image...
# stream_triples = 'CALL n10s.rdf.stream.fetch("file:///Users/liam/spectral_work_1/Brick/examples/custom_brick_v103_sample_graph.ttl","Turtle");'
# results = g.run(stream_triples)
# pdb.set_trace()


# This works... 
import_custom_example = 'CALL n10s.rdf.import.fetch("https://raw.githubusercontent.com/iamliamc/Brick/personal-experiments/examples/custom_brick_v103_sample_graph.ttl", "Turtle");'
results = g.run(import_custom_example).data()

nodes = NodeMatcher(g)
relationships = RelationshipMatcher(g)
resources = nodes.match("Resource").all()
building = nodes.match("Building").first()
pdb.set_trace()

print(result)
pdb.set_trace()

if False:
    g.delete_all()