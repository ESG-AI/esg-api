from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql://neondb_owner:npg_mEB3Jkfcj0tu@ep-little-poetry-a1nu8s3g-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text, nullable=False)
    uploaded_at = Column(TIMESTAMP, default=func.now())

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"))
    chunk_index = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

def init_db():
    Base.metadata.create_all(bind=engine)