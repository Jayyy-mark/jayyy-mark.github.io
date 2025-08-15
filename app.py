
from flask import Flask, request, render_template, jsonify
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@tool
def get_current_weather(location: str) -> str:
    """
    Retrieves the current weather for a given location.
    
    Args:
        location: The city and state (e.g., "San Francisco, CA").
    
    Returns:
        A string with the current weather information.
    """
    if "san francisco" in location.lower():
        return "The current weather in San Francisco is 65°F and sunny."
    elif "new york" in location.lower():
        return "The current weather in New York is 40°F and cloudy."
    else:
        return f"Sorry, I cannot get the weather for {location}."

# --- Initialize the model and agent once when the server starts ---
# This is more efficient than initializing it on every request.
try:
    tools = [get_current_weather]
    llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. Use the tools provided to answer the user's questions."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print("LangChain agent initialized successfully!")

except Exception as e:
    print(f"Error initializing LangChain agent: {e}")
    agent_executor = None # Ensure agent is None if initialization fails.


# --- Flask Routes ---

@app.route('/')
def home():
  return render_template("index.html")
  
@app.route("/chat", methods=["POST"])
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
