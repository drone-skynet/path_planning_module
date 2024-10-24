from objects import Drone, Edge, Intersection, haversine


def check_collision_of_one_intersection(intersection):
  drones_on_intersections = []
  for edge in intersection.edges :
    drones_on_intersections.extend(edge.drones_on_the_edge)
  drones_len = len(drones_on_intersections)
  for i in range(drones_len) :
    for j in range(i+1, drones_len) :
      drone1 = drones_on_intersections[i]
      drone2 = drones_on_intersections[j]
      distance = haversine([drone1.latitude, drone1.longitude], [drone2.latitude, drone2.longitude])
      #20m를 안전 거리
      if(distance < 0.02) :
        drone1.stop()
        drone2.stop()
  return
    


def check_all_collision(intersections) :
  for intersection in intersections:
    check_collision_of_one_intersection(intersection)
  return