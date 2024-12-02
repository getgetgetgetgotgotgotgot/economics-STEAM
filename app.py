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
    "notable_events": []  # Store notable events here
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
    game_state["events"].append(event)

def simulate_economic_changes(years):
    """Simulate more variable economic changes over time based on trends and random fluctuations."""

    # GDP Growth: Random fluctuations between -2% to +6% annually
    gdp_growth_rate = random.uniform(-0.02, 0.06)  # Range: -2% to +6%

    # Inflation: Random fluctuations between 0% to 5% annually
    inflation_rate = random.uniform(0, 0.05)  # Range: 0% to 5%

    # Unemployment: Random fluctuations based on a normal distribution (mean=5%, stddev=1%)
    unemployment_rate = max(0, random.gauss(0.05, 0.01))  # Mean 5%, standard deviation 1%

    # Population Growth: Random fluctuations between 0.1% to 1% annually
    population_growth_rate = random.uniform(0.001, 0.01)  # Range: 0.1% to 1%

    # Adjust GDP based on random growth rate
    old_gdp = game_state["gdp"]
    game_state["gdp"] *= (1 + gdp_growth_rate)

    # Adjust inflation based on random inflation rate
    game_state["inflation"] += inflation_rate

    # Adjust unemployment based on random fluctuations
    old_unemployment = game_state["unemployment"]
    game_state["unemployment"] = max(0, game_state["unemployment"] + random.uniform(-0.01, 0.02))  # Small random fluctuation

    # Adjust population based on random growth rate
    game_state["population"] *= (1 + population_growth_rate)

    # Simulate consumer confidence with more variability
    consumer_confidence_base = 70
    consumer_confidence_sensitivity = -0.5  # Negative relationship with inflation
    game_state["consumer_confidence"] = consumer_confidence_base - (game_state["inflation"] * consumer_confidence_sensitivity) + random.uniform(-5, 5)
    game_state["consumer_confidence"] = max(0, min(100, game_state["consumer_confidence"]))  # Ensure it's within 0-100

    # Simulate happiness with more variability
    happiness_base = 75
    happiness_sensitivity = -0.2
    game_state["happiness"] = happiness_base - (game_state["inflation"] * happiness_sensitivity) - (game_state["unemployment"] * happiness_sensitivity) + random.uniform(-5, 5)
    game_state["happiness"] = max(0, min(100, game_state["happiness"]))  # Ensure it's within 0-100

    # Simulate random fluctuation in investment
    game_state["investment"] += random.randint(-10, 20) * (game_state["consumer_confidence"] / 100)

    # Check for economic shocks
    if game_state["gdp"] < old_gdp * 0.9:  # GDP drops more than 10%
        track_event("Economic Shock: GDP has dropped significantly!")

    if game_state["inflation"] > 0.1:  # Inflation exceeds 10%
        track_event("Economic Shock: Inflation has exceeded 10%!")

    if game_state["unemployment"] > old_unemployment * 1.5:  # Unemployment has risen more than 50%
        track_event("Economic Shock: Unemployment has risen significantly!")

    log_event("Time Advancement", years, f"Date: {game_state['date']}, GDP: {game_state['gdp']}, Public Debt: {game_state['public_debt']}, Inflation: {game_state['inflation']}")

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
        game_state["gdp"] += change * 10
        game_state["public_debt"] -= change * 5
        game_state["investment"] -= change * 2
        game_state["consumer_confidence"] -= change * 0.5
        game_state["happiness"] -= change * 0.3
        log_event("Tax Adjustment", change, f"GDP: {game_state['gdp']}, Public Debt: {game_state['public_debt']}")
    elif action == "spending":
        game_state["gdp"] += change * 15
        game_state["public_debt"] += change * 10
        game_state["investment"] += change * 1
        game_state["consumer_confidence"] += change * 0.2
        game_state["happiness"] += change * 0.5
        log_event("Spending Adjustment", change, f"GDP: {game_state['gdp']}, Public Debt: {game_state['public_debt']}")
    elif action == "interest":
        game_state["inflation"] -= change * 0.5
        game_state["gdp"] -= change * 5
        game_state["unemployment"] += change * 0.2
        game_state["investment"] -= change * 3
        game_state["consumer_confidence"] -= change * 0.8
        game_state["happiness"] -= change * 0.2
        log_event("Interest Rate Adjustment", change, f"Inflation: {game_state['inflation']}, GDP: {game_state['gdp']}")
    elif action == "investment":
        game_state["gdp"] += change * 20
        game_state["investment"] += change
        game_state["consumer_confidence"] += change * 0.3
        game_state["happiness"] += change * 0.4
        log_event("Investment Adjustment", change, f"GDP: {game_state['gdp']}, Investment: {game_state['investment']}")

    return render_template("index.html", game_state=game_state)

@app.route("/time_advance", methods=["POST"])
def time_advance():
    """Advance time by a specified number of years and update game state."""
    years = int(request.form.get("years", 1))
    game_state["time"] += years
    game_state["date"] += timedelta(days=365 * years)

    # Simulate economic changes
    game_state["population"] += years * 0.5
    game_state["gdp"] *= 1 + (years * 0.02)  # Assume 2% annual growth
    game_state["public_debt"] *= 1 + (years * 0.03)  # Assume 3% debt growth
    game_state["unemployment"] = max(0, game_state["unemployment"] + years * 0.1)
    game_state["inflation"] = max(0, game_state["inflation"] + years * 0.2)
    game_state["happiness"] = max(0, min(100, game_state["happiness"] - years * 0.5))

    # Check if an economic shock occurs
    event_occurred = False
    if game_state["gdp"] < 800:  # Example: Economic shock if GDP falls below 800
        event_occurred = True
        log_event("Economic Shock", "GDP Drop", f"Date: {game_state['date']}, GDP: {game_state['gdp']}")

    if game_state["unemployment"] > 10:  # Example: Economic shock if unemployment is above 10%
        event_occurred = True
        log_event("Economic Shock", "Unemployment Surge", f"Date: {game_state['date']}, Unemployment: {game_state['unemployment']}")

    if game_state["inflation"] > 10:  # Example: Economic shock if inflation is above 10%
        event_occurred = True
        log_event("Economic Shock", "Inflation Surge", f"Date: {game_state['date']}, Inflation: {game_state['inflation']}")

    if event_occurred:
        # You can log the shock to be displayed in events, and store the event
        game_state["notable_events"].append({
            "date": game_state["date"],
            "description": "Economic Shock"
        })

    log_event("Time Advancement", years, f"Date: {game_state['date']}, GDP: {game_state['gdp']}, Public Debt: {game_state['public_debt']}")

    return render_template("index.html", game_state=game_state)


@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")

@app.route("/policy")
def policy():
    """Policy page."""
    return render_template("policy.html")

@app.route("/log")
def view_log():
    """View game log in a table format."""
    log_contents = []

    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as log_file:
            for line in log_file.readlines():
                line = line.strip()  # Clean any leading/trailing spaces or newlines
                if not line:
                    continue  # Skip empty lines

                try:
                    # Split the line at the first ": " to separate timestamp and message
                    parts = line.split(": ", 1)
                    if len(parts) < 2:
                        continue  # Skip lines that don't match the expected format
                    timestamp = parts[0]
                    message = parts[1]

                    # Split the message at ", Impact: " to separate the action/value and impact
                    action_value, impact = message.split(", Impact: ")

                    # Split the action_value at ", Value: " to separate action from value
                    action_value, value = action_value.split(", Value: ")

                    # Extract action name
                    action = action_value.split(": ")[1]
                    value = value.strip()  # Clean the value
                    impact = impact.strip()  # Clean the impact

                    log_contents.append({
                        "date": timestamp,
                        "action": action,
                        "value": value,
                        "impact": impact
                    })

                except ValueError as e:
                    print(f"Error processing log entry: {line} - {e}")
                    continue  # Skip problematic log entries

    return render_template("log.html", log_contents=log_contents)

@app.route("/events")
def view_events():
    """View notable events in a table format."""
    return render_template("events.html", events=game_state["events"])

@app.route("/clear_log", methods=["POST"])
def clear_log():
    """Clears the game log file."""
    with open(LOG_FILE_PATH, 'w') as log_file:
        log_file.truncate(0)

    return render_template("log.html", log_contents=[])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)