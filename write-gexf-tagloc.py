#!/usr/bin/env python

import networkx as nx
import re

from sqlalchemy.orm import join, contains_eager, joinedload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from igsql.database import Base, db_session, engine
from igsql.model import Location, Media, Tag, User

def graph_add_node(n, g, t, lat, lon):
    if t == 'media':
        if g.has_node(n.mid):
            g.node[n.mid]['weight'] += 1
        else:
            g.add_node(n.mid)
            g.node[n.mid]['label'] = n.link
            g.node[n.mid]['weight'] = 1
            g.node[n.mid]['type'] = t
            #print(n.location)
            g.node[n.mid]['latitude'] = lat
            g.node[n.mid]['longitude'] = lon
    elif t == 'tag':
        if g.has_node(n.name):
            g.node[n.name]['weight'] += 1
        else:
            g.add_node(n.name)
            g.node[n.name]['label'] = n.name
            g.node[n.name]['weight'] = 1
            g.node[n.name]['type'] = t
            g.node[n.name]['latitude'] = lat
            g.node[n.name]['longitude'] = lon

def graph_add_edge(n1, n2, g):
    if g.has_edge(n1.mid, n2.name):
        g[n1.mid][n2.name]['weight']+=1
    else:
        g.add_edge(n1.mid, n2.name)
        g[n1.mid][n2.name]['weight']=1

graph = nx.Graph()

# iterate through every tag object, storing each in t
for t in db_session.query(Tag).all():
#for t in db_session.query(Tag).join(Media).options(contains_eager(Media.location))[0:50]: #.all():
##for m in db_session.query(Media).join(Location).options(contains_eager(Media.location)).all():
    tlat_sum = 0.0
    tlon_sum = 0.0
    m_count = 0
    for m in t.media:
        try:
            mo = db_session.query(Media).filter_by(mid=m.mid).join(Location).options(contains_eager(Media.location)).one()
            #print(mo.location[0])
            tlat_sum += mo.location[0].latitude
            tlon_sum += mo.location[0].longitude
            m_count += 1
        except NoResultFound:
            pass
    try:
        tlat = tlat_sum / m_count
        tlon = tlon_sum / m_count
        #print('Tag {} - {} {}'.format(t.name, tlat, tlon))
    except ZeroDivisionError:
        continue

    # add t to the graph
    graph_add_node(t, graph, 'tag', tlat, tlon)
    # now iterate through all the media in t, storing each like in m
    for m in t.media:
        try:
            mo = db_session.query(Media).filter_by(mid=m.mid).join(Location).options(contains_eager(Media.location)).one()
            graph_add_node(m, graph, 'media', m.location[0].latitude, m.location[0].longitude)
            graph_add_edge(m, t, graph)
        except NoResultFound:
            pass

# you probably want to change this string to something meaningful too
q = 'media_tag'

# because it ends up in the file name for the GEXF output file
nx.write_gexf(graph, '{}_ig_graph.gexf'.format(q))
print('{}_ig_graph.gexf'.format(q))
