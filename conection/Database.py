import pymysql
import pyodbc
import json
#MYSQL
def conectar_bd():
    return pymysql.connect(
        host="servimaxinternal.app", 
        user='sergio_naranjo',
        password='5RT_20#',
        db='MERCADERIA',
        port=4406 
    )
    
# SQL SERVER
def conectar_abako():
    server = '10.100.200.254\\SQLSERVIMAX'
    database = 'SIN_SERVIMAX'
    username = 'msin'
    password = 'msin'
    
    connection_string = (
        'DRIVER={ODBC Driver 18 for SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'TrustServerCertificate=yes;'
    )
    try:
        connection = pyodbc.connect(connection_string)
        print("Conexión exitosa a SQL Server")
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    