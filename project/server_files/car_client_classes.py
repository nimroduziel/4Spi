# author - lil uzi vert
# IMPORTS
import sqlite3

# CLASS - this CLASS represents a camera in the system
class Car:
    def __init__(self, owner, ID, name, state):
        self.owner = owner
        self.ID = ID
        self.name = name
        self.state = state
    

    def var_list(self):
        return [self.camera_code, self.owner, self.mode]


# CLASS - this CLASS represents a user in the system
class Client:
    def __init__(self, username, salt, hash):
        self.username = username
        self.salt = salt
        self.hash = hash


    def var_list(self):
        return [self.username, self.password_salted_hash, self.salt, self.owned_cameras, self.accessed_cameras]


# CLASS - this class does the sql actions for the main server 
class CarClientORM:
    def __init__(self):
        self.conn = sqlite3.connect('cars_clients_DB.db')  # will store the DB connection
        self.cursor = self.conn.cursor()   # will store the DB connection cursor

    def open_DB(self): #
        """
        will open DB file and put value in:
        self.conn (need DB file name)
        and self.cursor
        """
        self.conn = sqlite3.connect('cars_clients_DB.db')
        self.cursor=self.conn.cursor()

    def close_DB(self): #
        self.conn.close()

    def fetch_all(self):
        print(self.cursor.fetchall())


    #All USER SQL
    # READ 
    def get_clients(self):
            self.open_DB()

            sql = f"SELECT * FROM 'client_table'"
            res = self.cursor.execute(sql)
            users = self.cursor.fetchall()

            self.close_DB()
            return users

    def get_usernames(self):
            self.open_DB()

            sql = f"SELECT Username FROM 'client_table'"
            res = self.cursor.execute(sql)
            users = self.cursor.fetchall()
            users2 = [x[0] for x in users]
            self.close_DB()
            return users2

    def get_user_by_username(self, username):
        self.open_DB()
        sql = f"SELECT * FROM 'client_table' WHERE Username='{username}'"
        res = self.cursor.execute(sql)
        user_data = self.cursor.fetchall()[0]

        self.close_DB()
        return user_data

    #WRITE
    def insert_user(self, client):#
            self.open_DB()
            
            sql = f"INSERT INTO client_table VALUES ('{client.username}','{client.salt}','{client.hash}')"
            print("insert_user: "+ sql)
            self.cursor.execute(sql)

            self.conn.commit()
            self.close_DB()
            return


    # ALL CAMERA SQL 
    # READ

    # WRITE
    def insert_car(self, car): #
        self.open_DB()

        sql = f"INSERT INTO car_table VALUES ('{car.owner}','{car.ID}','{car.name}','{car.state}')"
        print("insterted car: ", sql)
        self.cursor.execute(sql)
        
        self.conn.commit()

        self.close_DB()




    def get_cars_by_owner(self,owner):#
        self.open_DB()

        sql = f"SELECT * FROM car_table WHERE Owner= '{owner}';"
        print("get car by model: " + sql)
        res= self.cursor.execute(sql)
        cars = self.cursor.fetchall()

        self.close_DB()
        return cars

    def get_cars_id_by_owner(self,owner):#
        self.open_DB()

        sql = f"SELECT ID FROM car_table WHERE Owner= '{owner}';"
        print("get car by model: " + sql)
        res= self.cursor.execute(sql)
        cars = self.cursor.fetchall()
        cars2 = [i[0] for i in cars]
        print(cars2)

        self.close_DB()
        return cars2

    def get_cars_name_by_owner(self, owner):#
        self.open_DB()

        sql = f"SELECT Name FROM car_table WHERE Owner= '{owner}';"
        print("get car by model: " + sql)
        res= self.cursor.execute(sql)
        cars = self.cursor.fetchall()
        cars2 = [i[0] for i in cars]
        print(cars2)

        self.close_DB()
        return cars2

    def get_IDs(self):
        self.open_DB()

        sql = f"SELECT ID FROM car_table;"
        print("get car by model: " + sql)

        res = self.cursor.execute(sql)
        IDs = self.cursor.fetchall()
        IDs2 = [x[0] for x in IDs]
        self.close_DB()

        return IDs2

    def change_state(self, ID, state):
        self.open_DB()
        sql = f"UPDATE car_table SET State = '{state}' WHERE ID = '{ID}'"

        self.cursor.execute(sql)
        self.conn.commit()
        self.close_DB()
        return
        


        