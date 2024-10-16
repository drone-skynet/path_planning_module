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
    # MySQL 데이터베이스에 연결
    conn = mysql.connector.connect(
        host="localhost",        # MySQL 서버 주소 (로컬일 경우 localhost)
        user=db_user,    # MySQL 사용자 이름
        password=db_password,# MySQL 비밀번호
        database="drone" # 사용할 데이터베이스 이름
    )

    # 커서 생성
    cursor = conn.cursor()

    # 쿼리 실행
    cursor.execute("SELECT * FROM station")

    # 결과 가져오기
    results = cursor.fetchall()
    for row in results:
        station = Station(row[0],row[1],row[2],row[3],row[4])
        stations.append(station)

    # 커서와 연결 종료
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


# 유클리드 거리 계산 함수 (휴리스틱)
def heuristic(n1, n2):
    (x1, y1) = n1.longitude, n1.latitude
    (x2, y2) = n2.longitude, n2.latitude
    return haversine([x1,y1], [x2,y2])


def makeGraph() :
    # 그래프 생성
    global G
    G = nx.DiGraph()

    # 노드 추가 (좌표 정보 포함)
    for station in stations:
        #G.add_node((station.longitude, station.latitude))
        G.add_node((station))

    # 엣지 추가 (노드 간 거리 정보 포함)
    for edge in edges:
        #G.add_edge((edge.origin.longitude, edge.origin.latitude), (edge.destination.longitude, edge.destination.latitude), weight = edge.weight)
        G.add_edge(edge.origin, edge.destination, weight = edge.weight)

def visualize_graph():
    # 노드 그리기 (scatter 사용)
    for station in stations :
        ax.scatter(station.longitude, station.latitude, s=100, color='lightblue')  # 노드 크기와 색상 설정
        ax.text(station.longitude, station.latitude, station.name, fontsize=12, ha='right')  # 노드 레이블 표시

    # 간선 그리기 (plot 사용)
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
# 시각화 실행
visualize_graph()
