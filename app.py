import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# --- НАСТРОЙКИ ---
# Берем ключ из Secrets (настройки в Streamlit Cloud)
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = "ВАШ_КЛЮЧ_ТУТ" # Резервный вариант

TEACHER_PASSWORD = "admin" # Пароль для входа учителя

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Путь к файлу с данными
DATA_FILE = "results.csv"

# --- ГЛАВНОЕ МЕНЮ ---
st.sidebar.title("Навигация")
role = st.sidebar.radio("Кто вы?", ["Ученик", "Учитель"])

# --- РЕЖИМ УЧЕНИКА ---
if role == "Ученик":
    st.title("📝 Тестирование")
    st.info("Введите ваше имя и ответы. Учитель получит их автоматически.")
    
    with st.form("student_form", clear_on_submit=True):
        fio = st.text_input("Ваше ФИО (полностью)")
        answers = st.text_area("Введите ваши ответы (например: 1-а, 2-б, 3-в)")
        submitted = st.form_submit_button("✅ Отправить ответы")
        
        if submitted:
            if fio and answers:
                new_row = pd.DataFrame([{"ФИО": fio, "Ответы": answers}])
                
                # Сохраняем данные локально в CSV
                if os.path.exists(DATA_FILE):
                    df = pd.read_csv(DATA_FILE)
                    df = pd.concat([df, new_row], ignore_index=True)
                else:
                    df = new_row
                
                df.to_csv(DATA_FILE, index=False)
                st.success(f"Спасибо, {fio}! Ваши ответы успешно отправлены.")
                st.balloons()
            else:
                st.warning("Пожалуйста, заполните все поля!")

# --- РЕЖИМ УЧИТЕЛЯ ---
elif role == "Учитель":
    st.title("🔐 Панель учителя")
    
    password = st.text_input("Введите пароль для доступа", type="password")
    
    if password == TEACHER_PASSWORD:
        st.success("Доступ разрешен!")
        
        # Блок просмотра данных
        if os.path.exists(DATA_FILE):
            df_view = pd.read_csv(DATA_FILE)
            st.write("### Список ответов учеников:")
            st.dataframe(df_view) # Показывает таблицу прямо на экране
            
            # Кнопка скачивания для Excel
            st.download_button(
                label="📥 Скачать таблицу ответов (CSV)",
                data=df_view.to_csv(index=False).encode('utf-8-sig'),
                file_name="answers.csv",
                mime="text/csv",
            )
            
            st.divider()
            
            # Блок проверки ИИ
           if st.button("🚀 Начать проверку через ИИ"):
                if etalon:
                    with st.spinner('ИИ анализирует ответы...'):
                        student_data_text = df_view.to_string(index=False)
                        
                        # Детальная инструкция для ИИ
                        prompt = f"""
                        Ты — опытный учитель. Проверь ответы учеников, основываясь на эталоне.
                        
                        ЭТАЛОН ПРАВИЛЬНЫХ ОТВЕТОВ:
                        {etalon}
                        
                        ОТВЕТЫ УЧЕНИКОВ:
                        {student_data_text}
                        
                        Твоя задача:
                        1. Сравнить каждый ответ ученика с эталоном.
                        2. Выставить оценку по 5-балльной шкале.
                        3. Кратко написать, в чем ошибка, если она есть.
                        4. Выведи результат в виде красивой таблицы Markdown.
                        """
                        
                        response = model.generate_content(prompt)
                        st.markdown("### 📊 Результаты проверки:")
                        st.write(response.text)
                else:
                    st.warning("Сначала введите эталон (правильные ответы)!")






