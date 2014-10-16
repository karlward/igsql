#!/usr/bin/env python

import networkx as nx
import re

from sqlalchemy.orm import join, contains_eager
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from igsql.database import Base, db_session, engine
from igsql.model import Location, Media, Tag, User

def graph_add_node(n, g, t):
    if t == 'media':
        if g.has_node(n.mid):
            g.node[n.mid]['weight'] += 1
        else:
            g.add_node(n.mid)
            g.node[n.mid]['label'] = n.link
            g.node[n.mid]['weight'] = 1
            g.node[n.mid]['type'] = t
            #print(n.location)
            g.node[n.mid]['latitude'] = n.location[0].latitude
            g.node[n.mid]['longitude'] = n.location[0].longitude
    elif t == 'user':
        if g.has_node(n.username):
            g.node[n.username]['weight'] += 1
        else:
            g.add_node(n.username)
            g.node[n.username]['label'] = n.username
            g.node[n.username]['weight'] = 1
            g.node[n.username]['type'] = t

def graph_add_edge(n1, n2, g):
    if g.has_edge(n1.mid, n2.username):
        g[n1.mid][n2.username]['weight']+=1
    else:
        g.add_edge(n1.mid,n2.username)
        g[n1.mid][n2.username]['weight']=1

graph = nx.Graph()

# iterate through every media object, storing each in m
#for m in db_session.query(Media).join(Location).options(contains_eager(Media.location))[0:500]: #.all():
for m in db_session.query(Media).join(Location).options(contains_eager(Media.location)).all():
    # add m to the graph
    graph_add_node(m, graph, 'media')
    graph_add_node(m.user, graph, 'user')
    graph_add_edge(m, m.user, graph)
    # now iterate through all the likes in m, storing each like in u
    for u in m.likes:
        graph_add_node(u, graph, 'user')
        graph_add_edge(m, u, graph)

# you probably want to change this string to something meaningful too
q = 'media_user'

# because it ends up in the file name for the GEXF output file
nx.write_gexf(graph, '{}_ig_graph.gexf'.format(q))
print('{}_ig_graph.gexf'.format(q))
