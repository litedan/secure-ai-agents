"""Задание 3. База знаний: права читателя и приём документов (глава IV).

Сейчас поиск не знает, кто спрашивает: гость получает зарплатные ведомости. Документы
принимаются в индекс без проверки: из них можно подложить скрытую инструкцию. Исправьте:

  1. retrieve(query, user, chunks, k, score) — вернуть k самых подходящих чанков, но
     ТОЛЬКО из доступных читателю: у чанка есть поле "group", у читателя — список user["groups"].
     Фильтр применяется ДО отбора лучших k. Если сначала взять топ-k, а потом отфильтровать,
     читатель может остаться с пустой выдачей, и это ломает стенд ACL из лекции.
     score(query, text) — готовая функция оценки релевантности. Сортируйте по убыванию оценки.
  2. is_trusted_source(source) — доверять только источникам, начинающимся с "kb/" и без «..».
  3. clean_document(text) — очистить текст при приёме в индекс: убрать HTML-комментарии
     <!-- ... -->, элементы со стилем display:none или белым цветом текста
     (color:#fff / color:white), символы нулевой ширины. Видимый текст сохранить.

Проверка: pytest tests/test_03_rag.py
"""


import re


def retrieve(query: str, user: dict, chunks: list, k: int, score) -> list:
    # сначала фильтр по правам, и только потом отбор лучших k
    allowed = set(user.get("groups", []))
    visible = [c for c in chunks if c.get("group") in allowed]
    ranked = sorted(visible, key=lambda c: -score(query, c["text"]))
    return ranked[:k]


def is_trusted_source(source: str) -> bool:
    return source.startswith("kb/") and ".." not in source


_COMMENT = re.compile(r"<!--.*?-->", re.S)
# элемент (с любым текстом до style) со скрытым содержимым: целиком с телом
_HIDDEN = re.compile(
    r"<\w+[^>]*(?:display\s*:\s*none|color\s*:\s*(?:#fff(?:fff)?|white\b))[^>]*>.*?</\w+>",
    re.S | re.I,
)
_ZWSP = re.compile("[\u200b-\u200f\u2060\ufeff]")


def clean_document(text: str) -> str:
    text = _COMMENT.sub("", text)
    text = _HIDDEN.sub("", text)
    return _ZWSP.sub("", text)
