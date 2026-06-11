# Environment Monitor

An IoT environmental monitoring system that tracks indoor and outdoor temperature and humidity in real time. Sensor data is collected from an ESP32 microcontroller, stored in PostgreSQL, and displayed on a web dashboard with 24-hour ML-based forecasts.

## Features

- Live indoor temperature and humidity from a DHT sensor on an ESP32
- Outdoor weather pulled from the [Open-Meteo](https://open-meteo.com/) API
- Historical charts with Today / Last 24 h / Last 7 days views
- 24-hour forecast using linear regression (scikit-learn)

## Architecture

```
ESP32 + DHT sensor
        │ MQTT publish (sensors/esp32_room1)
        ▼
   MQTT Broker
        │
   subscriber.py ──► PostgreSQL (sensor_data, outside_data)
                           │
   temp_website.py ────────┘  (polls Open-Meteo every 5 min)
                           │
          app.py (Flask API + serves dashboard)
                           │
                    browser dashboard
```

## Hardware

| Component | Detail |
|-----------|--------|
| Microcontroller | ESP32 |
| Sensor | DHT11 / DHT22 on GPIO 14 |
| Embedded toolchain | PlatformIO |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Firmware | MicroPython (`main.py`), umqtt.simple |
| Backend | Python 3, Flask |
| Database | PostgreSQL, psycopg2 |
| Messaging | MQTT (Paho) |
| ML | pandas, scikit-learn (LinearRegression) |
| Weather API | Open-Meteo |
| Frontend | HTML5, CSS3, JavaScript, Chart.js |

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- An MQTT broker (e.g., Mosquitto) accessible on the network
- ESP32 with a DHT sensor flashed with `main.py`

### Database Setup

Create a PostgreSQL database and run the following:

```sql
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    device TEXT,
    temperature REAL,
    humidity REAL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE outside_data (
    id SERIAL PRIMARY KEY,
    temperature REAL,
    humidity REAL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Configuration

Set the following environment variables (or edit [config.py](config.py)):

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_NAME` | `environment` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `postgres` | Database password |
| `MQTT_BROKER` | `localhost` | MQTT broker address |

### Running the Services

Start each service in a separate terminal:

```bash
# 1. MQTT subscriber — stores sensor readings to PostgreSQL
python subscriber.py

# 2. Outdoor weather poller — fetches Open-Meteo data every 5 minutes
python temp_website.py

# 3. Flask web server — API + dashboard
python app.py
```

Open `http://localhost:5000` in your browser to view the dashboard.

### Flashing the ESP32

Edit the Wi-Fi and MQTT broker settings in [main.py](main.py), then flash it to the ESP32 using your preferred MicroPython tool (e.g., `mpremote` or Thonny).


## Project Structure

```
EnvironmentMonitor/
├── app.py              # Flask API server
├── main.py             # ESP32 MicroPython firmware
├── subscriber.py       # MQTT → PostgreSQL subscriber
├── prediction.py       # ML forecasting module
├── temp_website.py     # Outdoor weather poller
├── connect_sensor.py   # Serial sensor handler
├── config.py           # Shared configuration
├── templates/
│   └── index.html      # Web dashboard
├── src/                # Arduino/PlatformIO source
└── platformio.ini      # PlatformIO config
```
