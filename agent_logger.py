
import logging
from pathlib import Path

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage


# ============================================================
# НАСТРОЙКА ЛОГГЕРА
# ============================================================

logger = logging.getLogger("agent")
logger.setLevel(logging.DEBUG)

# Не передавать сообщения повторно в root logger
logger.propagate = False

# Файл логов располагается рядом с agent_logger.py
LOG_FILE = Path(__file__).resolve().parent / "agent.log"

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Добавляем файловый обработчик только один раз
file_handler_exists = any(
    isinstance(handler, logging.FileHandler)
    and Path(handler.baseFilename) == LOG_FILE
    for handler in logger.handlers
)

if not file_handler_exists:
    file_handler = logging.FileHandler(
        LOG_FILE,
        mode="a",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# ============================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# ============================================================

def log_step(step_name: str, details: str = ""):
    """Логирует отдельный этап работы агента."""
    logger.info("[%s] %s", step_name, details)


# ============================================================
# MIDDLEWARE ДЛЯ LANGCHAIN
# ============================================================

class LoggingMiddleware(AgentMiddleware):
    """
    Логирует:
    - сообщения перед вызовом модели;
    - решения модели о вызове инструментов;
    - результаты инструментов;
    - финальные ответы;
    - информацию о токенах и модели.
    """

    def __init__(self):
        super().__init__()
        self.step_counter = 0

    # --------------------------------------------------------
    # Перед вызовом LLM
    # --------------------------------------------------------

    def before_model(self, state, runtime):
        self.step_counter += 1
        logger.debug(f"STEP #{self.step_counter} | BEFORE_MODEL")
        messages = state.get("messages", [])

        if messages:
            last_msg = messages[-1]
            content = getattr(last_msg, "content", str(last_msg))

            logger.debug(
                "BEFORE_MODEL | последнее сообщение: %s",
                str(content)[:500]
            )

        return None

    # --------------------------------------------------------
    # После вызова LLM
    # --------------------------------------------------------

    def after_model(self, state, runtime):
        messages = state.get("messages", [])

        if not messages:
            return None

        last_msg = messages[-1]

        # Проверяем, запросила ли модель вызов инструмента
        tool_calls = getattr(last_msg, "tool_calls", None)

        if tool_calls:
            for tool_call in tool_calls:
                logger.info(
                    "MODEL_DECISION | tool=%s | args=%s | id=%s",
                    tool_call.get("name"),
                    tool_call.get("args"),
                    tool_call.get("id", "n/a")
                )

        else:
            # Если инструментов нет — логируем ответ модели
            content = getattr(last_msg, "content", "")

            if content:
                logger.info(
                    "MODEL_RESPONSE | %s",
                    str(content)[:1000]
                )

        # Информация об использовании токенов
        usage = getattr(last_msg, "usage_metadata", None)

        if usage:
            logger.info(
                "TOKENS | input=%s | output=%s | total=%s",
                usage.get("input_tokens", 0),
                usage.get("output_tokens", 0),
                usage.get("total_tokens", 0)
            )

        # Информация о модели
        response_meta = getattr(last_msg, "response_metadata", {}) or {}

        model_name = (
            response_meta.get("model_name")
            or response_meta.get("model")
            or "unknown"
        )

        logger.debug("MODEL | %s", model_name)

        return None

    # --------------------------------------------------------
    # Вызов инструмента
    # --------------------------------------------------------

    def wrap_tool_call(self, request, handler):
        tool_call = request.tool_call

        tool_name = tool_call.get("name", "unknown")
        tool_args = tool_call.get("args", {})

        logger.info(
            "TOOL_CALL | %s | аргументы: %s",
            tool_name,
            tool_args
        )

        try:
            # Выполняем инструмент
            result = handler(request)

            # Логируем результат
            if isinstance(result, ToolMessage):
                result_content = result.content
            else:
                result_content = str(result)

            logger.info(
                "TOOL_RESULT | %s | результат: %s",
                tool_name,
                str(result_content)[:1000]
            )

            return result

        except Exception:
            logger.exception(
                "TOOL_ERROR | %s | ошибка выполнения инструмента",
                tool_name
            )
            raise


# ============================================================
# ПРОВЕРКА ЛОГГЕРА
# ============================================================

# if __name__ == "__main__":
#     logger.info("TEST INFO | Логгер работает")
#     logger.debug("TEST DEBUG | Отладочная запись")
#     logger.warning("TEST WARNING | Тест предупреждения")
#     logger.error("TEST ERROR | Тест ошибки")

#     print(f"Тестовые записи сохранены в: {LOG_FILE}")




# import logging
# from pathlib import Path

# LOG_FILE = Path(__file__).resolve().parent / "agent.log"

# logger = logging.getLogger("agent_test")
# logger.setLevel(logging.DEBUG)
# logger.propagate = False

# handler = logging.FileHandler(
#     LOG_FILE,
#     mode="a",
#     encoding="utf-8"
# )

# handler.setLevel(logging.DEBUG)
# handler.setFormatter(
#     logging.Formatter(
#         "%(asctime)s | %(levelname)s | %(message)s"
#     )
# )

# logger.addHandler(handler)

# logger.info("TEST INFO")
# logger.debug("TEST DEBUG")
# logger.warning("TEST WARNING")
# logger.error("TEST ERROR")

# handler.flush()
# handler.close()

# print(f"Файл: {LOG_FILE}")
# print(f"Размер: {LOG_FILE.stat().st_size} байт")
