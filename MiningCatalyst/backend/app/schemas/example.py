from .base import Base

from sqlalchemy import Column, Integer, String


class RandomTable(Base):
    __tablename__ = "random_table"

    name = Column(String, index=True)
    random_value = Column(Integer)

    @property
    def is_good(self):
        return self.__check_if_good()

    def __check_if_good(self) -> bool:
        return self.random_value > 0
