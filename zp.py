import config
import pexpect
import logging
import google.generativeai as genai
from getch import getch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_zork_command(command, child):
    """Runs a command in Frotz using pexpect."""
    child.sendline(command)
    try:
        child.expect("> ", timeout=2)
    except pexpect.TIMEOUT:
        print(".")  # Visual indicator of timeout
    return child.before.decode('utf-8', errors='replace').strip()

def get_gemini_suggestion(zork_history, zork_output, prompt_file, log_file):
    """Gets a suggested command from Gemini, logging to a file."""
    with open(prompt_file, 'r') as f:
        prompt_template = f.read()
    prompt = prompt_template.format(zork_history=zork_history, zork_output=zork_output)

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content(prompt)
        
        # Write suggestion and explanation to log file
        with open(log_file, 'a') as log:
            log.write(f"============ Gemini Suggestion:\n{response.text}\n-------------------\n")

        return response
    except Exception as e:  
        logging.error(f"Error generating Gemini suggestion: {e}")
        return None  

prompt_file_path = "ZTUU.prompt"
log_file_path = "gemini_suggestions.log"

# Start Frotz process with -m and -q flags
child = pexpect.spawn("dfrotz -m -q games/ZTUU.Z5")

# Clear the log file at the start
with open(log_file_path, 'w') as log:
    pass  

# Get the initial prompt
zork_output = run_zork_command("", child)
history = ""

# Main game loop
while True:
    response = get_gemini_suggestion(history, zork_output, prompt_file_path, log_file_path)

    if response is None:
        print("Error getting suggestion from Gemini. Skipping this turn.")
        continue

    try:
        if response.candidates[0].finish_reason == "SAFETY":
            logging.warning(f"Gemini flagged a safety issue:\n{response}")
        else:
            suggestion = response.text
            action = suggestion.split("**")[1].split("**")[0].strip()

            zork_output = run_zork_command(action, child)
            history = history + "\n" + zork_output
            print(zork_output)

    except Exception as e:
        logging.error(f"Error parsing Gemini response: {e}")
        print("Error processing response. Skipping this turn.")

    print("Continue playing? (n to stop): ", end='', flush=True)
    choice = getch()
    print(choice)
    if choice.lower() == "n":
        break

child.terminate()
