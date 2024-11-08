from ..utils.utils import haversine, find_edge_by_point
import threading
import time
import math


class Drone:
  edges = []
  drones = []
  def __init__(self,id) :
    self.id=id
    self.longitude = 127.12629039752
    self.latitude = 37.4199323570328
    self.speed = 0.005
    self.velocity = [0,0]
    self.destinations = []
    self.is_moving = False
    self.is_armed = False
    self.take_off_time = None
    self.go_flag = 0
    #사라질 필드들
    self.prev_station = None
    self.edge = None
  @staticmethod
  def _calculate_lat_lon_speed(lat1, lon1, lat2, lon2, total_speed_km):
    # 위도에 따른 경도 거리 보정
    # 적도에서의 1도당 거리(약 111km)에 cos(위도) 를 곱하여 보정
    lat_km_per_degree = 111  # 위도 1도당 거리는 항상 약 111km
    lon_km_per_degree = 111 * math.cos(math.radians(lat1))  # 현재 위도에서의 경도 1도당 거리

    # 위도, 경도 차이를 km로 변환
    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1
    
    lat_distance_km = abs(lat_diff) * lat_km_per_degree
    lon_distance_km = abs(lon_diff) * lon_km_per_degree

    # 전체 거리 계산 (피타고라스 정리)
    total_distance = math.sqrt(lat_distance_km**2 + lon_distance_km**2)

    if total_distance == 0:
        return 0, 0

    # 속도 벡터 계산
    speed_ratio = total_speed_km / total_distance
    lat_v = (lat_distance_km * speed_ratio) / lat_km_per_degree
    lon_v = (lon_distance_km * speed_ratio) / lon_km_per_degree

    # 방향 설정
    if lat_diff < 0:
        lat_v *= -1
    if lon_diff < 0:
        lon_v *= -1
    
    return lat_v, lon_v

  def __renew_edge(self) :
    if(self.edge is not None) :
      self.edge.drones_on_the_edge.remove(self)
    if(len(self.destinations) < 1) :
      return 
    edge = self.__add_to_next_edge()
    self.edge = edge
    print("현재 드론:", self.id, "간선:",self.prev_station.name,"-",self.destinations[0].name)
    return

  def __add_to_next_edge(self):
    if len(self.destinations) < 2:
      return None
    next_edge = find_edge_by_point(Drone.edges, self.destinations[0], self.destinations[1]) 
    if(self not in next_edge.drones_on_the_edge) :
      next_edge.drones_on_the_edge.append(self)
      print("다음 간선에 미리 추가", self.id)
    return next_edge

  def _worker(self):
    while len(self.destinations)!=0 and self.is_moving:
      #print("드론 id :", self.id, self.latitude, self.longitude)
      dest=self.destinations[0]
      self.velocity = self._calculate_lat_lon_speed(self.latitude, self.longitude, dest.latitude, dest.longitude, self.speed)
      self.latitude += self.velocity[0]
      self.longitude += self.velocity[1]
      if len(self.destinations) > 0 and haversine([self.latitude, self.longitude], [self.destinations[0].latitude, self.destinations[0].longitude]) <= 0.05:
          self.__add_to_next_edge()
      time.sleep(0.5)
      # 드론의 현재 위치에서 목적지까지의 벡터
      if(len(self.destinations) > 0) :
        drone_to_dest = [
          self.destinations[0].latitude - self.latitude,
          self.destinations[0].longitude - self.longitude
        ]
        # 출발지에서 목적지까지의 벡터  
        start_to_dest = [
          self.destinations[0].latitude - self.prev_station.latitude,
          self.destinations[0].longitude - self.prev_station.longitude
        ]
        # 두 벡터의 내적 계산
        dot_product = (drone_to_dest[0] * start_to_dest[0] + 
                      drone_to_dest[1] * start_to_dest[1])
        
        if dot_product <= 0:
          print("도착한 목적지:", self.destinations[0].name)
          self.prev_station = self.destinations[0]
          self.destinations.pop(0)
          self.velocity = [0,0]
          self.__renew_edge()
          continue
    if(len(self.destinations) == 0) :
      self.land()
    return
    
  def move(self):
    self.is_moving=True
    # self.go_flag = 1
    thread = threading.Thread(target=self._worker, args=())
    thread.start()
    print("드론", self.id, "이동 시작")
    return
  
  def stop(self):
    # self.go_flag = 0
    self.is_moving=False
    print("드론",self.id,"강제 멈춤")

  def find_next_edge(self):
    return find_edge_by_point(self.destination[0], self.destination[1])
  
  def take_off(self):
    self.take_off_time = time.time()
    self.is_armed = True
    self.__add_to_next_edge()    
    self.prev_station = self.destinations[0]
    self.destinations.pop(0)
    self.__renew_edge()
    self.move()
    print("드론", self.id, "이륙")
  
  def land(self):
    self.stop()
    self.take_off_time = None
    self.is_moving = False
    self.edge = None
    self.is_armed = False
    print("드론", self.id, "착륙")
    return
  
  def __eq__(self, other):
    return self.id == other.id
    
  def __hash__(self):
    return hash(self.id)
