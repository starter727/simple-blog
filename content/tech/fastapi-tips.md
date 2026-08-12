---
title: FastAPI 实用技巧
summary: 一些 FastAPI 开发中的实用技巧
published: true
---

# FastAPI 实用技巧

## 1. 依赖注入

FastAPI 的依赖注入系统非常强大：

```python
from fastapi import Depends

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
async def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

## 2. 中间件

```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

返回查看：[[hello-world|Hello World]]
