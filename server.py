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

@app.route('/team/<team_id>/<state>/hand_touches', methods=['POST'])
def hand_touches(team_id, state):
    """
    Update hand touches for a specific team
    Args:
        team_id: The team identifier
        state: Boolean string ('true' or 'false') for increment/decrement
    """
    try:
        increment = state.lower() == 'true'
        request_data = request.get_json()
        print(f"Received request for team {team_id}, state: {state}")
        print(f"Request data: {request_data}")
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "setHandTouch",
            "data": {
                "teamId": team_id,
                "increment": increment
            }
        })
        if not response.ok:
            raise Exception(f"Apps Script returned status code: {response.status_code}")

        result = response.json()
        return jsonify(result), 200

    except Exception as e:
        print(f"Error in hand_touches: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@app.route('/team/<team_id>/time', methods=['POST'])
def update_time(team_id):
    """
    Update time for a specific team
    Args:
        team_id: The team identifier
    Body:
        JSON with totalTime value
    """
    try:
        request_data = request.get_json()
        total_time = request_data.get('data', {}).get('totalTime')
        
        if total_time is None:
            raise ValueError("totalTime is required in request data")
        print(f"Updating time for team {team_id}: {total_time}")
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "setTime",
            "data": {
                "teamId": team_id,
                "totalTime": float(total_time)
            }
        })
        if not response.ok:
            raise Exception(f"Apps Script returned status code: {response.status_code}")
        result = response.json()
        return jsonify(result), 200

    except ValueError as ve:
        print(f"Validation error: {str(ve)}")
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        print(f"Error in update_time: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


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
def receive_data(increment):
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
                     "increment":increment,
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

@app.route('/esp_data', methods=['POST'])
def receive_data_esp():
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
    
@app.route('/present/teams')
def present_teams():
    """
    Display presentation-only dashboard for all teams
    """
    try:
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "getTeamId",
            "data": {}
        })
        teams = response.json()
        print(teams)
        return render_template('present_teams.html', teams=teams)
    except Exception as e:
        return render_template('present_teams.html', teams={}, error=str(e))

@app.route('/present/<team_id>')
def present(team_id):
    """
    Display presentation-only dashboard for a team
    """
    try:
        response = requests.post(APPS_SCRIPT_URL, json={
            "action": "getTeamData",
            "data": {"teamId": team_id}
        })
        team = response.json()
        return render_template('present_teamdata.html', team=team)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
if __name__ == '__main__':
    app.run(debug=True, host='192.168.29.254')