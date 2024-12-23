# Import the necessary libraries

# LangChain Imports
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_google_genai import ChatGoogleGenerativeAI

# Environment Management
from dotenv import load_dotenv
import os

# Local Imports
from .modify_midi_constants import VALID_INSTRUMENTS, VALID_NOTES, ACCEPTABLE_PARAMETERS

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    google_api_key=GEMINI_API_KEY,
    model=GEMINI_MODEL,
    temperature=0
)

# Define schemas for the output parser
schemas = [
    ResponseSchema(
        name=key,
        type=value['type'],
        description=f"{value['description']} Constraints: {value['constraints']}"
        if value.get("complex", False) else value["description"],
    )
    for key, value in ACCEPTABLE_PARAMETERS.items()
]

# Initialize the parser
parser = StructuredOutputParser.from_response_schemas(schemas)

# Prompt components
PREFIX = "You are a music AI assistant. Based on the user's description, generate parameters to modify a MIDI file."
INSTRUCTIONS = parser.get_format_instructions()
CONSTRAINTS = f""" 
1. Instruments MUST be chosen from the LIST of AVAILABLE INSTRUMENTS ONLY:
   {', '.join(VALID_INSTRUMENTS)}.

2. Scales must follow the '(Note)(Accidental)(Octave)_(Type)' format:
   Available Notes and Accidentals: {', '.join(VALID_NOTES)}.
   Available Types: major, minor.
"""

PROMPT_TEMPLATE = f"""
{PREFIX}

ENSURE OUTPUT FORMAT IS AS FOLLOWS:
{INSTRUCTIONS}

IMPORTANT CONSTRAINTS:
{CONSTRAINTS}
"""

def execute_query(text_query):
    """ 
    Execute a query using the Gemini model and parse the response.

    Args:
        text_query (str): The user query to execute.
        
    Returns:
        dict: The parsed response from the model.
    """
    try:
        gemini_response = llm.invoke(f"{PROMPT_TEMPLATE}\n\nUser request: {text_query}")

        parsed_response = parser.parse(gemini_response.content)

        return parsed_response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Test the utility
    example_query = "Make the song sound like a lofi slow hip hop beat."
    response = execute_query(example_query)
    if response:
        print("Parsed Response:")
        print(response)