print("Attempting to import create_app from application...")
from application import create_app


app = create_app()

if __name__ == "__main__":
    app.run()
