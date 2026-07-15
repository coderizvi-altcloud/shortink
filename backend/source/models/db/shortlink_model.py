from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from backend.source.config.database import Base


class ShortlinkModel(Base):
    __tablename__ = "shortlink"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(unique=True, index=True)
    short_code: Mapped[str] = mapped_column(unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    click_count: Mapped[int] = mapped_column(default=0)
