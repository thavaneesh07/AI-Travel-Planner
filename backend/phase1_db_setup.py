import sqlite3

conn = sqlite3.connect("travel_planner.db")
c = conn.cursor()

c.executescript("""
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT,
  profile TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itineraries (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  destination TEXT,
  start_date TEXT,
  end_date TEXT,
  budget REAL,
  interests TEXT,
  status TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itinerary_days (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  itinerary_id TEXT,
  day_number INTEGER,
  date TEXT,
  morning TEXT,
  afternoon TEXT,
  evening TEXT,
  estimated_cost REAL
);
""")

# insert sample user + itinerary
c.execute("INSERT OR IGNORE INTO users (id,name,email,profile) VALUES (?,?,?,?)",
          ("USER_ID_1","Brunda","brunda@example.com",'{"traveler_type":"solo"}'))

c.execute("""INSERT OR IGNORE INTO itineraries (id,user_id,destination,start_date,end_date,budget,interests,status)
             VALUES (?,?,?,?,?,?,?,?)""",
          ("ITINERARY_ID_123","USER_ID_1","Paris","2025-10-01","2025-10-07",1500,'["history","food"]',"completed"))

c.execute("""INSERT INTO itinerary_days (itinerary_id,day_number,date,morning,afternoon,evening,estimated_cost)
             VALUES (?,?,?,?,?,?,?)""",
          ("ITINERARY_ID_123",1,"2025-10-01",
           "Check-in at budget hotel near Montmartre",
           "Visit Eiffel Tower & Seine River cruise",
           "Dinner at Le Bouillon Pigalle",120.0))

conn.commit()
print("✅ DB created and sample rows inserted (travel_planner.db).")
conn.close()
