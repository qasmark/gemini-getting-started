import google.generativeai as genai
import os
import time
from collections import deque
from datetime import datetime
from dotenv import load_dotenv


_API_QUOTA_EXCEEDED_MESSAGE = "Превышена квота API. Попробуйте позже или проверьте лимиты."
_HISTORY_LENGTH = 10
_DEFAULT_REQUEST_DELAY = 1

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
_model = genai.GenerativeModel("gemini-pro")
_chat_history = deque(maxlen=_HISTORY_LENGTH)


def _send_message(message: str) -> str:
    response = _model.generate_content(message)
    _chat_history.append({"role": "user", "content": message, "timestamp": datetime.now()})
    _chat_history.append({"role": "gemini", "content": response.text, "timestamp": datetime.now()})
    return response.text


def _show_chat_history() -> None:
    print("\nИстория чата:")
    for message in _chat_history:
        print(f"[{message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] {message['role'].capitalize()}: {message['content']}")
    print("-" * 30)


def _get_api_usage_info() -> None:
    try:
        response = _model.count_tokens("test")
        print("Информация об использовании API:")
        if response and hasattr(response, "prompt_tokens") and hasattr(response, "total_billable_characters"):
            print(f"  Пробные токены (пример): {response.prompt_tokens}")
            print(f"  Всего тарифицируемых символов (пример): {response.total_billable_characters}")
        else:
            print("  Не удалось получить информацию об использовании API.")
    except Exception as e:
        print(f"Ошибка при получении информации об использовании API: {e}")

    print("  (Информация о QPM недоступна в стандартном API)")


def _print_gemini_response(response: str) -> None:
    print("Gemini:", response)
    print("-" * 30)


def _add_request_delay(delay_seconds: float = _DEFAULT_REQUEST_DELAY) -> None:
    time.sleep(delay_seconds)


def _process_user_input() -> None:
    print("Добро пожаловать в чат с Gemini!")
    print("Введите 'выход' для завершения, 'история' для просмотра истории, 'лимиты' для информации об API.")

    while True:
        user_message = input("Вы: ")

        if user_message.lower() == "выход":
            break
        elif user_message.lower() == "история":
            _show_chat_history()
        elif user_message.lower() == "лимиты":
            _get_api_usage_info()
        else:
            try:
                gemini_response = _send_message(user_message)
                _print_gemini_response(gemini_response)
                _add_request_delay()
            except Exception as e:
                print(f"Ошибка при отправке запроса: {e}")
                if "Quota exceeded" in str(e):
                    print(_API_QUOTA_EXCEEDED_MESSAGE)
                    _get_api_usage_info()
                break


if __name__ == "__main__":
    _process_user_input()