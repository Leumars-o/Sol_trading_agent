""" This module is responsible for generating the questions and answers for the quiz.

    Returns:
        _type_: dict
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GENAI_API_KEY'))

# Quiz Prompt Structure
structure = '{\
"question" : " ",\
"options" : ["", "", "", ""],\
"explanation" : "" (200 chars max),\
"correct_option_id" : \
}'


# Prompt Configuration
prompt = f"Generate an interesting quiz question for {languages[random_number]} in the format: {structure}"

file = open('gemini_prompt.txt', 'r')
prompt = file.read()
file.close()

# AI Model Configuration
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

# Create the AI model
model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

# Start a chat session
chat_session = model.start_chat(
  history=[]
)

# Prompt the model
def prompt_model():
  """ This function is responsible for prompting the AI model
  
    Args:
        prompts (_type_): list
        prompt_index (_type_): int

    Returns:
        _type_: dict
                The response from the AI model
    """
  # Send the prompt to the model
  response = chat_session.send_message(prompt)
  
  # Clean up the response
  response_data = response.text.replace("```json", "").replace("}\n```", "}").strip()

  # Convert the response type to dict
  response_clean = eval(response_data)
  # Return the response dict
  return (response_clean)

#   print(response_clean)


# prompt_model()