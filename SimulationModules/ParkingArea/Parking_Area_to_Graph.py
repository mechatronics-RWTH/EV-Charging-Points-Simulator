
from typing import List, Tuple
from SimulationModules.ParkingArea.ParkingAreaElements.InterfaceField import InterfaceField
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingPath
from SimulationModules.ParkingArea.ParkingAreaElements.Obstacle import Obstacle
from dataclasses import dataclass
import numpy as np
from collections import deque, namedtuple

EDGE_WEIGHT=1


class Graph:
    def __init__(self):
        self.nodes: List[InterfaceField] = []
        self.edges: List[Tuple[InterfaceField, InterfaceField, float]] =[]

    def add_edge(self, start: InterfaceField, end: InterfaceField, weight: float):
        self.edges.append((start, end, weight))

    def add_node(self, node: InterfaceField):
        self.nodes.append(node)

    def assign_nodes(self, nodes: List[InterfaceField]):
        self.nodes = nodes

    def create_edges(self):
        for node in self.nodes:
            direct_neighbours = self.get_direct_neighbors(node)
            for neighbour in direct_neighbours:
                self.connect_if_possible(node, neighbour)

    def connect_if_possible(self, node1, node2):
        if isinstance(node1, Obstacle) or isinstance(node2, Obstacle):
            return
        #All other kinds of fields can be connected to a neighboured ParkingPath
        if isinstance(node1, ParkingPath) or isinstance(node2, ParkingPath):
        #an edge consists of a start- and end node and a weight
            self.add_edge(start=node1, end=node2, weight=EDGE_WEIGHT)


    def get_direct_neighbors(self, current_node: InterfaceField):
        return [node for node in self.nodes if self.get_position_distance_of_nodes(current_node, node) == 1]

    def get_position_distance_of_nodes(self, node1, node2):
        return np.linalg.norm(np.array(node1.position) - np.array(node2.position))


    

def determine_distances_for_indices(parking_area):
    area_size = len(parking_area.parking_area_fields)
    graph = Graph()
    graph.assign_nodes(parking_area.parking_area_fields)
    graph.create_edges()
    #distances_for_indexes is an array with all dijkstra distances for all pairs of Fieldindices
    distances_for_fields=[dijkstra_distances(graph, node) for node in graph.nodes]
    distances_for_indices=np.zeros([area_size,area_size])
    for i in range(area_size):
        for j in range(area_size):
            distance_from_field_with_index_i=distances_for_fields[i]
            distances_for_indices[i,j]=distance_from_field_with_index_i[parking_area._get_field_by_index(j)]

    return distances_for_indices
   

#TODO: Not sure if I want that here, if it is just 
def get_field_from_parking_area_by_position(parking_area,
                                             position: List[int]) -> InterfaceField:

    field: InterfaceField = next((field for field in parking_area.parking_area_fields if position == field.position), None)
    if field is None:
        raise ValueError(f"Field with position: {position} not found")
    else:
        return field 

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
    for field in parking_area.parking_area_fields:
        graph.add_node(field)
    
    for node in graph.nodes:
        graph.get_neighbors(node)

    for i, x in enumerate(xs[:-1]):
            for j, y in enumerate(ys[:-1]):
                nodes.append(get_field_from_parking_area_by_position(parking_area=parking_area, position=[x, y]))

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

def connect_if_possible(parking_area, 
                        edges: list, 
                        pos1: List[int], 
                        pos2: List[int]):
    '''
    this methode connects two nodes (fields) if necessary depending on their type.
    we dont avoid duplicates in this method
    '''
    node1=get_field_from_parking_area_by_position(parking_area=parking_area,position= pos1)
    node2=get_field_from_parking_area_by_position(parking_area=parking_area,position= pos2)
    #if one of the fields is an Obstacle, there will be no connection
    if isinstance(node1, Obstacle) or isinstance(node2, Obstacle):
        return
    #All other kinds of fields can be connected to a neighboured ParkingPath
    if isinstance(node1, ParkingPath) or isinstance(node2, ParkingPath):
        #an edge consists of a start- and end node and a weight
        edges.append((node1, node2,EDGE_WEIGHT))

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

def dijkstra_distances(graph, start: InterfaceField):
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

