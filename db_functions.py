from dotenv import load_dotenv
import os
import mysql.connector
import csv

load_dotenv()

HOST = os.getenv("HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

mydb = mysql.connector.connect(
  host=HOST,
  user=USERNAME,
  password=PASSWORD,
  database=DATABASE
)

def import_data(folder_name: str):
    cursor = mydb.cursor()
    try:
        # drop tables
        drop_tables = [
            "ModelConfigurations", "ModelServices", "DataStorage", "LLMService",
            "InternetService", "Configuration", "CustomizedModel", "BaseModel",
            "AgentClient", "AgentCreator", "User"
        ]
        for t in drop_tables:
            cursor.execute(f"DROP TABLE IF EXISTS {t}")

        # create tables
        ddls = [
            """CREATE TABLE User (
                uid INT, email TEXT NOT NULL, username TEXT NOT NULL,
                PRIMARY KEY (uid))""",

            """CREATE TABLE AgentCreator (
                uid INT, bio TEXT, payout TEXT,
                PRIMARY KEY (uid),
                FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE)""",

            """CREATE TABLE AgentClient (
                uid INT, interests TEXT NOT NULL, cardholder TEXT NOT NULL,
                expire DATE NOT NULL, cardno INT NOT NULL, cvv INT NOT NULL,
                zip INT NOT NULL, PRIMARY KEY (uid),
                FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE)""",

            """CREATE TABLE BaseModel (
                bmid INT, creator_uid INT NOT NULL, description TEXT NOT NULL,
                PRIMARY KEY (bmid),
                FOREIGN KEY (creator_uid) REFERENCES AgentCreator(uid)
                ON DELETE CASCADE)""",

            """CREATE TABLE CustomizedModel (
                bmid INT, mid INT NOT NULL,
                PRIMARY KEY (bmid, mid),
                FOREIGN KEY (bmid) REFERENCES BaseModel(bmid)
                ON DELETE CASCADE)""",

            """CREATE TABLE Configuration (
                cid INT, client_uid INT NOT NULL, content TEXT NOT NULL,
                labels TEXT NOT NULL, PRIMARY KEY (cid),
                FOREIGN KEY (client_uid) REFERENCES AgentClient(uid)
                ON DELETE CASCADE)""",

            """CREATE TABLE InternetService (
                sid INT, provider TEXT NOT NULL, endpoints TEXT NOT NULL,
                PRIMARY KEY (sid))""",

            """CREATE TABLE LLMService (
                sid INT, domain TEXT, PRIMARY KEY (sid),
                FOREIGN KEY (sid) REFERENCES InternetService(sid)
                ON DELETE CASCADE)""",

            """CREATE TABLE DataStorage (
                sid INT, type TEXT, PRIMARY KEY (sid),
                FOREIGN KEY (sid) REFERENCES InternetService(sid)
                ON DELETE CASCADE)""",

            """CREATE TABLE ModelServices (
                bmid INT NOT NULL, sid INT NOT NULL, version INT NOT NULL,
                PRIMARY KEY (bmid, sid),
                FOREIGN KEY (bmid) REFERENCES BaseModel(bmid) ON DELETE CASCADE,
                FOREIGN KEY (sid) REFERENCES InternetService(sid)
                ON DELETE CASCADE)""",

            """CREATE TABLE ModelConfigurations (
                bmid INT NOT NULL, mid INT NOT NULL, cid INT NOT NULL,
                duration INT NOT NULL,
                PRIMARY KEY (bmid, mid, cid),
                FOREIGN KEY (bmid, mid) REFERENCES CustomizedModel(bmid, mid)
                ON DELETE CASCADE,
                FOREIGN KEY (cid) REFERENCES Configuration(cid)
                ON DELETE CASCADE)"""
        ]

        for ddl in ddls:
            cursor.execute(ddl)

        # import CSV files
        load_order = [
            "User", "AgentCreator", "AgentClient", "BaseModel", "CustomizedModel",
            "Configuration", "InternetService", "LLMService", "DataStorage",
            "ModelServices", "ModelConfigurations"
        ]

        for table in load_order:
            path = os.path.join(folder_name, f"{table}.csv")
            if not os.path.exists(path):
                continue

            with open(path, "r") as f:
                for row in csv.reader(f):
                    row = [None if x == "NULL" else x for x in row]
                    placeholders = ",".join(["%s"] * len(row))
                    cursor.execute(f"INSERT INTO {table} VALUES ({placeholders})", row)

        mydb.commit()
        cursor.close()
        print("Success")

    except Exception:
        cursor.close()
        print("Fail")


def insertAgentClient(uid:int, username:str, email:str, card_number:int, card_holder:str, expiration_date:str, cvv:int, zip:int, interests:str):
    # convert string arguments from command line into correct datatypes
    uid = int(uid)
    card_number = int(card_number)
    cvv = int(cvv)
    zip = int(zip)

    # insert agent client
    cursor = mydb.cursor()

    # first put uid, email, and username into user
    query = """
            INSERT IGNORE INTO User (uid, email, username) 
            VALUES (%s, %s, %s)
            """
    values = (uid, email, username)

    cursor.execute(query, values)
    mydb.commit()

    query = """
            INSERT IGNORE INTO AgentClient (uid, interests, cardholder, expire, cardno, cvv, zip) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
    values = (uid, interests, card_holder, expiration_date,card_number, cvv, zip)   
    
    cursor.execute(query, values)
    mydb.commit()
    
    return


def addCustomizedModel(mid:int, bmid:int):
  #add customized model to table

  #grab all the needed info
  cursor = mydb.cursor()

  #check if base model exists

  query = """
          SELECT * 
          FROM BaseModel b
          WHERE b.bmid = %s
          """
  cursor.execute(query, (bmid,))
  results = cursor.fetchall()

  if results:
    #add customized model
    query = """
            INSERT IGNORE INTO CustomizedModel (bmid, mid)
            VALUES (%s, %s)
            """          
    values = (bmid, mid)

    cursor.execute(query, values)
    mydb.commit()

    return

  else:
    return False


def deleteBaseModel(bmid:int):
    # delete base model from table
    uid = int(uid)

    cursor = mydb.cursor

    query = """
            DELETE FROM BaseModel WHERE bmid = (bmid)
            VALUES (%s)
            """
    values = (bmid)

    cursor.execute(query,values)
    mydb.commit()
    
    return


def listInternetService(bmid: int):
    cursor = mydb.cursor()
    try:
        bmid = int(bmid)

        query = """
            SELECT I.sid, I.endpoints, I.provider
            FROM ModelServices M
            JOIN InternetService I ON M.sid = I.sid
            WHERE M.bmid = %s
            ORDER BY I.provider ASC
        """

        cursor.execute(query, (bmid,))
        results = cursor.fetchall()

        for row in results:
            print(",".join(str(x) for x in row))

        cursor.close()

    except Exception:
        cursor.close()
        print("Fail")

def keywordSearch(keyword: str):
  
  """
  SELECT *
  FROM BaseModel as b
  INNER JOIN ModelServices as ms ON b.bmid = ms.bmid
  INNER JOIN LLMService as l on ms.sid = l.sid
  WHERE l.domain LIKE '%video%' 
  ORDER BY b.bmid ASC 
  LIMIT 5
  """
