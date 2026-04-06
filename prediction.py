import pandas as pd
import psycopg2
import numpy as np
from sklearn.linear_model import LinearRegression
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD


def get_db_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    query = """
        SELECT temperature, humidity, recorded_at
        FROM sensor_data
        ORDER BY recorded_at
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def predict_future(steps=None):
    df = get_db_data()

    df["timestamp"]=pd.to_datetime(df["recorded_at"])
    df["hour"]= df["timestamp"].dt.hour
    df["minute"]= df["timestamp"].dt.minute

    df["time_in_hours"]=df["hour"]+df["minute"]/60.0

    df["sin_time"]=np.sin(2*np.pi*df["time_in_hours"]/24)
    df["cos_time"]=np.cos(2*np.pi*df["time_in_hours"]/24)

    X = df[["sin_time", "cos_time"]]
    temp_model = LinearRegression()
    temp_model.fit(X, df["temperature"])

    hum_model = LinearRegression()
    hum_model.fit(X, df["humidity"])
    step_size_minutes = 5
    if steps is None:
        steps = int((24 * 60)/step_size_minutes)
    last_timestamp = df["timestamp"].iloc[-1]

    predictions = []

    for i in range(steps):
        future_timestamp=last_timestamp+pd.Timedelta(minutes=step_size_minutes*(i+1))

        hour=future_timestamp.hour
        minute=future_timestamp.minute

        time_in_hours=hour+minute/60.0

        sin_time = np.sin(2*np.pi*time_in_hours/24)
        cos_time = np.cos(2*np.pi*time_in_hours/24)

        X_future = np.array([[sin_time, cos_time]])

        temp_pred = temp_model.predict(X_future)[0]*9/5+32
        hum_pred = hum_model.predict(X_future)[0]

        predictions.append({
            "time": future_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": float(temp_pred),
            "humidity": float(hum_pred)
        })

    return predictions


if __name__ == "__main__":
    preds = predict_future()

    for p in preds[:24]:
        print(p)