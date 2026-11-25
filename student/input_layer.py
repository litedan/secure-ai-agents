"""Задание 1. Вход: что бот принимает от пользователя (глава III лекции).

Сейчас бот пропускает любой текст любой длины от любого числа запросов. Исправьте:

  1. sanitize_input(text, max_len)
       - вырезать невидимые символы: нулевой ширины (U+200B…U+200F, U+2060, U+FEFF) и
         «символы-теги» U+E0000…U+E007F, а также управляющие символы (кроме \\n и \\t);
       - привести текст к нормальной форме Юникода (unicodedata.normalize("NFKC", ...)):
         так «ｉｇｎｏｒｅ» из полноширинных букв превращается в обычное «ignore»;
       - если после очистки текст пустой или длиннее max_len — выбросить InputRejected.
         Не обрезайте молча: обрезанный запрос может поменять смысл.
  2. RateLimiter — не больше `limit` запросов от одного пользователя за `window_s` секунд.
       Окно скользящее: запросы старше window_s секунд не считаются. Пользователи независимы.

Проверка: pytest tests/test_01_input.py
"""
import unicodedata
from collections import defaultdict, deque


class InputRejected(Exception):
    """Запрос не принят: слишком длинный, пустой или состоит из мусора."""


def sanitize_input(text: str, max_len: int = 2000) -> str:
    cleaned = []
    for ch in text:
        # «символы-теги» из блока Variations Selectors Supplement
        if "\U000e0000" <= ch <= "\U000e007f":
            continue
        # невидимые символы (нулевой ширины и т.п.) и управляющие, кроме \n и \t
        category = unicodedata.category(ch)
        if category == "Cf" or (category == "Cc" and ch not in "\n\t"):
            continue
        cleaned.append(ch)

    # NFKC превращает полноширинные буквы в обычные и т.п.
    result = unicodedata.normalize("NFKC", "".join(cleaned)).strip()

    if not result:
        raise InputRejected("пустой запрос или состоит из невидимых символов")
    if len(result) > max_len:
        raise InputRejected(f"запрос длиннее {max_len} символов")
    return result


class RateLimiter:
    def __init__(self, limit: int = 5, window_s: float = 60):
        self.limit = limit
        self.window_s = window_s
        self._history: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, user_id: str, now: float) -> bool:
        history = self._history[user_id]
        # скользящее окно: выбрасываем запросы старше window_s секунд
        while history and now - history[0] >= self.window_s:
            history.popleft()
        if len(history) >= self.limit:
            return False
        history.append(now)
        return True
