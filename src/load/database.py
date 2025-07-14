from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_name = Column(String)
    full_post_content = Column(String)
    replies = Column(Integer)
    reposts = Column(Integer)
    likes = Column(Integer)
    views = Column(Integer)
    platform = Column(String)


class PostManager():
    def __init__(self, url):
        self.engine = create_engine(url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def init_db(self):
        Base.metadata.create_all(bind=self.engine)
    
    def save_to_db(self, dataframe: pd.DataFrame):
        db = self.SessionLocal()
        try:
            for _, row in dataframe.iterrows():
                post = Post(
                    author_name=row['author_name'],
                    full_post_content=row['full_post_content'],
                    replies=row['replies'] if pd.notnull(row['replies']) else 0,
                    reposts=row['reposts'] if pd.notnull(row['reposts']) else 0,
                    likes=row['likes'] if pd.notnull(row['likes']) else 0,
                    views=row['views'] if pd.notnull(row['views']) else 0,
                    platform=row['platform']
                )
                db.add(post)
            db.commit()
        finally:
            db.close()