# -- Programmer Mmdrza - Mmdrza.Com -- 2024
from flask import Flask, render_template, request, jsonify
import markdown
import json
import requests
import os

# Configurations
# enter your api url from local or server (ollama)
api_url = "http://0.0.0.0:11434/api/chat"
# default model , can use any model: https://ollama.com/library
model = "qwen:32b" # https://ollama.com/library/codegemma
current = os.path.dirname(os.path.realpath(__file__))
pathTemp = os.path.join(current, "template")
app = Flask(__name__, template_folder=pathTemp)


# -- Chat Function for Receiving Messages
def chat(messages):
    try:
        # -- Can Stream Response set to False (Not Recommended)
        r = requests.post(
            api_url,
            json={"model": model, "messages": messages, "stream": True},
            stream=True
        )

        output = ""
        for line in r.iter_lines():
            if line:
                body = json.loads(line)
                if "error" in body:
                    return "Error: " + body["error"]
                if body.get("done") is False:
                    message = body.get("message", "")
                    content = message.get("content", "")
                    output += content
                if body.get("done", False):
                    return output

    except requests.exceptions.RequestException as e:
        return f"Error in connection: {e}"


# Main Page Render
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


# Responser Function for ollama API
@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("user_input")
    if user_input:
        # -- ollama Model Response (dictionary mode)
        messages = [{"role": "user", "content": user_input}]
        # -- Send and Receive Messages from ollama API
        response_message = chat(messages)
        # -- Response To Markdown Format
        formatted_response = markdown.markdown(response_message, extensions=['fenced_code', 'codehilite'])

        return jsonify({"response": formatted_response})
    return jsonify({"response": "No input provided!"})


# Run App (debug can be true or false)
if __name__ == "__main__":
    app.run(debug=True)
