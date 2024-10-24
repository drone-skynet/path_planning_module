from math import radians, sin, cos, sqrt, atan2
import threading
import time

def haversine(coord1, coord2):
    # 지구의 반지름 (단위: km)
    R = 6371.0

    # 위도와 경도를 라디안으로 변환
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    # 위도와 경도의 차이 계산
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine 공식
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # 거리 계산
    distance = R * c
    return distance

def find_distance_between_2_drones(drone1, drone2) :
  return haversine([drone1.latitude, drone1.longitude], [drone2.latitude, drone2.longitude])

def find_edge_by_point(edges, origin, destination) :
  for edge in edges :
    if(edge.origin == origin and edge.destination == destination) :
      return edge
  return None  

class Station:
  def __init__(self, id, name, longitude, latitude, capacity):
    self.id = id
    self.name = name
    self.longitude = float(longitude)
    self.latitude = float(latitude)
    self.capacity = capacity

  def __repr__(self):
    return self.name
    #return (f"Station(id={self.id}, name={self.name}, "
    #       f"latitude={self.latitude}, longitude={self.longitude}, capacity={self.capacity})")
  def __eq__(self, other):
    return self.id == other.id #내용 비교
  def __hash__(self):
    return hash((self.longitude, self.latitude))

class Edge:
  def __init__(self, origin, destination):
    self.origin = origin
    self.destination = destination
    self.weight = haversine([origin.latitude, origin.longitude], [destination.latitude, destination.longitude])
    self.drones_on_the_edge = []
  def __repr__(self):
    return (f"edge(origin={self.origin.name}, destination={self.destination.name}, "
            f"weight={self.weight})")
  def __eq__(self, other):
    return self.origin == other.origin and self.destination == other.destination
  


class Drone:
  def __init__(self,id) :
    self.id=id
    self.longitude = 127.12629039752
    self.latitude = 37.4199323570328
    self.speed = 0.001
    self.velocity = [0,0]
    self.destinations = []
    self.is_moving = False
    #사라질 필드들
    self.pos_queue = []
    self.before_station = None
    self.edge = None
  @staticmethod
  def _calculate_lat_lon_speed(lat1, lon1, lat2, lon2, total_speed):
    # 각 변위를 km 단위로 변환 (대략적인 변환)
    lat_distance_km = haversine([lat1, lon1], [lat2, lon1])  # 경도 변화 없이 위도만 변화할 때 거리
    lon_distance_km = haversine([lat1, lon1], [lat1, lon2])  # 위도 변화 없이 경도만 변화할 때 거리

    # 전체 거리 계산
    total_distance = haversine([lat1, lon1], [lat2, lon2])

    # 위도와 경도로의 속도 분해 (비율에 따라)
    if total_distance == 0:
        lat_v = 0
        lon_v = 0
    else:
        lat_v = (lat_distance_km / total_distance) * total_speed
        if(lat2-lat1<0) :
          lat_v *= -1
        lon_v = (lon_distance_km / total_distance) * total_speed
        if(lon2-lon1<0) :
          lon_v *= -1
    
    return lat_v, lon_v

  def __renew_edge(self, edges) :
    if(self.edge is not None) :
      self.edge.drones_on_the_edge.remove(self)
    if(len(self.destinations) < 1) :
      return
    edge = find_edge_by_point(edges, self.before_station, self.destinations[0])
    self.edge = edge
    edge.drones_on_the_edge.append(self)
    print("현재 드론:", self.id, "간선:",self.before_station.name,"-",self.destinations[0].name)
    return


  def _worker(self, edges):
    before_velocity = [0,0]
    self.before_station=self.destinations[0]
    self.destinations.pop(0)
    self.__renew_edge(edges)
    while len(self.destinations)!=0 and self.is_moving :
      #print("드론 id :", self.id, self.latitude, self.longitude)
      self.pos_queue.append({"longitude" : self.longitude, "latitude" : self.latitude})
      dest=self.destinations[0]
      self.velocity = self._calculate_lat_lon_speed(self.latitude, self.longitude, dest.latitude, dest.longitude, self.speed)
      self.latitude += self.velocity[0]
      self.longitude += self.velocity[1]
      time.sleep(1)
      if(self.velocity[0]*before_velocity[0] < 0 or self.velocity[1]*before_velocity[1] < 0) :
        print("도착 목적지:", self.destinations[0].name)
        self.before_station=self.destinations[0]
        self.destinations.pop(0)
        self.velocity=[0,0]
        before_velocity=[0,0]
        self.__renew_edge(edges)
        continue
      before_velocity=self.velocity
    return
    
  def move(self, edges):
    self.is_moving=True
    thread = threading.Thread(target=self._worker, args=(edges,))
    thread.start()
    print("드론", self.id, "비행 시작")
    return
  
  def stop(self):
    self.is_moving=False
    print("드론",self.id,"강제 멈춤")
  
class Intersection :
  def __init__(self, edges, latitude, longitude) :
    self.edges = edges
    self.latitude = latitude
    self.longitude = longitude

  def __repr__(self):
    return "{Intersection " + str(self.latitude) + ", " + str(self.longitude) + "}"
  
  def __eq__(self, other) :
    if(self.latitude == other.latitude and self.longitude == other.longitude) :
      return True
    return False
  
  def __hash__(self):
      return hash((self.latitude, self.longitude))
  
  def fuse_same_point(self, other) : 
    if self.__eq__(other) :
      #self.edges.extend(other.edges)
      for new_edge in other.edges:
        if new_edge not in self.edges : #하나의 경로가 두 개의 경로와 교점을 만들어도, 중복된 경로는 한 번만 들어가게
          self.edges.append(new_edge)
      return True
    return False
    