
from flask import Flask, request, render_template, jsonify
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

app = Flask(__name__)

@app.route('/')
def home():
  return render_template("index.html")
  
@app.route("/api/run_agent", methods=["POST"])
def run_agent():
    """
    API endpoint to run the LangChain agent with user input.
    """
    if not agent_executor:
        return jsonify({"output": "The agent is not available. Please check the server logs."}), 500

    data = request.json
    user_input = data.get("input", "")

    if not user_input:
        return jsonify({"output": "Please provide an input."}), 400

    try:
        # Pass the input to the agent and get the response
        result = agent_executor.invoke({"input": user_input, "chat_history": []})
        
        # Return the final output as a JSON response
        return jsonify({"output": result["output"]})

    except Exception as e:
        print(f"Error invoking agent: {e}")
        return jsonify({"output": "An error occurred while processing your request."}), 500

app.run(debug=False, host="0.0.0.0")
