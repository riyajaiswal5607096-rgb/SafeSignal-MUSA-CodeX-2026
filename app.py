from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


def create_database():
    con = sqlite3.connect("safesignal.db")

    con.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_type TEXT,
            location TEXT,
            incident_time TEXT,
            reporter_id TEXT
        )
    """)

    con.commit()
    con.close()


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        incident_type = request.form["incident_type"]
        location = request.form["location"]
        incident_time = request.form["incident_time"]

        reporter_id = request.form.get(
            "reporter_id",
            "Anonymous"
        )

        con = sqlite3.connect("safesignal.db")

        con.execute("""
            INSERT INTO reports
            (incident_type, location, incident_time, reporter_id)
            VALUES (?, ?, ?, ?)
        """, (
            incident_type,
            location,
            incident_time,
            reporter_id
        ))

        con.commit()
        con.close()

        return render_template(
            "report.html",
            message="Signal submitted successfully!"
        )

    return render_template("report.html")


@app.route("/map")
def pattern_map():

    con = sqlite3.connect("safesignal.db")

    reports = con.execute("""
        SELECT incident_type, location, incident_time, reporter_id
        FROM reports
    """).fetchall()

    con.close()


    # ==========================================
    # PROTOTYPE CREDIBILITY ENGINE
    # ==========================================

    total_reports = len(reports)

    unique_reporters = len(
        set(r[3] for r in reports)
    )

    incident_types = len(
        set(r[0] for r in reports)
    )

    locations = [
        r[1].strip().lower()
        for r in reports
    ]

    unique_locations = len(set(locations))


    # A pattern is considered credible when:
    #
    # 1. At least 3 signals exist
    # 2. At least 3 distinct reporters exist
    # 3. At least 2 incident types exist
    # 4. Signals are concentrated at one location

    pattern = (
        total_reports >= 3
        and unique_reporters >= 3
        and incident_types >= 2
        and unique_locations == 1
    )


    return render_template(
        "map.html",
        reports=reports,
        pattern=pattern
    )


@app.route("/explain")
def explain():

    con = sqlite3.connect("safesignal.db")

    reports = con.execute("""
        SELECT incident_type, location, incident_time, reporter_id
        FROM reports
    """).fetchall()

    con.close()


    unique_reporters = len(
        set(r[3] for r in reports)
    )

    incident_types = len(
        set(r[0] for r in reports)
    )


    return render_template(
        "explain.html",
        reports=reports,
        unique_reporters=unique_reporters,
        incident_types=incident_types
    )


@app.route("/alert")
def alert():

    return render_template(
        "alert.html"
    )


if __name__ == "__main__":

    create_database()

    app.run(debug=True)