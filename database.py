from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ⚠️ apna password yaha dal
DATABASE_URL = "mysql+pymysql://root:Aryan%40113@localhost/verity_ai"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()