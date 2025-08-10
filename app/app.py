import streamlit as st
import joblib
import numpy as np
import pandas as pd

# Загружаем модель
model = joblib.load("fraud_detection_xgb.pkl")

st.title("Fraud Detection App")
st.write("Проверка транзакций на мошенничество")

# --- Вкладки ---
mode = st.radio("Выберите режим:", ["Вручную", "CSV"])

# --- Режим вручную ---
if mode == "Вручную":
    st.subheader("Ручной ввод")
    st.write("Введите **30 чисел** через пробел или запятую в порядке: `Time, V1, V2, ..., V28, Amount`")

    input_string = st.text_area("Пример: 0, -1.3598, -0.07278, 2.5363, ..., 149.62", "")

    if st.button("Предсказать (вручную)"):
        try:
            # Разделяем строку по пробелам или запятым
            values = [float(x.replace(",", ".")) for x in input_string.replace(",", " ").split()]
            
            if len(values) != 30:
                st.error(f"❌ Должно быть 30 чисел, а вы ввели {len(values)}.")
            else:
                features = np.array([values])
                prediction = model.predict(features)[0]
                proba = model.predict_proba(features)[0][1]

                if prediction == 1:
                    st.error(f"⚠️ Мошенническая транзакция! Вероятность: {proba:.2%}")
                else:
                    st.success(f"✅ Транзакция нормальная. Вероятность мошенничества: {proba:.2%}")
        except ValueError:
            st.error("❌ Ошибка: убедитесь, что все введённые значения — числа.")

# --- Режим CSV ---
elif mode == "CSV":
    st.subheader("Загрузка CSV")
    st.write("CSV должен содержать **30 столбцов** в порядке: `Time, V1, ..., V28, Amount`")

    uploaded_file = st.file_uploader("Загрузите CSV файл", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if df.shape[1] != 30:
                st.error(f"❌ Должно быть 30 столбцов, а у вас {df.shape[1]}.")
            else:
                predictions = model.predict(df)
                probabilities = model.predict_proba(df)[:, 1]

                df['Prediction'] = predictions
                df['Fraud Probability'] = probabilities

                st.success("✅ Файл обработан!")
                st.dataframe(df)

                csv_output = df.to_csv(index=False).encode('utf-8')
                st.download_button("Скачать результаты", csv_output, "fraud_predictions.csv", "text/csv")
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")