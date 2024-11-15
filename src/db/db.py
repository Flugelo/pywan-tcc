import mysql.connector
from mysql.connector import Error
from datetime import datetime

class Database:
    def __init__(self, host, user, passwd, database, port=3306):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.database = database
        self.connection = None  # Usando 'self.connection' consistentemente
        self.create_table()

    def open_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.passwd,
                database=self.database,
                port=self.port
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def execute_query(self, query, params=None):
        """
        Método auxiliar para executar queries que não retornam resultados (INSERT, UPDATE, DELETE).
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self.open_connection()
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"Error executing query: {e}")

    def fetch_query(self, query, params=None):
        """
        Método auxiliar para executar queries que retornam resultados (SELECT).
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self.open_connection()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Error fetching data: {e}")
            return None

    def create_table(self):
        """
        Cria as tabelas necessárias no banco de dados, caso não existam.
        """
        table_queries = [
            '''
            CREATE TABLE IF NOT EXISTS manipulation (
                id INT(10) NOT NULL AUTO_INCREMENT,
                action VARCHAR(7) NOT NULL,
                address VARCHAR(20) NOT NULL,
                operator VARCHAR(45) NULL,
                latency SMALLINT UNSIGNED NULL,
                created_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            ) ENGINE = InnoDB;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS ping (
                id INT(10) NOT NULL AUTO_INCREMENT,
                list_name VARCHAR(75) NOT NULL,
                gateway VARCHAR(20) NOT NULL,
                address VARCHAR(20) NOT NULL,
                latency INT(10) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            ) ENGINE = InnoDB;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS curruent_address_list (
                id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                list_name VARCHAR(100) NOT NULL,
                address VARBINARY(16) NOT NULL,
                prefix_length TINYINT UNSIGNED,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE = InnoDB;
            '''
        ]
        try:
            if self.connection is None or not self.connection.is_connected():
                self.open_connection()
            cursor = self.connection.cursor()
            for query in table_queries:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            print("Tables created or verified successfully")
        except Error as e:
            print(f"Error creating tables: {e}")

    def insert_manipulation(self, action, address, latency, operator):
        query = '''
            INSERT INTO manipulation (action, address, latency, operator)
            VALUES (%s, %s, %s, %s)
        '''
        params = (action, address, latency, operator)
        self.execute_query(query, params)

    def select(self, limit=50, order_by='ASC'):
        query = f'''
            SELECT * FROM manipulation
            ORDER BY id {order_by}
            LIMIT %s
        '''
        params = (limit,)
        return self.fetch_query(query, params)


    def insert_ping_test(self, list_name, gateway, address, latency):
        if isinstance(latency, int):
            query = '''
                INSERT INTO ping (list_name, gateway, address, latency)
                VALUES (%s, %s, %s, %s)
            '''
            params = (list_name, gateway, address, latency)
            self.execute_query(query, params)
        else:
            print("Latency must be an integer")


    def clear_current_address_list(self):
        query = "TRUNCATE TABLE curruent_address_list;"
        self.execute_query(query)

    def insert_curruent_address_list(self, data):
        query = '''
            INSERT INTO curruent_address_list (list_name, address, prefix_length, created_at)
            VALUES (%s, INET6_ATON(%s), %s, %s)
        '''
        try:
            if self.connection is None or not self.connection.is_connected():
                self.open_connection()
            cursor = self.connection.cursor()
            for entry in data:
                list_name = entry['list']
                address_full = entry['address']
                if '/' in address_full:
                    address, prefix_length = address_full.split('/')
                else:
                    address = address_full
                    prefix_length = None
                created_at = entry.get('creation-time', None)
                params = (list_name, address, int(prefix_length) if prefix_length else None, created_at)
                cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"Failed to insert data into MySQL table: {e}")

    def get_list_name_to_current_address_list(self, address : str):
        query = '''
            SELECT id, list_name FROM curruent_address_list WHERE address = INET6_ATON(%s) AND prefix_length = %s;
        '''
        address, prefix_length = address.split('/')
        params = (address, prefix_length)
        results = self.fetch_query(query,params)

        if len(results) == 1: 
            return results[0] 
        else: None

    def insert_one_current_address_list(self, entry):
        query = '''
            INSERT INTO curruent_address_list (list_name, address, prefix_length, created_at)
            VALUES (%s, INET6_ATON(%s), %s, %s)
        '''

        try:
            if self.connection is None or not self.connection.is_connected():
                self.open_connection()

            cursor = self.connection.cursor()
            list_name = entry['list_name']
            address, prefix_length = entry['network'].split('/')

            created_at = datetime.now()
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')

            params = (list_name, address, int(prefix_length) if prefix_length else None, created_at)
            cursor.execute(query, params)

            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"Failed to insert data into MySQL table: {e}")

    def update_current_address_list(self, entry):
        query = '''
            UPDATE curruent_address_list SET list_name = %s WHERE address = INET6_ATON(%s) AND prefix_length = %s
        '''

        address, prefix_length = entry['network'].split('/')
        params = (entry['list_name'],address, prefix_length)

        cursor = self.connection.cursor()
        cursor.execute(query, params)

        self.connection.commit()
        cursor.close()

    def __del__(self):
        self.close_connection()
