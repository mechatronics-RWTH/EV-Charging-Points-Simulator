
from typing import List
from SimulationModules.ParkingArea.Parking_Area import ParkingSpot
from SimulationModules.ParkingArea.Parking_Area import ParkingPath, Field
from SimulationModules.ParkingArea.Parking_Area import Obstacle
from SimulationModules.ParkingArea.Parking_Area import GiniChargingSpot
import numpy as np
from collections import deque, namedtuple
#from pyvis.network import Network

def pa_as_graph(parking_area):
    '''
    We want to convert the ParkingArea, which is an Array atm,
    into a graph to use pathfinding and costfunctions
    '''
    xs = np.arange(0, parking_area.parking_area_size[0] + 1, 1, dtype=int)
    ys = np.arange(0, parking_area.parking_area_size[1] + 1, 1, dtype=int)
    #we save the graph as namedtuple, with spots as nodes and their links 
    #as edges
    graph= namedtuple("Graph",["nodes", "edges"])
    nodes=[]
    edges=[]
    #at first, we add all fields as nodes
    for i, x in enumerate(xs[:-1]):
            for j, y in enumerate(ys[:-1]):
                nodes.append(parking_area._get_field_by_position([x, y]))

    #after that, we add an edge from all fields to all their neighbours,
    #if that makes sense
    for i, x in enumerate(xs[:-1]):
            for j, y in enumerate(ys[:-1]):

                        if x>0:
                            connect_if_possible(parking_area, edges, [x, y],[x-1, y])
                            connect_if_possible(parking_area, edges, [x-1, y],[x, y])
                        if y>0:
                            connect_if_possible(parking_area, edges, [x, y],[x, y-1])
                            connect_if_possible(parking_area, edges, [x, y-1],[x, y])
                        if x<len(xs)-2:
                            connect_if_possible(parking_area, edges, [x, y],[x+1, y])
                            connect_if_possible(parking_area, edges, [x+1, y],[x, y])
                        if y<len(ys)-2:
                            connect_if_possible(parking_area, edges, [x, y],[x, y+1])
                            connect_if_possible(parking_area, edges, [x, y+1],[x, y])

    #we remove duplicates from the edges
    edges=list(set(edges))
    return graph(nodes, edges)

def connect_if_possible(parking_area, edges: list, pos1: List[int], pos2: List[int]):
    '''
    this methode connects two nodes (fields) if necessary depending on their type.
    we dont avoid duplicates in this method
    '''
    node1=parking_area._get_field_by_position(pos1)
    node2=parking_area._get_field_by_position(pos2)
    #if one of the fields is an Obstacle, there will be no connection
    if isinstance(node1, Obstacle) or isinstance(node2, Obstacle):
        return
    #All other kinds of fields can be connected to a neighboured ParkingPath
    if isinstance(node1, ParkingPath) or isinstance(node2, ParkingPath):
        #an edge consists of a start- and end node and a weight
        edges.append((node1, node2,node2.cost))

'''
#this method can be used to visualize the developed graph
def show(graph, output_filename):
    g=Network()
    tilesize=40
    for node in graph.nodes:
        label="("+str(node.position[0])+","+str(node.position[1])+")"
        pos_x=node.position[0]*tilesize
        pos_y=node.position[1]*tilesize
        col=node.color
   
        g.add_node(label, size=10,x=pos_x, y=pos_y,physics=True, color=col)
    for edge in graph.edges:
        label1="("+str(edge[0].position[0])+","+str(edge[0].position[1])+")"
        label2="("+str(edge[1].position[0])+","+str(edge[1].position[1])+")"
        #logger.info("made edge from "+label1+" to "+label2)
        g.add_edge(label1,label2)
    
    g.toggle_physics(False)
    g.width = "100%"
    g.height = "100%"
    g.show(output_filename)
    return g
'''


def dijkstra_distance(graph, start, goal):
    '''
    this method can find the shortest traveldistance 
    between two nodes in a graph
    '''
    #in dists, we see the shortest distance from start node to every node,
    #in handled, we see if they are already handles  
    dists={node: float('infinity') for node in graph.nodes}
    handled={node: False for node in graph.nodes}
    dists[start]=0
    #chosen is the node were now looking at
    while not all(value for value in handled.values()):
        #we make a list with all unhandled nodes 
        unhandled_nodes = [node for node, is_handled in handled.items() if not is_handled]
        #now we filter dists for all unhandled nodes
        filtered_dists = {node: dists[node] for node in unhandled_nodes}
        #from those we take the one with lowest distance
        chosen = min(filtered_dists, key=lambda k: filtered_dists[k])     
        for edge in graph.edges:
            if edge[0]==chosen:
                dists[edge[1]]=min(edge[2]+dists[edge[0]],dists[edge[1]])
                
        handled[chosen]=True
        #logger.info(handled)        

    return dists[goal]

def dijkstra_distances(graph, start: Field):
    '''
    this method can find the shortest travel distances 
    between the start node and every other node in a graph
    '''
    #in dists, we see the shortest distance from start node to every node,
    #in handled, we see if they are already handles  
    dists={node: float('infinity') for node in graph.nodes}
    handled={node: False for node in graph.nodes}
    dists[start]=0
    #chosen is the node were now looking at
    while not all(value for value in handled.values()):
        #we make a list with all unhandled nodes 
        unhandled_nodes = [node for node, is_handled in handled.items() if not is_handled]
        #now we filter dists for all unhandled nodes
        filtered_dists = {node: dists[node] for node in unhandled_nodes}
        #from those we take the one with lowest distance
        chosen = min(filtered_dists, key=lambda k: filtered_dists[k])     
        for edge in graph.edges:
            if edge[0]==chosen:
                dists[edge[1]]=min(edge[2]+dists[edge[0]],dists[edge[1]])
                
        handled[chosen]=True
        #logger.info(handled)        

    return dists

