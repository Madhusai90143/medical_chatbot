from app import app  # noqa: F401

# This file is used by gunicorn to locate the app object
# The actual server is run via the Start application workflow

if __name__ == "__main__":
    # This is for direct Python execution, not used with gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
