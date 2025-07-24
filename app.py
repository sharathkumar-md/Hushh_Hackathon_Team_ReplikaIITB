from flask import Flask, request, jsonify
import requests
from hushh_mcp.agents.calendar_agent import schedule_meeting

app = Flask(__name__)

@app.route('/agent', methods=['POST'])
def agent():
    user_input = request.json.get('input')
    action = request.json.get('action')
    consent_token = request.json.get('consent_token')
    if action == "schedule_meeting":
        result = schedule_meeting({"meeting_info": user_input, "consent_token": consent_token})
        return jsonify({"result": result})
    
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={"model": "llama3", "prompt": user_input}
    )
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)