from app import create_app  # Importing the create_app function from app/__init__.py
import os
# Create the app
app = create_app()

# Run the app if this script is executed
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
