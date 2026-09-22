from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB = os.path.join(os.path.dirname(__file__), "safesignal.db")


def get_db():
    return sqlite3.connect(DB)


def create_database():
    con = get_db()

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

    # The old MVP opened with 5 synthetic signals and the demo submission
    # made the dashboard show 6 Total Signals.
    count = con.execute("SELECT COUNT(*) FROM reports").fetchone()[0]

    if count == 0:
        demo_reports = [
            ("Loitering", "central corridor", "Just now", "Reporter 1"),
            ("Following", "central corridor", "Just now", "Reporter 2"),
            ("Verbal Harassment", "central corridor", "Just now", "Reporter 3"),
            ("Other", "central corridor", "Just now", "Reporter 4"),
            ("Catcalling", "central corridor", "Just now", "Reporter 1"),
        ]

        con.executemany("""
            INSERT INTO reports
            (incident_type, location, incident_time, reporter_id)
            VALUES (?, ?, ?, ?)
        """, demo_reports)

        con.commit()

    con.close()


@app.route("/", methods=["GET", "POST"])
def home():
    create_database()

    reporter_id = request.args.get("reporter_id", "Reporter 1")
    message = request.args.get("message")

    if request.method == "POST":
        incident_type = request.form["incident_type"]
        location = request.form["location"]
        incident_time = request.form["incident_time"]
        reporter_id = request.form.get("reporter_id", "Reporter 1")

        con = get_db()

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

        message = "Signal submitted successfully!"

    return render_template(
        "report.html",
        message=message,
        reporter_id=reporter_id
    )


@app.route("/change-reporter")
def change_reporter():
    current = request.args.get("current", "Reporter 1")

    reporters = [
        "Reporter 1",
        "Reporter 2",
        "Reporter 3",
        "Reporter 4"
    ]

    if current in reporters:
        current_index = reporters.index(current)
        next_reporter = reporters[
            (current_index + 1) % len(reporters)
        ]
    else:
        next_reporter = "Reporter 1"

    return redirect(
        url_for(
            "home",
            reporter_id=next_reporter,
            message=f"Demo reporter changed to {next_reporter}"
        )
    )

@app.route("/map")
def pattern_map():
    create_database()

    con = get_db()

    reports = con.execute("""
        SELECT incident_type, location, incident_time, reporter_id
        FROM reports
        ORDER BY id DESC
    """).fetchall()

    con.close()

    total_reports = len(reports)
    unique_reporters = len(set(r[3] for r in reports))
    incident_types = len(set(r[0] for r in reports))

    locations = [r[1].strip().lower() for r in reports]
    unique_locations = len(set(locations))

    pattern = (
        total_reports >= 3
        and unique_reporters >= 3
        and incident_types >= 2
        and unique_locations == 1
    )

    return render_template(
        "map.html",
        reports=reports,
        pattern=pattern,
        total_reports=total_reports,
        unique_reporters=unique_reporters,
        incident_types=incident_types
    )


@app.route("/explain")
def explain():
    create_database()

    con = get_db()

    reports = con.execute("""
        SELECT incident_type, location, incident_time, reporter_id
        FROM reports
    """).fetchall()

    con.close()

    unique_reporters = len(set(r[3] for r in reports))
    incident_types = len(set(r[0] for r in reports))

    return render_template(
        "explain.html",
        reports=reports,
        unique_reporters=unique_reporters,
        incident_types=incident_types
    )


@app.route("/alert")
def alert():
    create_database()
    return render_template("alert.html")


create_database()


if __name__ == "__main__":
    app.run(debug=True)
