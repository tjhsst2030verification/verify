import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import json
import threading
from pathlib import Path

from flask import Flask, request
from requests_oauthlib import OAuth2Session
from werkzeug.serving import make_server

import streamlit as st

CLIENT_ID = "KxvPkRJiHIZX0BuHrNdCXM0LCQ9ZEFKjrVIREKgr"
CLIENT_SECRET = "PtEe1pSe18sh3frhlnEO1ULP7KORKDvZ3sGbCQWZjEilPU6FlUbzPCq1ZUuM8vO2T7N1U41JzKuAlaay1MyyKPelLia4FxJ8yqHnW4B6IC73SGVwB7MI1wrTPYMyzlDl"

REDIRECT_URI = "http://127.0.0.1:5000/callback"

AUTH_URL = "https://ion.tjhsst.edu/oauth/authorize/"
TOKEN_URL = "https://ion.tjhsst.edu/oauth/token/"
PROFILE_URL = "https://ion.tjhsst.edu/api/profile"

OUTPUT_FILE = Path(__file__).parent / "ion_profile.json"

app = Flask(__name__)

oauth = OAuth2Session(
    CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    scope=["read"]
)

authorization_url, state = oauth.authorization_url(AUTH_URL)

callback_received = threading.Event()


@app.route("/callback")
def callback():
    try:
        print("\nAuthenticating with Ion...")

        oauth.fetch_token(
            TOKEN_URL,
            authorization_response=request.url,
            client_secret=CLIENT_SECRET
        )

        print("Authentication successful!")
        print("Retrieving profile...")

        response = oauth.get(PROFILE_URL)
        response.raise_for_status()

        profile = response.json()

        print("Profile retrieved successfully!")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(profile, file, indent=4, ensure_ascii=False)

        print("\nProfile saved to:")
        print(OUTPUT_FILE.resolve())

        print("\n========== ION PROFILE ==========\n")
        print(json.dumps(profile, indent=4, ensure_ascii=False))
        print("\n=================================")

        return "Profile successfully retrieved and saved! You can close this tab."

    except Exception as error:
        print("\nERROR:", repr(error))
        return "Something went wrong. Check the VS Code terminal."

    finally:
        callback_received.set()


if __name__ == "__main__":
    server = make_server("127.0.0.1", 5000, app)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    print("Opening Ion authentication...")
    import webbrowser
    webbrowser.open(authorization_url)

    print("Waiting for authentication...")

    callback_received.wait()

    server.shutdown()
    print("\nProgram finished.")