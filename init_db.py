from app import app, db

def init_database():
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()