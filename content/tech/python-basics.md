---
title: Python 基础笔记
summary: Python 语言基础回顾
published: true
---

# Python 基础笔记

## 数据类型

| 类型 | 示例 | 说明 |
|------|------|------|
| int | `42` | 整数 |
| float | `3.14` | 浮点数 |
| str | `"hello"` | 字符串 |
| list | `[1, 2, 3]` | 列表 |
| dict | `{"a": 1}` | 字典 |

## 列表推导式

```python
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]
```

## 装饰器

```python
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper
```
