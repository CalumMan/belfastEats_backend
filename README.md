# Belfast Eats – Backend API 🍽️

A Flask-based REST API that powers the **Belfast Eats** full‑stack application. The backend handles business data, location coordinates, and API endpoints used by the front‑end for browsing and mapping food spots across Belfast.

---

## 🚀 Features

* RESTful Flask API
* Business data storage (JSON / structured data)
* Coordinate enrichment for mapping
* Modular route structure
* Environment-based configuration

---

## 🧰 Tech Stack

* Python 3
* Flask
* REST APIs
* JSON data storage
* Virtual environment (venv)

---

## 📁 Project Structure

```
belfast_eats_backend/
│
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── add_coords_to_db.py        # Script to enrich business data with coordinates
├── businesses_with_coords.json
├── data/                      # Raw / processed data files
├── routes/                    # API route modules
├── .gitignore                 # Ignored files (venv, secrets, cache)
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/CalumMan/belfastEats_backend.git
cd belfastEats_backend
```

### 2️⃣ Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

(Windows: `venv\Scripts\activate`)

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the API

```bash
python app.py
```

The API will run locally (usually at):

```
http://127.0.0.1:5000
```

---

## 📡 Example API Usage

Typical endpoints include:

* Fetch businesses
* Retrieve coordinate-enriched listings
* Serve data to front‑end map components

(Expand as front‑end develops)

---

## 🔐 Environment Variables

Sensitive configuration is stored in a `.env` file (not pushed to GitHub):

```
FLASK_ENV=development
SECRET_KEY=your_key_here
```

---

## 📈 Future Improvements

* Database integration (MongoDB / SQL)
* Authentication & user accounts
* Admin CRUD panel
* Cloud deployment (Azure)

---

## 👨‍💻 Author

**Calum Byrne**
Final‑Year Software Engineering Student – Ulster University

---

## 📜 License

This project is for educational and portfolio use.
