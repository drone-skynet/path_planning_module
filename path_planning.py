import mysql.connector
from station import Station, Edge, haversine
import networkx as nx
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

stations=[]
edges=[]
fig, ax = plt.subplots()
limitDistance = 2.0

def getStationsFromDb() :
    conn = mysql.connector.connect(
        host="localhost",
        user=db_user,
        password=db_password,
        database="drone" 
    )
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM station")

        results = cursor.fetchall()
        for row in results:
            station = Station(row[0],row[1],row[2],row[3],row[4])
            stations.append(station)
    finally:
        cursor.close()
        conn.close()
    return

def getEdgesByStations() :
    n = len(stations)
    for i in range(n):
        for j in range(i+1,n):
            edges.append(Edge(stations[i],stations[j]))
            edges.append(Edge(stations[j],stations[i]))
            if(edges[-1].weight > limitDistance) : 
                edges.pop()
                edges.pop()
    return


# 휴리스틱(좌표 -> 거리 계산)
def heuristic(n1, n2):
    (x1, y1) = n1.longitude, n1.latitude
    (x2, y2) = n2.longitude, n2.latitude
    return haversine([x1,y1], [x2,y2])


def makeGraph() :
    global G
    G = nx.DiGraph()

    for station in stations:
        #G.add_node((station.longitude, station.latitude))
        G.add_node((station))

    # 엣지 추가
    for edge in edges:
        #G.add_edge((edge.origin.longitude, edge.origin.latitude), (edge.destination.longitude, edge.destination.latitude), weight = edge.weight)
        G.add_edge(edge.origin, edge.destination, weight = edge.weight)

def visualize_graph():
    for station in stations :
        ax.scatter(station.longitude, station.latitude, s=100, color='lightblue')  # 노드 크기와 색상 설정
        ax.text(station.longitude, station.latitude, station.name, fontsize=12, ha='right')  # 노드 레이블 표시

    for edge in edges:
        x_values = [edge.origin.longitude, edge.destination.longitude]
        y_values = [edge.origin.latitude, edge.destination.latitude]
        ax.plot(x_values, y_values, color='gray', linewidth=1)  # 간선 그리기

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'stations in Seoul & edges shorter than {limitDistance}km')
    plt.show()

def searchRoute() :
    start = stations[0]
    goal = stations[13]
    path = nx.astar_path(G, start, goal, heuristic=heuristic, weight='weight')

    rsltStr=""
    for station in path :
        rsltStr += station.name+" "
    print(rsltStr)

    for index, station in enumerate(path):
        if(index < len(path)-1) :
            x_values = [path[index].longitude, path[index+1].longitude]
            y_values = [path[index].latitude, path[index+1].latitude]
            ax.plot(x_values, y_values, color='blue', linewidth=5)  # 간선 그리기


getStationsFromDb()
getEdgesByStations()

print(stations)
print(edges)

makeGraph()
searchRoute()

visualize_graph()
