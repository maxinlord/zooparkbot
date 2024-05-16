from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase, AsyncAttrs):
    
    idpk: Mapped[int] = mapped_column(Integer, primary_key=True)

    repr_cols_num = 3
    repr_cols = ()
    
    def __repr__(self):
        cols = [
            f"{col}={getattr(self, col)}"
            for idx, col in enumerate(self.__table__.columns.keys())
            if col in self.repr_cols or idx < self.repr_cols_num
        ]
        return f"<{self.__class__.__name__} {', '.join(cols)}>"