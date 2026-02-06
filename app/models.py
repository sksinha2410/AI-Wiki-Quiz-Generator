from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    key_entities = Column(Text, nullable=True)  # stored as JSON string
    sections = Column(Text, nullable=True)  # stored as JSON string

    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    related_topics = relationship(
        "RelatedTopic", back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # stored as JSON string
    answer = Column(String, nullable=False)
    difficulty = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)

    quiz = relationship("Quiz", back_populates="questions")


class RelatedTopic(Base):
    __tablename__ = "related_topics"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    topic = Column(String, nullable=False)

    quiz = relationship("Quiz", back_populates="related_topics")
