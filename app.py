from flask import Flask, render_template, request
from datetime import datetime, timedelta
import os
import random

app = Flask(__name__)

# Initial game state
game_state = {
    "gdp": 1000,
    "unemployment": 5,
    "inflation": 2,
    "public_debt": 500,
    "investment": 200,
    "consumer_confidence": 70,
    "time": 0,
    "population": 100.0,
    "happiness": 75.0,
    "date": datetime(2024, 1, 1),
    "notable_events": [],  # Store notable events here
    "policies": [],  # Store enacted policies here
}

# Log file path
LOG_FILE_PATH = 'game_log.txt'


def log_event(action, value, impact):
    """Logs events with timestamp, action, value, and impact to the game_log.txt file."""
    timestamp = datetime.now()
    log_message = f"{timestamp}: Action: {action}, Value: {value}, Impact: {impact}\n"

    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(log_message)


def track_event(event_description):
    """Adds a notable event to the game state."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    event = {
        'timestamp': timestamp,
        'description': event_description
    }
    game_state["notable_events"].append(event)


@app.route("/")
def index():
    """The main page of the game."""
    return render_template("index.html", game_state=game_state)


@app.route("/adjust", methods=["POST"])
def adjust():
    """Handle changes to the game state based on user actions."""
    action = request.form.get("action")
    change = int(request.form.get("value"))

    if action == "taxes":
        game_state["gdp"] += random.uniform(8, 12) * change
        game_state["public_debt"] -= random.uniform(4, 6) * change
        game_state["investment"] -= random.uniform(1.5, 2.5) * change
        game_state["consumer_confidence"] -= random.uniform(0.4, 0.6) * change
        game_state["happiness"] -= random.uniform(0.2, 0.4) * change
        log_event("Tax Adjustment", change, f"GDP: {game_state['gdp']}, Public Debt: {game_state['public_debt']}")
    elif action == "spending":
        game_state["gdp"] += random.uniform(12, 18) * change
        game_state["public_debt"] += random.uniform(8, 12) * change
        game_state["investment"] += random.uniform(0.8, 1.2) * change
        game_state["consumer_confidence"] += random.uniform(0.15, 0.25) * change
        game_state["happiness"] += random.uniform(0.4, 0.6) * change
        log_event("Spending Adjustment", change, f"GDP: {game_state['gdp']}, Public Debt: {game_state['public_debt']}")
    elif action == "interest":
        game_state["inflation"] -= random.uniform(0.4, 0.6) * change
        game_state["gdp"] -= random.uniform(4, 6) * change
        game_state["unemployment"] += random.uniform(0.15, 0.25) * change
        game_state["investment"] -= random.uniform(2.5, 3.5) * change
        game_state["consumer_confidence"] -= random.uniform(0.7, 0.9) * change
        game_state["happiness"] -= random.uniform(0.15, 0.25) * change
        log_event("Interest Rate Adjustment", change, f"Inflation: {game_state['inflation']}, GDP: {game_state['gdp']}")
    elif action == "investment":
        game_state["gdp"] += random.uniform(18, 22) * change
        game_state["investment"] += random.uniform(0.9, 1.1) * change
        game_state["consumer_confidence"] += random.uniform(0.25, 0.35) * change
        game_state["happiness"] += random.uniform(0.3, 0.5) * change
        log_event("Investment Adjustment", change, f"GDP: {game_state['gdp']}, Investment: {game_state['investment']}")

    return render_template("index.html", game_state=game_state)


@app.route("/time_advance", methods=["POST"])
def time_advance():
    """Advance time by a specified number of years and update game state."""
    years = int(request.form.get("years", 1))
    game_state["time"] += years
    game_state["date"] += timedelta(days=365 * years)

    # Simulate economic growth (same as before)
    gdp_growth_rate = random.uniform(0.01, 0.03)  # GDP grows 1-3% annually
    debt_growth_rate = random.uniform(0.02, 0.04)  # Public debt grows 2-4%
    population_growth = random.uniform(0.4, 0.6)  # Population grows 0.4-0.6% annually

    game_state["gdp"] *= (1 + gdp_growth_rate * years)
    game_state["public_debt"] *= (1 + debt_growth_rate * years)
    game_state["population"] += years * population_growth
    game_state["unemployment"] = max(0, game_state["unemployment"] + random.uniform(0.05, 0.15) * years)
    game_state["inflation"] = max(0, game_state["inflation"] + random.uniform(0.1, 0.3) * years)
    game_state["happiness"] = max(0, min(100, game_state["happiness"] - random.uniform(0.3, 0.7) * years))

    # Introduce random economic shocks (same as before)
    if random.random() < 0.1:  # 10% chance per year of a shock
        shock_type = random.choice(["recession", "boom", "inflation_spike", "debt_crisis"])
        if shock_type == "recession":
            game_state["gdp"] -= random.uniform(50, 150)
            game_state["unemployment"] += random.uniform(1, 3)
            track_event("Economic Shock: Recession! GDP and employment impacted.")
        elif shock_type == "boom":
            game_state["gdp"] += random.uniform(100, 200)
            game_state["unemployment"] -= random.uniform(1, 2)
            track_event("Economic Shock: Boom! Economic indicators improved.")
        elif shock_type == "inflation_spike":
            game_state["inflation"] += random.uniform(2, 5)
            track_event("Economic Shock: Inflation Spike! Consumer prices rising.")
        elif shock_type == "debt_crisis":
            game_state["public_debt"] += random.uniform(100, 300)
            game_state["consumer_confidence"] -= random.uniform(5, 10)
            track_event("Economic Shock: Debt Crisis! Public debt increased.")

    # Introduce random policies
    if random.random() < 0.1:  # 10% chance of a policy being enacted each year
        policy_type = random.choice(["ubi", "tax_cuts", "austerity", "green_investment", "healthcare_reform"])

        if policy_type == "ubi":
            game_state["consumer_confidence"] += random.uniform(5, 15)
            game_state["happiness"] += random.uniform(2, 5)
            game_state["public_debt"] += random.uniform(100, 300)
            track_event("Policy Enacted: Universal Basic Income. Increased spending but rising debt.")
            game_state["policies"].append({
                "policy": "Universal Basic Income (UBI)",
                "description": "Increases consumer spending and happiness, but raises public debt.",
                "impact": f"Consumer Confidence: +{random.uniform(5, 15):.2f}, Happiness: +{random.uniform(2, 5):.2f}, Public Debt: +{random.uniform(100, 300):.2f}"
            })

        elif policy_type == "tax_cuts":
            game_state["consumer_confidence"] += random.uniform(3, 10)
            game_state["investment"] += random.uniform(10, 30)
            game_state["public_debt"] += random.uniform(50, 200)
            track_event("Policy Enacted: Tax Cuts. Boosted spending and investment but rising debt.")
            game_state["policies"].append({
                "policy": "Tax Cuts",
                "description": "Boosts consumer spending and investment, but raises public debt.",
                "impact": f"Consumer Confidence: +{random.uniform(3, 10):.2f}, Investment: +{random.uniform(10, 30):.2f}, Public Debt: +{random.uniform(50, 200):.2f}"
            })

        elif policy_type == "austerity":
            game_state["public_debt"] -= random.uniform(100, 300)
            game_state["gdp"] -= random.uniform(50, 100)
            game_state["unemployment"] += random.uniform(1, 3)
            game_state["consumer_confidence"] -= random.uniform(5, 10)
            track_event("Policy Enacted: Austerity Measures. Reduced debt but increased unemployment.")
            game_state["policies"].append({
                "policy": "Austerity Measures",
                "description": "Reduces public debt but increases unemployment and decreases GDP growth.",
                "impact": f"Public Debt: -{random.uniform(100, 300):.2f}, GDP: -{random.uniform(50, 100):.2f}, Unemployment: +{random.uniform(1, 3):.2f}"
            })

        elif policy_type == "green_investment":
            game_state["public_debt"] += random.uniform(100, 300)
            game_state["gdp"] += random.uniform(50, 150)
            game_state["consumer_confidence"] += random.uniform(2, 5)
            track_event("Policy Enacted: Green Energy Investment. Increased debt but long-term growth.")
            game_state["policies"].append({
                "policy": "Green Energy Investment",
                "description": "Increases GDP and long-term growth, but raises public debt.",
                "impact": f"Public Debt: +{random.uniform(100, 300):.2f}, GDP: +{random.uniform(50, 150):.2f}, Consumer Confidence: +{random.uniform(2, 5):.2f}"
            })

        elif policy_type == "healthcare_reform":
            game_state["public_debt"] += random.uniform(50, 200)
            game_state["happiness"] += random.uniform(5, 10)
            game_state["gdp"] += random.uniform(20, 50)
            track_event("Policy Enacted: Healthcare Reform. Increased happiness and productivity.")
            game_state["policies"].append({
                "policy": "Healthcare Reform",
                "description": "Boosts happiness and productivity, but raises public debt.",
                "impact": f"Public Debt: +{random.uniform(50, 200):.2f}, Happiness: +{random.uniform(5, 10):.2f}, GDP: +{random.uniform(20, 50):.2f}"
            })

    log_event("Time Advancement", years, f"Date: {game_state['date']}, GDP: {game_state['gdp']}, Public Debt: {game_state['public_debt']}")

    return render_template("index.html", game_state=game_state)




@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")


@app.route("/policy")
def policy():
    """Display the policies that have been enacted."""
    # Ensure game_state is passed to the template
    return render_template("policy.html", game_state=game_state)



@app.route("/log")
def view_log():
    """View game log in a table format."""
    log_contents = []

    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as log_file:
            for line in log_file.readlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    parts = line.split(": ", 1)
                    if len(parts) < 2:
                        continue
                    timestamp = parts[0]
                    message = parts[1]
                    action_value, impact = message.split(", Impact: ")
                    action_value, value = action_value.split(", Value: ")
                    action = action_value.split(": ")[1]
                    value = value.strip()
                    impact = impact.strip()
                    log_contents.append({
                        "date": timestamp,
                        "action": action,
                        "value": value,
                        "impact": impact
                    })
                except ValueError:
                    continue

    return render_template("log.html", log_contents=log_contents)


@app.route("/events")
def view_events():
    """View notable events in a table format."""
    return render_template("events.html", events=game_state["notable_events"])


@app.route("/clear_log", methods=["POST"])
def clear_log():
    """Clears the game log file."""
    with open(LOG_FILE_PATH, 'w') as log_file:
        log_file.truncate(0)

    return render_template("log.html", log_contents=[])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
