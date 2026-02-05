import streamlit as st  # ПРОВЕРЬТЕ ЭТУ СТРОКУ!
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- НАСТРОЙКИ ---
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = "AIzaSy..." # Ваш ключ

TEACHER_PASSWORD = "admin"

# Подключение к Google Таблице
conn = st.connection("gsheets", type=GSheetsConnection)

# --- РЕЖИМ УЧЕНИКА ---
st.sidebar.title("Навигация")
role = st.sidebar.radio("Кто вы?", ["Ученик", "Учитель"])

if role == "Ученик":
    st.title("📝 Тестирование")
    with st.form("student_form"):
        fio = st.text_input("Ваше ФИО")
        answers = st.text_area("Ваши ответы")
        submitted = st.form_submit_button("✅ Отправить")
        
        if submitted:
            if fio and answers:
                try:
                    # Читаем текущие данные (ttl=0 значит не использовать кэш, читать сразу)
                    existing_data = conn.read(worksheet="Sheet1", ttl=0)
                except Exception:
                    # Если таблица пустая или ошибка чтения — создаем пустой список
                    existing_data = pd.DataFrame(columns=["ФИО", "Ответы"])
                
                # Создаем новую строчку
                new_row = pd.DataFrame([{"ФИО": fio, "Ответы": answers}])
                
                # Соединяем старое с новым
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                
                # Отправляем обратно в Google
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success(f"Спасибо, {fio}! Ваши ответы записаны.")
                st.balloons() # Немного праздника при успешной отправке!
            else:
                st.warning("Пожалуйста, заполните все поля!")

# Режим учителя остается таким же, но данные он будет брать из conn.read()

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




