import os
import netrc
import json
import requests
from flask import Flask, request, jsonify ,render_template
from flask_cors import CORS
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwU6vJffMsCWOKeOJ2seXnIysd44V3HhXJM3koOtY2A4oGyEALt7R3IPNUS5xsmgWGW/exec"
app = Flask(__name__)
CORS(app) 
currentTeam = None

@app.route('/')
def home():
    """
    Display webpage with list of teams
    """
    try:
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "getTeamId",
            "data": {}
        })
        teams_data = response.json()
        # Ensure teams_data is a list
        teams = teams_data if isinstance(teams_data, list) else []
        return render_template('base.html', teams=teams)
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        return render_template('base.html', teams=[], error=str(e))


@app.route('/teams')
def teams():
    """
    Display specific team details
    """
    try:
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "getTeamId",
            "data": {}
        })
        teams = response.json()
        print(teams)
        return render_template('teams.html', teams=teams)
    except Exception as e:
        return render_template('teams.html', teams={}, error=str(e))

@app.route('/team/api/<team_id>')
def team_api(team_id):
    """
    Display specific team details
    """
    try:
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "getTeamData",
            "data": {"teamId": team_id}
        })
        team = response.json()
        return jsonify(team), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/team/<team_id>')
def team_detail(team_id):
    print(team_id)
    global currentTeam 
    currentTeam = team_id
    """
    Display specific team details
    """
    try:
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "getTeamData",
            "data": {"teamId": team_id}
        })
        print(response.json())
        team = response.json()
        print(team)
        return render_template('team_detail.html', team=team)
    except Exception as e:
        return render_template('team_detail.html', team={}, error=str(e))

@app.route('/team/<team_id>/hand_touches', methods=['POST'])
def hand_touches(team_id):
    print(team_id)
    """
    Display specific team details
    """
    try:
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "setHandTouch",
            "data": {
                    "teamId": team_id,
                     "increment":False
                    }
        })
        team = response.json()
        return team
    except Exception as e:
        print(e)

@app.route('/getAllTeamId', methods=['POST'])
def getTeamId():
    """
    Endpoint to get all data from Google Sheet using Apps Script
    Accepts POST request with empty/null JSON body
    """
    try:
        response = requests.post(APPS_SCRIPT_URL, json={ "action" : "getTeamId",
            "data": {}})
        data = response.json()
        print("Received data:", data)
        return jsonify(data), 200

    except Exception as e:
        print("Error retrieving team data:", e)
        return jsonify({"status": "error", "message": str(e)}), 400

    
@app.route('/data', methods=['POST'])
def receive_data():
    """
    Endpoint to receive data from ESP device.
    Data is expected to be in JSON format.
    """
    try:
        data = request.get_json()
        print("Received data:", data)
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "setCheckPoints",
            "data": {
                    "teamId": currentTeam,
                     "increment":False,
                     "checkPoints": data
                    }
        })
        team = response.json()
        return team
    except Exception as e:
        print(e)
        return jsonify({"status": "success", "message": "Data received successfully"}), 200

    except Exception as e:
        print("Error processing data:", e)
        return jsonify({"status": "error", "message": str(e)}), 400
    
if __name__ == '__main__':
    app.run(debug=True, host='192.168.243.120')