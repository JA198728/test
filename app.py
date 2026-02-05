import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# --- 1. НАСТРОЙКИ (КЛЮЧИ И ПАРОЛИ) ---
# Пробуем взять ключ из Secrets, если нет - используем пустую строку (нужно вставить свой в Secrets)
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
TEACHER_PASSWORD = "admin" # Пароль для входа учителя
DATA_FILE = "results.csv"  # Файл, где хранятся ответы

# Настройка нейросети
if API_KEY:
    genai.configure(api_key=API_KEY)
    # Используем самую стабильную версию модели
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Ошибка: API ключ не найден в Secrets!")

# --- 2. ИНТЕРФЕЙС ---
st.set_page_config(page_title="Проверка Тестов", layout="centered")

st.sidebar.title("Меню")
role = st.sidebar.radio("Выберите роль:", ["Ученик", "Учитель"])

# --- 3. РЕЖИМ УЧЕНИКА ---
if role == "Ученик":
    st.title("📝 Тестирование")
    st.write("Пожалуйста, введите ваше имя и ответы на вопросы теста.")
    
    # Форма отправки
    with st.form("student_form", clear_on_submit=True):
        fio = st.text_input("Ваше ФИО")
        answers = st.text_area("Ваши ответы (например: 1-а, 2-б, 3-в...)", height=150)
        submitted = st.form_submit_button("Отправить ответы")
        
        if submitted:
            if fio and answers:
                # Создаем новую строку данных
                new_row = pd.DataFrame([{"ФИО": fio, "Ответы": answers}])
                
                # Сохраняем в CSV файл
                if os.path.exists(DATA_FILE):
                    df = pd.read_csv(DATA_FILE)
                    df = pd.concat([df, new_row], ignore_index=True)
                else:
                    df = new_row
                
                df.to_csv(DATA_FILE, index=False)
                st.success(f"Ответы для {fio} успешно сохранены!")
                st.balloons()
            else:
                st.warning("Пожалуйста, заполните все поля!")

# --- 4. РЕЖИМ УЧИТЕЛЯ ---
elif role == "Учитель":
    st.title("🔐 Панель управления")
    
    password = st.text_input("Введите пароль", type="password")
    
    if password == TEACHER_PASSWORD:
        st.success("Доступ открыт")
        
        # Проверяем, есть ли уже ответы
        if os.path.exists(DATA_FILE):
            df_view = pd.read_csv(DATA_FILE)
            st.write("### Таблица ответов учеников:")
            st.dataframe(df_view)
            
            # Кнопка скачивания таблицы
            csv_data = df_view.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Скачать таблицу (Excel/CSV)",
                data=csv_data,
                file_name="results.csv",
                mime="text/csv"
            )
            
            st.divider()
            
            # БЛОК ПРОВЕРКИ ИИ
            st.write("### 🤖 Автоматическая проверка ИИ")
            etalon = st.text_area("Вставьте эталон (правильные ответы)", placeholder="Например: 1-а, 2-б, 3-в...")
            
            if st.button("🚀 Запустить проверку ИИ"):
                if etalon:
                    with st.spinner('Gemini анализирует ответы...'):
                        try:
                            # Собираем данные учеников в текст для ИИ
                            student_responses = ""
                            for i, row in df_view.iterrows():
                                student_responses += f"Ученик: {row['ФИО']}\nОтветы: {row['Ответы']}\n\n"
                            
                            prompt = f"""
                            Ты — строгий, но справедливый учитель. Сравни ответы учеников с эталоном.
                            ЭТАЛОН:
                            {etalon}
                            
                            ОТВЕТЫ УЧЕНИКОВ:
                            {student_responses}
                            
                            Выведи результат в виде Markdown-таблицы:
                            | ФИО | Оценка | Комментарий |
                            Засчитывай ответ как правильный, если смысл совпадает, даже если есть опечатки.
                            """
                            
                            response = model.generate_content(prompt)
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Произошла ошибка при работе с ИИ: {e}")
                else:
                    st.warning("Введите правильные ответы для сравнения!")
        else:
            st.info("Пока никто не сдал тест.")
            
    elif password != "":
        st.error("Неверный пароль")






