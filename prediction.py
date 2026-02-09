import pandas as pd
import psycopg2
import numpy as np
from sklearn.linear_model import LinearRegression


def get_db_data():
    conn = psycopg2.connect(
        host="localhost",
        database="environment",
        user="postgres",
        password="Dynamic@00"
    )

    query = """
        SELECT temperature, humidity, timestamp
        FROM dht11
        ORDER BY timestamp
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df

# Predict in 2 hours
def predict_future(steps=1442):
    df = get_db_data()

    df["time_index"] = np.arange(len(df))

    X = df[["time_index"]]

    temp_model = LinearRegression()
    temp_model.fit(X, df["temperature"])

    hum_model = LinearRegression()
    hum_model.fit(X, df["humidity"])

    future_index = np.arange(len(df), len(df) + steps).reshape(-1, 1)

    temp_preds = temp_model.predict(future_index)
    hum_preds = hum_model.predict(future_index)

    predictions = []

    for i in range(steps):
        predictions.append({
            "temperature": float(temp_preds[i]),
            "humidity": float(hum_preds[i])
        })

    return predictions