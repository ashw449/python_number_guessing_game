import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

# REQUIRED for sessions. Generate a real one with:
#   python -c "import secrets; print(secrets.token_hex(16))"
app.secret_key = "dev-only-change-me"

# Defaults used the very first time a player arrives
DEFAULTS = {"min_value": 1, "max_value": 100, "max_guesses": 5}

# Sanity cap so nobody can request 10,000 guesses
GUESS_LIMIT_MAX = 50


# ---------------------------------------------------------------- settings
def current_settings():
    """Settings stored in the session, falling back to defaults."""
    return {
        "min_value": session.get("min_value", DEFAULTS["min_value"]),
        "max_value": session.get("max_value", DEFAULTS["max_value"]),
        "max_guesses": session.get("max_guesses", DEFAULTS["max_guesses"]),
    }


def parse_settings(form):
    """Return (settings, error). settings is None when the input is invalid."""
    try:
        lo = int(form.get("min_value", "").strip())
        hi = int(form.get("max_value", "").strip())
        limit = int(form.get("max_guesses", "").strip())
    except (AttributeError, ValueError):
        return None, "Settings must all be whole numbers."

    if lo >= hi:
        return None, "Minimum must be less than maximum."
    if limit < 1:
        return None, "You need at least 1 guess."
    if limit > GUESS_LIMIT_MAX:
        return None, f"Maximum guesses is {GUESS_LIMIT_MAX}."

    return {"min_value": lo, "max_value": hi, "max_guesses": limit}, None


def start_new_game(settings):
    """Reset all game state using the given settings."""
    session.update(settings)
    session["number"] = random.randint(settings["min_value"], settings["max_value"])
    session["guesses_left"] = settings["max_guesses"]
    session["status"] = "playing"          # playing | won | lost
    session["message"] = (
        f"I'm thinking of a number between "
        f"{settings['min_value']} and {settings['max_value']}."
    )
    session["history"] = []
    session.pop("settings_error", None)


# ------------------------------------------------------------------ routes
@app.route("/")
def index():
    if "number" not in session:
        start_new_game(current_settings())

    return render_template(
        "index.html",
        settings=current_settings(),
        guess_limit=GUESS_LIMIT_MAX,
        guesses_left=session["guesses_left"],
        status=session["status"],
        message=session["message"],
        history=session["history"],
        settings_error=session.pop("settings_error", None),
    )


@app.route("/start", methods=["POST"])
def start():
    # The settings form always submits min_value/max_value/max_guesses.
    # The "Play again" / "Restart" buttons submit nothing -> reuse settings.
    if request.form.get("min_value") is not None:
        settings, error = parse_settings(request.form)
        if error:
            session["settings_error"] = error
            return redirect(url_for("index"))   # keep the current game intact
    else:
        settings = current_settings()

    start_new_game(settings)
    return redirect(url_for("index"))


@app.route("/guess", methods=["POST"])
def guess():
    if "number" not in session or session["status"] != "playing":
        return redirect(url_for("index"))

    lo, hi = session["min_value"], session["max_value"]
    raw = request.form.get("guess", "").strip()

    # --- invalid input: does NOT cost a guess ---
    try:
        value = int(raw)
    except ValueError:
        session["message"] = "❗ Please enter a valid whole number."
        return redirect(url_for("index"))

    if value < lo or value > hi:
        session["message"] = f"Please enter a number between {lo} and {hi}."
        return redirect(url_for("index"))

    number = session["number"]
    history = session["history"]

    # --- correct guess ---
    if value == number:
        history.append({"value": value, "result": "correct"})
        session["history"] = history
        session["status"] = "won"
        session["message"] = (
            f"🎉 Correct! The number was {number}. "
            f"You won with {session['guesses_left']} guess(es) remaining!"
        )
        return redirect(url_for("index"))

    # --- wrong guess: hint, then spend a guess ---
    if value < number:
        result, hint = "low", "📈 Too low!"
    else:
        result, hint = "high", "📉 Too high!"

    history.append({"value": value, "result": result})
    session["history"] = history
    session["guesses_left"] -= 1
    left = session["guesses_left"]

    if left == 0:
        session["status"] = "lost"
        session["message"] = f"😔 Game over! The number was {number}."
    elif left == 1:
        session["message"] = f"{hint} ⚠️ You have 1 guess left."
    else:
        session["message"] = f"{hint} ❌ Wrong guess! {left} guesses left."

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)