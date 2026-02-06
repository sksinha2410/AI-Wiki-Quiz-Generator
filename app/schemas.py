from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class QuestionBase(BaseModel):
    question: str
    options: List[str]
    answer: str
    difficulty: str | None = None
    explanation: str | None = None


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: int

    class Config:
        orm_mode = True


class RelatedTopicBase(BaseModel):
    topic: str


class RelatedTopic(RelatedTopicBase):
    id: int

    class Config:
        orm_mode = True


class QuizBase(BaseModel):
    url: HttpUrl


class QuizCreate(QuizBase):
    pass


class Quiz(QuizBase):
    id: int
    title: str
    summary: Optional[str] = None
    key_entities: dict | None = None
    sections: list[str] | None = None
    quiz: List[Question] = []
    related_topics: List[str] = []

    class Config:
        orm_mode = True


class QuizListItem(BaseModel):
    id: int
    url: str
    title: str

    class Config:
        orm_mode = True


class QuizResponse(BaseModel):
    id: int
    url: str
    title: str
    summary: Optional[str]
    key_entities: dict | None
    sections: list[str] | None
    quiz: List[Question]
    related_topics: list[str]

    class Config:
        orm_mode = True
