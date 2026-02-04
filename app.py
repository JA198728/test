import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# --- НАСТРОЙКИ ---
# Приоритет ключу из "Secrets", если его нет - берем ваш текстовый ключ
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = "AIzaSyBm67o0GkwhDlBuqkZ9tfLpTnotvvG8HoI"

TEACHER_PASSWORD = "admin" 

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- ГЛАВНОЕ МЕНЮ ---
st.sidebar.title("Навигация")
role = st.sidebar.radio("Кто вы?", ["Ученик", "Учитель"])

# --- РЕЖИМ УЧЕНИКА ---
if role == "Ученик":
    st.title("📝 Тестирование")
    st.info("Пожалуйста, заполните форму ниже. Ваши ответы будут переданы учителю.")
    
    with st.form("student_form"):
        fio = st.text_input("Ваше ФИО (полностью)")
        answers = st.text_area("Введите ваши ответы (например: 1-а, 2-б, 3-в)")
        
        submitted = st.form_submit_button("✅ Отправить ответы")
        
        if submitted:
            if fio and answers:
                new_data = pd.DataFrame({"ФИО": [fio], "Ответы": [answers]})
                
                # Работа с файлом в облаке
                file_path = "spisok.xlsx"
                if os.path.exists(file_path):
                    try:
                        df = pd.read_excel(file_path)
                        df = pd.concat([df, new_data], ignore_index=True)
                    except:
                        df = new_data
                else:
                    df = new_data
                
                df.to_excel(file_path, index=False)
                st.success(f"Спасибо, {fio}! Ваши ответы успешно сохранены.")
            else:
                st.warning("Заполните все поля!")

# --- РЕЖИМ УЧИТЕЛЯ ---
elif role == "Учитель":
    st.title("🔐 Панель учителя")
    
    password = st.text_input("Введите пароль для доступа к проверке", type="password")
    
    if password == TEACHER_PASSWORD:
        st.success("Доступ разрешен!")
        
        etalon = st.text_area("Введите эталон правильных ответов")
        
        if st.button("🚀 Начать проверку ИИ"):
            if os.path.exists("spisok.xlsx") and etalon:
                try:
                    df = pd.read_excel("spisok.xlsx")
                    student_data = df.to_string(index=False)
                    
                    prompt = f"Эталон: {etalon}\nДанные учеников:\n{student_data}\nПроверь и выведи таблицу с оценками."
                    
                    response = model.generate_content(prompt)
                    st.markdown("### Результаты анализа:")
                    st.write(response.text)
                    st.balloons()
                except Exception as e:
                    st.error(f"Ошибка: {e}")
            else:
                st.warning("Файл с ответами пуст или не введен эталон!")
    elif password != "":
        st.error("Неверный пароль!")
