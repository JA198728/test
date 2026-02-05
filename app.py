import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from datetime import datetime

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="Исследование: ИИ-Анализ МОДО", layout="wide")

API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
DATA_FILE = "modo_research_results.csv"

if not API_KEY:
    st.error("Ошибка: Добавьте GOOGLE_API_KEY в Secrets!")
    st.stop()

# НАСТРОЙКА ИИ (Динамический поиск рабочей модели)
genai.configure(api_key=API_KEY)

@st.cache_resource
def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in models if 'gemini-1.5-flash' in m), models[0])
        return genai.GenerativeModel(target)
    except Exception as e:
        st.error(f"Системная ошибка доступа к ИИ: {e}")
        return None

model = get_working_model()

# --- 2. ИНТЕРФЕЙС ПРИВЕТСТВИЯ ---
st.title("📚 Тестирование")
st.info("Добро пожаловать! Ваши ответы будут проанализированы ИИ для выявления пробелов в знаниях.")

fio = st.text_input("👤 Введите ваше фамилию и имя, чтобы начать тест:")

if not fio:
    st.warning("Пожалуйста, введите данные выше, чтобы получить доступ к заданиям.")
    st.stop()

# --- 3. ИНТЕРФЕЙС ТЕСТИРОВАНИЯ ---
st.success(f"Привет, {fio}! Желаем удачи в прохождении теста.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Блок А")
        q1 = st.radio("1. Основной орган выделительной системы (фильтр):", 
                      ["Почки", "Печень", "Легкие", "Кишечник"], index=None)
        q2 = st.radio("2. Структурно-функциональная единица почки:", 
                      ["Лоханка", "Нефрон", "Пирамида", "Капсула"], index=None)
    
    with col2:
        st.write("### Блок Б")
        q3 = st.radio("3. Процесс фильтрации крови происходит в:", 
                      ["Мочеточниках", "Лоханке", "Капиллярном клубочке"], index=None)
        q4 = st.radio("4. В состав первичной мочи в норме НЕ входит:", 
                      ["Глюкоза", "Белок", "Вода", "Витамины"], index=None)

# --- 4. ЛОГИКА АНАЛИЗА ---
if st.button("🚀 Сдать тест и получить ИИ-анализ"):
    if None in [q1, q2, q3, q4]:
        st.error("Ошибка: Пожалуйста, ответьте на ВСЕ вопросы теста!")
    else:
        with st.spinner("ИИ анализирует ваши ответы..."):
            student_data = f"""
            Ученик: {fio}
            Ответы:
            1. Орган-фильтр: {q1} (Верно: Почки)
            2. Единица почки: {q2} (Верно: Нефрон)
            3. Место фильтрации: {q3} (Верно: Капиллярном клубочке)
            4. Состав мочи: {q4} (Верно: Белок)
            """
            
            try:
                analysis_prompt = f"""
                Ты — эксперт-педагог и аналитик. Проанализируй ответы ученика {fio}:
                {student_data}
                
                Твоя задача:
                1. Выдай итоговый балл (из 4).
                2. Опиши, какие темы усвоены, а какие нет.
                3. Объясни ученику суть его ошибок с точки зрения биологии.
                4. Дай краткую рекомендацию по изучению PDF-сборника МОДО.
                """
                
                response = model.generate_content(analysis_prompt)
                analysis_text = response.text
                
                st.markdown("---")
                st.subheader("🔍 Результаты ИИ-анализа:")
                st.write(analysis_text)
                
                result_row = pd.DataFrame([{
                    "Дата": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "ФИО": fio,
                    "Ответы": student_data.replace('\n', ' '),
                    "Анализ_ИИ": analysis_text
                }])
                
                if os.path.exists(DATA_FILE):
                    result_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                else:
                    result_row.to_csv(DATA_FILE, index=False)
                
                st.balloons()
                    
            except Exception as e:
                st.error(f"Ошибка ИИ: {e}")

# --- 5. КАБИНЕТ УЧИТЕЛЯ ---
st.markdown("---")
with st.expander("🔐 Вход для Учителя"):
    pass_input = st.text_input("Введите пароль доступа:", type="password")
    if pass_input == "admin":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            st.dataframe(df)
            st.download_button("📥 Скачать таблицу (CSV)", df.to_csv(index=False).encode('utf-8'), "results.csv", "text/csv")
        else:
            st.info("Данных пока нет.")

