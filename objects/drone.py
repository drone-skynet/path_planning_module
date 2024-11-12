from ..utils.utils import haversine, find_edge_by_point
import threading
import time
import math
import mqtt_client


class Drone:
  edges = []
  drones = []
  def __init__(self,id, is_armed, is_guided, latitude, longitude, altitude, battery_status, mission_status) :
    self.id = id
    self.is_armed = is_armed
    self.is_guided = is_guided
    self.longitude = longitude
    self.latitude = latitude
    self.altitude = altitude
    self.battery_status = battery_status
    self.mission_status = mission_status

    self.destinations = []
 #   self.is_moving = False 속도로 체크
    self.velocity = [0,0,0]
    self.take_off_time = None
    self.go_flag = 0
    self.prev_station = None
    self.edge = None
  
  def is_moving(self):
    if self.velocity[0] < 0.1 and self.velocity[1] < 0.1 and self.velocity[2] < 0.1 :
      return False
    return True
  
  def __renew_edge(self) :
    if(self.edge is not None) :
      self.edge.drones_on_the_edge.remove(self)
    if(len(self.destinations) < 1) :
      return 
    edge = self.add_to_next_edge()
    self.edge = edge
    print("현재 드론:", self.id, "간선:",self.prev_station.name,"-",self.destinations[0].name)
    return

  def add_to_next_edge(self):
    if len(self.destinations) < 2:
      return None
    next_edge = find_edge_by_point(Drone.edges, self.destinations[0], self.destinations[1]) 
    if(self not in next_edge.drones_on_the_edge) :
      next_edge.drones_on_the_edge.append(self)
      print("다음 간선에 미리 추가", self.id)
    return next_edge
    
  def move(self):
    # self.is_moving=True
    command = {
      "command": "MOVE_TO",
      "latitude": self.destinations[0].latitude,
      "longitude": self.destinations[0].longitude,
      "altitude": self.altitude
    }
    mqtt_client.publish_control_command(command)
    print("드론", self.id, "이동 시작")
    return
  
  def stop(self):
    # self.go_flag = 0
    if(not self.is_moving) :
      return
    print("드론",self.id,"강제 멈춤")

  def find_next_edge(self):
    return find_edge_by_point(self.destination[0], self.destination[1])
  
  def take_off(self):
    self.add_to_next_edge()    
    self.prev_station = self.destinations[0]
    self.destinations.pop(0)
    self.__renew_edge()
    # 드론 GUIDED 모드 설정
    command = {
      "command": "SET_MODE",
      "mode": "GUIDED",
      "sys_id": self.id,
    }
    mqtt_client.publish_control_command(command)
    # 드론 ARM
    command = {
      "command": "ARM",
      "sys_id": self.id,
      "comp_id": 1 
    }
    mqtt_client.publish_control_command(command)
    self.is_armed = True
    # 이륙
    command = {
      "command": "TAKEOFF",
      "sys_id": 1,
      "comp_id": 1,
      "altitude": 90
    }
    mqtt_client.publish_control_command(command)
    self.take_off_time = time.time()

    print("드론", self.id, "이륙")
    while(self.altitude < 80) :
      time.sleep(1)
    self.move()
  
  def remaining_distance(self):
    return haversine([self.latitude, self.longitude], [self.destinations[0].latitude, self.destinations[0].longitude])

  def land(self):
    self.stop()

    command = {
      "command": "LAND",
      "sys_id": 1,
      "comp_id": 1
    }
    mqtt_client.publish_control_command(command)

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
