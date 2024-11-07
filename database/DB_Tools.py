import sqlite3
import json

class DB_Tools():
    def __init__(self):
        self.conn = sqlite3.connect('database/database.sqlite3',check_same_thread=False)
        self.cursor = self.conn.cursor()

    def insert(self,feature_name,scenario_data):
        insert_query = "INSERT INTO index_feature2scenariostable (feature, scenarios) VALUES (?, ?)"

        scenarios_json=json.dumps(scenario_data)

        self.cursor.execute(insert_query, (feature_name,scenarios_json))
        self.conn.commit()

    def select_all(self):
        self.cursor.execute("SELECT * FROM index_feature2scenariostable")
        rows = self.cursor.fetchall()
        feature2scenarios_list=[]
        for row in rows:
            feature2scenarios={}
            feature2scenarios["feature"]=row[1]
            feature2scenarios["scenarios"]=eval(row[2])
            feature2scenarios_list.append(feature2scenarios)

        return feature2scenarios_list





        