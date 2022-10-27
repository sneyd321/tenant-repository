import argparse
import configparser
import os 

parser = argparse.ArgumentParser()

parser.add_argument('--user', dest='user', type=str)
parser.add_argument('--password', dest='password', type=str)
parser.add_argument('--database', dest='database', type=str)
parser.add_argument('--host', dest='host', type=str)

args = parser.parse_args()
user = args.user
password = args.password
host = args.host
database = args.database


config = configparser.ConfigParser()
config.read('alembic.ini')
connectionString = f"mysql+aiomysql://{user}:{password}@{host}/{database}"
print(connectionString)


config['alembic']["sqlalchemy.url"] = connectionString


with open('alembic.ini', 'w') as configfile:
    config.write(configfile)