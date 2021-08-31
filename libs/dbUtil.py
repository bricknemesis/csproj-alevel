
import sqlite3
import random
conn = sqlite3.connect("users.db")
c = conn.cursor()

idKeys = {
    "customer": "customerId",
    "customerMetrics": "customerId",
    "trainer": "trainerId",
    "lesson": "lessonId",
    "location": "locationId"
}

c.execute("""
    CREATE table IF NOT EXISTS customer (
        customerId integer,
        username text,
        password text,
        firstName text,
        lastName text,
        postcode text,
        address text,
        telephone text,
        dateOfBirth text,
        email text,
        pendingVerificationCode text,
        profilePicture blob
    )
""")

c.execute("""
    CREATE table IF NOT EXISTS trainer (
        trainerId integer,
        username text,
        password text,
        firstName text,
        lastName text,
        postcode text,
        address text,
        telephone text,
        dateOfBirth text,
        email text,
        pendingVerificationCode text,
        profilePicture blob
    )
""")

c.execute("""
    CREATE table IF NOT EXISTS manager (
        customerId integer,
        username text,
        password text,
        firstName text,
        lastName text,
        postcode text,
        address text,
        telephone text,
        dateOfBirth text,
        email text,
        pendingVerificationCode text,
        profilePicture blob
    )
""")

c.execute("""
   CREATE table IF NOT EXISTS customerMetrics (
       customerId integer,
       weight float,
       height float,
       run_time float,
       maxDeadlift float
   )
""")

c.execute("""
   CREATE table IF NOT EXISTS lesson (
       lessonId integer,
       trainerId integer,
       lessonType text,
       duration float,
       date text,
       locationId integer,
       maxPeople integer,
       currentPeople integer
   )
""")

c.execute("""
    CREATE table IF NOT EXISTS location (
        locationId integer
    )
""")

def checkIfIdExists(tableName, id):
    c.execute(f"SELECT * FROM {tableName} where {idKeys[tableName]} = {id}")
    return len(c.fetchall() or []) > 0 and True or False

def generateId(tableName):
    c.execute(f"SELECT * FROM {tableName}")
    pupilData = c.fetchall()
    newId = len(pupilData) + 1

    while checkIfIdExists(tableName, newId):
        newId = random.randint(1, 9999999999999999) #if this ever clashed I'd be pretty unlucky...
    return newId

def create(tableName, dict):
    #     c.execute(f"""
    #     INSERT into {tableName} VALUES (
    #         :id,
    #         :username,
    #         :password,
    #         :firstName,
    #         :lastName,
    #         :postcode,
    #         :address,
    #         :telephone,
    #         :dateOfBirth,
    #         :email,
    #         :profilePicture,
    #         :pendingVerificationCode 
    #     )
    # """, dict)

    s = f"INSERT into {tableName} VALUES ("
    i = 0
    for key, value in dict.items():
        i += 1
        s += "\n\t" + ":" + key + (i != len(dict) and "," or "")
    s += "\n)"
    print(s)
    c.execute(s, dict)
    conn.commit()

def retrieve(tableName, id = None):

    if not id:
        c.execute(f"SELECT * FROM {tableName}") #basically return everything
    else:
        c.execute(f"SELECT * FROM {tableName} WHERE {idKeys[tableName]} = :id", {"id": id})
    
    return id and c.fetchone() or c.fetchall()

def update(tableName, id, key, value):
    c.execute(f"UPDATE {tableName} SET {key} = \"{value}\" WHERE {idKeys[tableName]} = {id}")
    conn.commit()

def delete(tableName, id):
    c.execute(f"DELETE FROM {tableName} WHERE {idKeys[tableName]} = :id", {"id": id})
    conn.commit()

