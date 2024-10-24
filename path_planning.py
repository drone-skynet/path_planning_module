import mysql.connector
from objects import Station, Edge, Drone, haversine
from intersection_finding import find_all_intersections
import networkx as nx
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import time
from collision_check import check_all_collision

load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

stations=[]
edges=[]
drones=[]
intersections=[]
fig, ax = plt.subplots()
limitDistance = 2.0

def get_stations_from_db() :
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

def get_edges_by_stations() :
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


def make_graph() :
    global G
    G = nx.DiGraph()

    for station in stations:
        #G.add_node((station.longitude, station.latitude))
        G.add_node(station)

    # 엣지 추가
    for edge in edges:
        #G.add_edge((edge.origin.longitude, edge.origin.latitude), (edge.destination.longitude, edge.destination.latitude), weight = edge.weight)
        G.add_edge(edge.origin, edge.destination, weight = edge.weight)

def visualize_graph():
    for station in stations :
        ax.scatter(station.longitude, station.latitude, s=100, color='lightblue')  # 노드 크기와 색상 설정
        ax.text(station.longitude, station.latitude, "", fontsize=12, ha='right')  # 노드 레이블 표시

    for edge in edges:
        x_values = [edge.origin.longitude, edge.destination.longitude]
        y_values = [edge.origin.latitude, edge.destination.latitude]
        ax.plot(x_values, y_values, color='gray', linewidth=1)  # 간선 그리기

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'stations in Seoul & edges shorter than {limitDistance}km')
  #  plt.ion() # 인터렉티브 모드 on
  #  plt.show()

def search_route(start, goal) :
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
    
    return path


def add_drone(path) :
    drone = Drone(len(drones))
    drone.longitude, drone.latitude = path[0].longitude, path[0].latitude
    drone.destinations = path[:]
    drones.append(drone)

    

if __name__ == '__main__':        
    get_stations_from_db()
    get_edges_by_stations()
    print("간선 수:",len(edges))
    intersections = find_all_intersections(edges)
    
    make_graph()
    
    visualize_graph()

    start_time = time.time()
    path = search_route(stations[0], stations[13])
    add_drone(path)
    print(path)
    path = search_route(stations[4], stations[50])
    add_drone(path)
    print(path)
    path = search_route(stations[100], stations[20])
    add_drone(path)
    path = search_route(stations[100], stations[20])
    add_drone(path)
    path = search_route(stations[100], stations[20])
    add_drone(path)
    print(path)
    end_time = time.time()
    print("경로 탐색 소요 시간", end_time-start_time)

    for drone in drones :
        time.sleep(1)
        drone.move(edges)

    
    dest_sum = 1
    while(dest_sum > 0) :
        time.sleep(2)
        check_all_collision(intersections)
        dest_sum = 0
        for drone in drones: 
            dest_sum += len(drone.destinations)
            #for pos in drone.pos_queue:
                #ax.scatter(pos["longitude"], pos["latitude"], s=100, color='red')  # 노드 크기와 색상 설정
            print(drone.id, drone.pos_queue)
            drone.pos_queue.clear()
        # plt.draw()  # 그래프를 다시 그리기
        # plt.pause(1)  # 잠시 멈춤으로써 창이 멈추지 않고 업데이트 되도록 함
        # plt.show()
 #   plt.ioff()  # 인터랙티브 모드 종료
    print("모든 비행 종료")
    plt.show()

        