"""Задание 5. Шлюз инструментов: код решает, что агенту можно (глава V).

Сейчас любой вызов инструмента разрешён. Модель можно уговорить на что угодно, поэтому
решение принимает код вне модели, по правилам.

  1. decide(tool, args) -> "allow" | "ask" | "deny". Правила:
       search_knowledge_base — allow
       web_search            — allow, но если запрос длиннее 200 символов или содержит «http» — deny
       read_file             — allow только для путей внутри docs/ (после нормализации пути:
                               posixpath.normpath; пути с «..», абсолютные и любые .env — deny)
       send_email            — адрес на @company.example: ask (нужно подтверждение человека);
                               любой другой адрес: deny
       write_file            — путь внутри drafts/: ask, иначе deny
       run_shell             — deny
       неизвестный инструмент — deny (fail-safe default: по умолчанию «нельзя»)
  2. Budget — не больше max_steps обращений к модели за один запрос. Метод spend() возвращает
     True, пока лимит не исчерпан, и False после. Лимит по умолчанию — 8.

Проверка: pytest tests/test_05_gateway.py
"""
import posixpath


def _norm(path: str) -> str:
    return posixpath.normpath(path)


def _inside(path: str, prefix: str) -> bool:
    """Путь (уже нормализованный) лежит внутри папки prefix."""
    return path == prefix or path.startswith(prefix + "/")


def decide(tool: str, args: dict) -> str:
    if tool == "search_knowledge_base":
        return "allow"

    if tool == "web_search":
        query = args.get("query", "")
        if len(query) > 200 or "http" in query.lower():
            return "deny"
        return "allow"

    if tool == "read_file":
        path = args.get("path", "")
        norm = _norm(path)
        name = posixpath.basename(norm).lower()
        # .., абсолютные пути и любые .env — всегда отказ
        if posixpath.isabs(path) or ".." in norm.split("/") or name.startswith(".env"):
            return "deny"
        return "allow" if _inside(norm, "docs") else "deny"

    if tool == "send_email":
        to = args.get("to", "")
        return "ask" if to.lower().endswith("@company.example") else "deny"

    if tool == "write_file":
        path = args.get("path", "")
        return "ask" if _inside(_norm(path), "drafts") else "deny"

    if tool == "run_shell":
        return "deny"

    # fail-safe default: неизвестный инструмент — «нельзя»
    return "deny"


class Budget:
    def __init__(self, max_steps: int = 8):
        self.max_steps = max_steps
        self.used = 0

    def spend(self) -> bool:
        if self.used >= self.max_steps:
            return False
        self.used += 1
        return True
