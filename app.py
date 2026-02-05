import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

st.set_page_config(page_title="ИИ-Анализатор МОДО", layout="wide")

API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
DATA_FILE = "analysis_results.csv"

if not API_KEY:
    st.error("Ключ API отсутствует!")
    st.stop()

genai.configure(api_key=API_KEY)

# --- ДИНАМИЧЕСКИЙ ПОДБОР МОДЕЛИ (Лечит 404) ---
@st.cache_resource
def get_working_model():
    try:
        # Пытаемся найти все доступные модели в аккаунте
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Приоритет отдаем flash, если нет - берем любую рабочую
        target = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
        return genai.GenerativeModel(target)
    except Exception as e:
        st.error(f"Не удалось получить список моделей: {e}")
        return None

model = get_working_model()

st.title("🔬 Лаборатория анализа ИИ")
st.info("Цель: Проверить, как ИИ интерпретирует сложные данные из PDF МОДО-2022")

# --- СТРУКТУРА ДЛЯ АНАЛИЗА ---
task_type = st.selectbox("Что анализируем?", 
    ["Логический вывод (Математика)", "Контекстный анализ (Чтение)", "Причинно-следственные связи (Химия/Биология)"])

context_text = st.text_area("Вставьте фрагмент из PDF для анализа:", height=200)
user_question = st.text_input("Ваш проверочный вопрос к ИИ:")

if st.button("Запустить анализ ИИ"):
    if context_text and user_question:
        with st.spinner("ИИ препарирует текст..."):
            try:
                # Специальный промпт для анализа (а не просто ответа)
                full_prompt = f"""
                Действуй как аналитик данных. Перед тобой текст из сборника МОДО:
                '{context_text}'
                
                Проанализируй этот текст и ответь на вопрос: '{user_question}'
                В своем ответе:
                1. Укажи на конкретные факты из текста.
                2. Объясни свою логику (почему ты считаешь этот ответ верным).
                3. Оцени сложность вопроса для ИИ по шкале от 1 до 10.
                """
                
                response = model.generate_content(full_prompt)
                
                st.subheader("Результат анализа:")
                st.write(response.text)
                
                # Сохраняем логи для твоего исследования
                log_data = pd.DataFrame([{"Тип": task_type, "Вопрос": user_question, "Ответ": response.text}])
                if os.path.exists(DATA_FILE):
                    pd.concat([pd.read_csv(DATA_FILE), log_data]).to_csv(DATA_FILE, index=False)
                else:
                    log_data.to_csv(DATA_FILE, index=False)
                    
            except Exception as e:
                st.error(f"Ошибка при генерации: {e}")
    else:
        st.warning("Заполните данные для анализа!")

if st.sidebar.button("Скачать лог анализа"):
    if os.path.exists(DATA_FILE):
        st.sidebar.download_button("Скачать CSV", pd.read_csv(DATA_FILE).to_csv(), "logs.csv")
