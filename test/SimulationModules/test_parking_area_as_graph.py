from SimulationModules.ParkingArea.Parking_Area_to_Graph import Graph, determine_distances_for_indices
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ParkingArea.ParkingAreaElements import Field, ParkingPath
from unittest.mock import MagicMock
import pytest

@pytest.fixture
def parking_area():
    mock_parking_area= MagicMock(spec=ParkingArea)
    mock_parking_area.parking_area_fields=[]
    mock_parking_area.parking_area_size=4
    return mock_parking_area

@pytest.fixture
def graph_with_four_nodes():
    graph = Graph()
    field1 = MagicMock(spec=ParkingPath)
    field1.position = [0,0]
    field2 = MagicMock(spec=ParkingPath)
    field2.position = [0,1]
    field3 = MagicMock(spec=ParkingPath)
    field3.position = [1,0]
    field4 = MagicMock(spec=ParkingPath)
    field4.position = [1,1]
    graph.assign_nodes([field1, field2, field3, field4])
    return graph


class TestParkingAreaAsGraph:

    def test_create_graph(self,
                            ):
        graph = Graph()
        assert graph.nodes == []
        assert graph.edges == []

    def test_add_node(self):
        graph = Graph()
        field = MagicMock(spec=Field)
        graph.add_node(field)
        assert graph.nodes == [field]

    def test_add_edge(self):
        graph = Graph()
        field1 = MagicMock(spec=Field)
        field2 = MagicMock(spec=Field)
        graph.add_edge(field1, field2, 1)
        assert graph.edges == [(field1, field2, 1)]
    
    def test_assign_nodes(self):
        graph = Graph()
        field1 = MagicMock(spec=Field)
        field2 = MagicMock(spec=Field)
        graph.assign_nodes([field1, field2])
        assert graph.nodes == [field1, field2]

    def test_get_direct_neighbors(self,
                                  graph_with_four_nodes : Graph):
        neighbors = graph_with_four_nodes.get_direct_neighbors(graph_with_four_nodes.nodes[0])
        assert neighbors \
                == [graph_with_four_nodes.nodes[1], graph_with_four_nodes.nodes[2]]

    def test_get_position_distance_of_nodes(self):
        graph = Graph()
        field1 = MagicMock(spec=Field)
        field1.position = [0,0]
        field2 = MagicMock(spec=Field)
        field2.position = [0,1]
        assert graph.get_position_distance_of_nodes(field1, field2) == 1

    def test_connect_if_possible(self,
                                 ):
        graph = Graph()
        field1 = MagicMock(spec=ParkingPath)
        field1.position = [0,0]
        field2 = MagicMock(spec=ParkingPath)
        field2.position = [0,1]
        field3 = MagicMock(spec=ParkingPath)
        field3.position = [1,0]
        field4 = MagicMock(spec=ParkingPath)
        field4.position = [1,1]
        graph.assign_nodes([field1, field2, field3, field4])
        graph.connect_if_possible(field1, field2)
        assert graph.edges == [(field1, field2, 1)]

    def test_create_edges(self,
                          graph_with_four_nodes : Graph):

        graph_with_four_nodes.create_edges()
        assert len(graph_with_four_nodes.edges) == 4*2

    def test_create_edges_line_shape(self):
        graph = Graph()
        field1 = MagicMock(spec=ParkingPath)
        field1.position = [0,0]
        field2 = MagicMock(spec=ParkingPath)
        field2.position = [0,1]
        field3 = MagicMock(spec=ParkingPath)
        field3.position = [0,2]
        field4 = MagicMock(spec=ParkingPath)
        field4.position = [0,3]
        graph.assign_nodes([field1, field2, field3, field4])
        graph.create_edges()
        print(graph.edges)
        assert len(graph.edges) == 2+2*2

    def test_determine_distances_for_indices(self,
                                             parking_area):
        field1 = MagicMock(spec=ParkingPath)
        field1.position = [0,0]
        field2 = MagicMock(spec=ParkingPath)
        field2.position = [0,1]
        field3 = MagicMock(spec=ParkingPath)
        field3.position = [0,2]
        field4 = MagicMock(spec=ParkingPath)
        field4.position = [0,3]
        parking_area.parking_area_fields = [field1, field2, field3, field4]
        parking_area._get_field_by_index = lambda index: parking_area.parking_area_fields[index]
        distances = determine_distances_for_indices(parking_area)
        assert (distances == [[0, 1, 2, 3.],
                                [1, 0, 1, 2],
                                [2, 1, 0, 1],
                                [3, 2, 1, 0,]]).all()

