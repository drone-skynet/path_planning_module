from math import radians, sin, cos, sqrt, atan2

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

class Edge:
  def __init__(self, origin, destination):
    self.origin = origin
    self.destination = destination
    self.weight = haversine([origin.latitude, origin.longitude], [destination.latitude, destination.longitude])
  def __repr__(self):
    return (f"edge(origin={self.origin.name}, destination={self.destination.name}, "
            f"weight={self.weight})")
  