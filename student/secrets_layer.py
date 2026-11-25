"""Задание 6. Секреты: короткая жизнь и никаких ключей в журнале (глава VI).

Сейчас «токен доступа» живёт 90 дней и подходит ко всем задачам, а журнал хранит всё, что
пользователь написал, в том числе вставленные ключи.

  1. TokenVault — выдаёт и проверяет токены.
       issue(scope, now, ttl_s=None) -> {"token": str, "scope": str, "expires_at": float}
         срок по умолчанию 300 секунд; запросить можно не больше 3600, больший срок срезается;
       check(token, scope, now) -> bool — истина, только если токен выдан этим хранилищем,
         не истёк, не отозван и выдан именно для этой области (scope);
       revoke(token) — отзыв: после него check всегда False.
     Токены генерируйте через secrets.token_urlsafe, не random: random предсказуем.
  2. redact(text) — заменить на «[СКРЫТО]» всё, что похоже на секрет:
       sk-... и tvly-... (после префикса не меньше 8 символов из букв, цифр, «-» и «_»),
       «Bearer <токен>», пары вида api_key=..., token: ..., password=... (регистр не важен).

Проверка: pytest tests/test_06_secrets.py
"""
import re
import secrets

DEFAULT_TTL_S = 300     # срок жизни по умолчанию
MAX_TTL_S = 3600        # потолок: дольше не бывает


class TokenVault:
    def __init__(self):
        self._tokens = {}

    def issue(self, scope: str, now: float, ttl_s: float | None = None) -> dict:
        ttl = DEFAULT_TTL_S if ttl_s is None else min(ttl_s, MAX_TTL_S)
        token = secrets.token_urlsafe(32)   # предсказуемый random тут не годится
        record = {"scope": scope, "expires_at": now + ttl, "revoked": False}
        self._tokens[token] = record
        return {"token": token, "scope": scope, "expires_at": record["expires_at"]}

    def check(self, token: str, scope: str, now: float) -> bool:
        record = self._tokens.get(token)
        if record is None or record["revoked"]:
            return False
        if now >= record["expires_at"]:
            return False
        return record["scope"] == scope

    def revoke(self, token: str) -> None:
        if token in self._tokens:
            self._tokens[token]["revoked"] = True


_SECRET_PATTERNS = [
    re.compile(r"\b(?:sk|tvly)-[\w-]{8,}"),          # sk-... и tvly-...
    re.compile(r"\bBearer\s+\S+", re.I),             # Bearer <токен>
    re.compile(r"\b(?:api_key|token|password)\s*[=:]\s*\S+", re.I),  # пары ключ=значение
]


def redact(text: str) -> str:
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[СКРЫТО]", text)
    return text
