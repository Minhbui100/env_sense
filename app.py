from flask import Flask, jsonify, render_template, request
import psycopg2
from prediction import predict_future

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="environment",
        user="postgres",
        password="Dynamic@00"
    )

@app.route("/api/data")
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()

    time_range = request.args.get("range", "today")
    if time_range=="today":
        filt="date(timestamp)=current_date"
    elif time_range=="24h":
        filt="timestamp >= NOW() - INTERVAL '24 hours'"
    else:
        filt="timestamp >= NOW() - INTERVAL '7 days'"

    cur.execute(f"""
        SELECT temperature, humidity, timestamp
        FROM dht11
        WHERE {filt}
        ORDER BY timestamp
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert to JSON format
    data = [
        {
            "temperature": r[0],
            "humidity": r[1],
            "timestamp": r[2].strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in rows
    ]

    return jsonify(data)

@app.route("/api/predict")
def predict():
    preds = predict_future(steps=1440)
    return jsonify(preds)



@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)