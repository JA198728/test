import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="Проверка Тестов", layout="centered")

# Берем ключ из Secrets
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
TEACHER_PASSWORD = "admin" 
DATA_FILE = "results.csv"

if not API_KEY:
    st.error("Критическая ошибка: GOOGLE_API_KEY не найден в Secrets!")
    st.stop()

# Настройка Google AI с автоматическим выбором модели
genai.configure(api_key=API_KEY)

@st.cache_resource
def get_model():
    """Функция для поиска доступной модели, чтобы избежать ошибки 404"""
    try:
        # Пытаемся найти самую современную модель
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Приоритет выбора:
        for model_name in ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.5-flash-latest']:
            if model_name in available_models:
                return genai.GenerativeModel(model_name)
        # Если ничего из списка не нашли, берем первую доступную
        return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"Не удалось инициализировать модель: {e}")
        return None

model = get_model()

# --- 2. ИНТЕРФЕЙС ---
st.sidebar.title("Навигация")
role = st.sidebar.radio("Выберите роль:", ["Ученик", "Учитель"])

# --- 3. РЕЖИМ УЧЕНИКА ---
if role == "Ученик":
    st.title("📝 Сдача теста")
    
    with st.form("student_form", clear_on_submit=True):
        fio = st.text_input("Ваше ФИО")
        answers = st.text_area("Ваши ответы (например: 1-а, 2-б...)", height=150)
        submitted = st.form_submit_button("Отправить")
        
        if submitted:
            if fio and answers:
                new_row = pd.DataFrame([{"ФИО": fio, "Ответы": answers}])
                if os.path.exists(DATA_FILE):
                    df = pd.read_csv(DATA_FILE)
                    df = pd.concat([df, new_row], ignore_index=True)
                else:
                    df = new_row
                df.to_csv(DATA_FILE, index=False)
                st.success(f"Ответы для {fio} успешно сохранены!")
                st.balloons()
            else:
                st.warning("Заполните все поля!")

# --- 4. РЕЖИМ УЧИТЕЛЯ ---
elif role == "Учитель":
    st.title("🔐 Панель учителя")
    password = st.text_input("Введите пароль", type="password")
    
    if password == TEACHER_PASSWORD:
        if os.path.exists(DATA_FILE):
            df_view = pd.read_csv(DATA_FILE)
            st.write("### Ответы учеников:")
            st.dataframe(df_view)
            
            st.divider()
            st.write("### 🤖 Проверка ИИ")
            etalon = st.text_area("Введите правильные ответы (эталон)")
            
            if st.button("🚀 Запустить проверку"):
                if etalon and model:
                    with st.spinner('ИИ проверяет работы...'):
                        try:
                            # Формируем список ответов для ИИ
                            student_responses = ""
                            for _, row in df_view.iterrows():
                                student_responses += f"Ученик: {row['ФИО']}\nОтветы: {row['Ответы']}\n\n"
                            
                            prompt = f"""
                            Проверь ответы учеников по эталону. 
                            ЭТАЛОН: {etalon}
                            ОТВЕТЫ: {student_responses}
                            
                            Выдай таблицу Markdown: ФИО | Оценка | Ошибки.
                            Будь лоялен к опечаткам.
                            """
                            
                            response = model.generate_content(prompt)
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Ошибка ИИ: {e}")
                elif not model:
                    st.error("Модель ИИ не инициализирована.")
                else:
                    st.warning("Введите эталон!")
        else:
            st.info("Ответов пока нет.")
    elif password != "":
        st.error("Неверный пароль")







