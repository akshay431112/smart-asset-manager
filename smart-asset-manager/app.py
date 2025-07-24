from flask import Flask, render_template, request, redirect
import sqlite3, os, qrcode
import barcode
from barcode.writer import ImageWriter

app = Flask(__name__)
DB_FILE = 'database.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, owner TEXT, location TEXT)")

@app.route("/")
def index():
    with sqlite3.connect(DB_FILE) as conn:
        assets = conn.execute("SELECT * FROM assets").fetchall()
    return render_template("index.html", assets=assets)

@app.route("/add", methods=["GET", "POST"])
def add_asset():
    if request.method == "POST":
        name = request.form["name"]
        owner = request.form["owner"]
        location = request.form["location"]
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute("INSERT INTO assets (name, owner, location) VALUES (?, ?, ?)", (name, owner, location))
            asset_id = cursor.lastrowid

        # QR Code
        qr_path = f"static/qrcodes/{asset_id}.png"
        qrcode.make(f"ID:{asset_id}, Name:{name}, Owner:{owner}, Location:{location}").save(qr_path)

        # Barcode
        barcode_path = f"static/barcodes/{asset_id}"
        barcode.get("code128", str(asset_id), writer=ImageWriter()).save(barcode_path)

        return redirect("/")
    return render_template("add_asset.html")

@app.route("/asset/<int:asset_id>")
def asset_detail(asset_id):
    with sqlite3.connect(DB_FILE) as conn:
        asset = conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()
    return render_template("asset_detail.html", asset=asset)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)