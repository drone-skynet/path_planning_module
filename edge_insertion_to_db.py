from objects import Edge, Station
import os
import mysql.connector

DB_HOST = 'localhost'
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = 'drone'

stations=[]
edges=[]

def get_stations_from_db() :
  conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME 
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

def insert_edge_to_db() :
  connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
  )
  try:
    cursor = connection.cursor()

   

    insert_sql = """
      INSERT INTO edge (path_id, origin_station_id, destination_station_id, distance)
      VALUES (uuid(), %s, %s, %s)
      ON DUPLICATE KEY UPDATE
      station_name = VALUES(station_name)
    """

    for edge in edges:
      cursor.execute(insert_sql, (edge.origin.id, edge.destination.id, edge.weight))
        
      connection.commit()
  finally:
    cursor.close()
    connection.close()


