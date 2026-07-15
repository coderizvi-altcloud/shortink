# FastAPI + SQLAlchemy — Database, Model, Schema Notes

## 1. Database Engine Setup (`database.py`)

Core pieces every `database.py` needs:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql://user:password@host:port/database_name"

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Notes:**
- `DATABASE_URL` format: `postgresql://<user>:<password>@<host>:<port>/<db_name>`
- `Base` — every ORM model inherits from this
- `engine` — the actual DB connection
- `SessionLocal` — factory that creates DB sessions
- `get_db()` — dependency-injected into routes via `Depends(get_db)`, yields a session and always closes it after use

---

## 2. Making a Model (ORM)

Use `Mapped` + `mapped_column()` from SQLAlchemy, inheriting from `Base`.

```python
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class TableName(Base):
    __tablename__ = "table_name"

    field: Mapped[int] = mapped_column(primary_key=True)
```

**Golden rule for models:**
> Always store everything you *might* need later — think ahead about every field the table could realistically use (timestamps, counters, flags, foreign keys), not just what's needed right now.

---

## 3. Making Schemas (Pydantic)

Keep it to **three** schema types per resource, no more:

```
Base       →  shared fields common to all variants
XCreate    →  request schema (client → server)
Response   →  response schema (server → client)
```

**Naming convention:**
- Request schema → `XCreate`
- Response schema → `Response`

Use `Annotated` for field definitions in schemas:

```python
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

class XBase(BaseModel):
    field: Annotated[str, Field(min_length=1)]

class XCreate(XBase):
    pass

class XResponse(XBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
```

---

## 4. Quick Reference Table

| Concept | Tool Used |
|---|---|
| DB engine + session | `create_engine`, `sessionmaker` |
| Base class for models | `DeclarativeBase` |
| Model fields | `Mapped`, `mapped_column()` |
| Schema fields | `Annotated`, `Field()` |
| ORM → Pydantic conversion | `ConfigDict(from_attributes=True)` |

---

## 5. Mental Checklist

- [ ] Model = think **wide** — everything the table could ever store
- [ ] Schema = think **narrow** — only what this one endpoint needs
- [ ] `from_attributes=True` only needed on schemas that read from ORM objects
- [ ] Never hardcode secrets/passwords in `database.py` — pull from `.env` via `pydantic-settings`