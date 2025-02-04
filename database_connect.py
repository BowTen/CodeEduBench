from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
import json
import aitestOrm
from sqlalchemy.pool import NullPool


# 读取配置文件
with open('config.json', 'r') as config_file:
	config = json.load(config_file)


def get_session(database):
	# 获取数据库配置
	db_config = config[database]
	DB_USER = db_config['user']
	DB_PASSWORD = db_config['password']
	DB_HOST = db_config['host']
	DB_PORT = db_config['port']
	DB_NAME = db_config['name']

	# 构建数据库连接URL
	DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

	# 创建数据库连接
	engine = create_engine(DATABASE_URL,poolclass=NullPool)
	Session = sessionmaker(bind=engine)
	session = Session()

	return session