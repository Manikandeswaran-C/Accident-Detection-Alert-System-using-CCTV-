from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    log_file = 'alerts.csv'
    alerts = []
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        alerts = df.tail(10).to_dict(orient='records')

    snapshot = "static/captured_frame.jpg" if os.path.exists("static/captured_frame.jpg") else None
    return render_template("dashboard.html", alerts=alerts, snapshot=snapshot)

if __name__ == '__main__':
    app.run(debug=True)
