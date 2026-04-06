from flask import Flask, jsonify, render_template, request
import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from prediction import predict_future

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


@app.route("/api/data")
def get_data():
    time_range = request.args.get("range", "today")
    if time_range == "24h":
        filt = "s.recorded_at >= NOW() - INTERVAL '24 hours'"
        trunc = "minute"
    elif time_range == "7d":
        filt = "s.recorded_at >= NOW() - INTERVAL '7 days'"
        trunc = "minute"
    else:
        filt = "date(s.recorded_at) = current_date"
        trunc = "minute"

    query = f"""
        SELECT
            MIN(s.id) AS id,
            MIN(s.device) AS device,
            AVG(s.temperature) AS inside_temp,
            AVG(s.humidity) AS inside_humidity,
            AVG(o.temperature) AS outside_temp,
            AVG(o.humidity) AS outside_humidity,
            date_trunc('{trunc}', s.recorded_at) AS recorded_at
        FROM sensor_data s
        LEFT JOIN outside_data o
          ON ABS(EXTRACT(EPOCH FROM (s.recorded_at-o.recorded_at)))<180
        WHERE {filt}
        GROUP BY date_trunc('{trunc}', s.recorded_at)
        ORDER BY recorded_at;
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    data = [
        {
            "id": r[0],
            "device": r[1],
            "inside_temp": round(float(r[2])*9/5+32, 1),
            "inside_humidity": round(float(r[3]), 1),
            "outside_temp": round(float(r[4]), 1),
            "outside_humidity": round(float(r[5]), 1),
            "recorded_at": r[6].strftime("%Y-%m-%d %H:%M:%S"),
        }
        for r in rows
        if r[2] is not None and r[3] is not None and r[4] is not None and r[5] is not None
    ]

    return jsonify(data)


@app.route("/api/current")
def get_current():
    query = """
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
          ON ABS(EXTRACT(EPOCH FROM (s.recorded_at - o.recorded_at))) < 140
        ORDER BY s.recorded_at DESC
        LIMIT 1;
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        r = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if r is None:
        return jsonify({"error": "No data available"}), 404

    return jsonify({
        "id": r[0],
        "device": r[1],
        "inside_temp": round(float(r[2])*9/5+32, 1),
        "inside_humidity": round(float(r[3]), 1),
        "outside_temp": round(float(r[4]), 1),
        "outside_humidity": round(float(r[5]), 1),
        "recorded_at": r[6].strftime("%Y-%m-%d %H:%M:%S"),
    })


@app.route("/api/predict")
def predict():
    try:
        preds = predict_future(steps=288)
        return jsonify(preds)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
