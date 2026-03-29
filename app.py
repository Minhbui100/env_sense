from flask import Flask, jsonify, render_template, request
import psycopg2
from prediction import predict_future


app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="environment",
        user="postgres",
        password="postgres"
    )


@app.route("/api/data")
def get_data():

    conn = get_db_connection()
    cur = conn.cursor()

    time_range = request.args.get("range", "today")

    if time_range == "today":
        filt = "date(s.recorded_at)=current_date"
    elif time_range == "24h":
        filt = "s.recorded_at >= NOW() - INTERVAL '24 hours'"
    else:
        filt = "s.recorded_at >= NOW() - INTERVAL '7 days'"

    query = f"""
        SELECT 
            s.id,
            s.device,
            s.temperature AS inside_temp,
            s.humidity AS inside_humidity,
            o.temperature AS outside_temp,
            o.humidity AS outside_humidity,
            s.recorded_at 
        FROM sensor_data s
        JOIN outside_data o
        ON ABS(EXTRACT(EPOCH FROM (s.recorded_at-o.recorded_at)))<120
        WHERE {filt}
        ORDER BY recorded_at;
    """

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    data = [
        {
            "id": r[0],
            "device": r[1],
            "inside_temp": r[2]*9/5+32,
            "inside_humidity": r[3],
            "outside_temp": r[4],
            "outside_humidity": r[5],
            "recorded_at": r[6].strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in rows
    ]


    return jsonify(data)


@app.route("/api/current")
def outside_temp():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            s.id,
            s.device,
            s.temperature AS inside_temp,
            s.humidity AS inside_humidity,
            o.temperature AS outside_temp,
            o.humidity AS outside_humidity,
            s.recorded_at 
        FROM sensor_data s
        JOIN outside_data o
        ON ABS(EXTRACT(EPOCH FROM (s.recorded_at-o.recorded_at)))<120
        ORDER BY recorded_at desc
        limit 1;
    """)

    r = cur.fetchone()

    cur.close()
    conn.close()

    data = [
        {
            "id": r[0],
            "device": r[1],
            "inside_temp": r[2]*9/5+32,
            "inside_humidity": r[3],
            "outside_temp": r[4],
            "outside_humidity": r[5],
            "recorded_at": r[6].strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    return jsonify(data)


@app.route("/api/predict")
def predict():
    preds = predict_future(steps=120)
    return jsonify(preds)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)