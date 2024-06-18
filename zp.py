import config
import pexpect
import logging
import google.generativeai as genai
from getch import getch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_zork_command(command, child):
    """Runs a command in Frotz using pexpect, with a timeout."""
    child.sendline(command)
    try:
        child.expect("> ", timeout=1)  # Reduced timeout to 1 second
    except pexpect.TIMEOUT:
        print(".")
    return child.before.decode('utf-8', errors='replace').strip()

def get_gemini_suggestion(zork_history, zork_output):
    """Gets a suggested command from Gemini, logging to a file."""
    with open(config.PROMPT_FILE_PATH, 'r') as f:
        prompt_template = f.read()
    prompt = prompt_template.format(zork_history=zork_history, zork_output=zork_output)

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash') 
    try:
        response = model.generate_content(prompt)

        with open(config.LOG_FILE_PATH, 'a') as log:
            log.write(f"============ Gemini Suggestion:\n{response.text}\n-------------------\n")

        return response
    except Exception as e:  
        logging.error(f"Error generating Gemini suggestion: {e}")
        return None  

def summarize_game(history):
    """Asks Gemini to summarize the game based on the history."""
    with open(config.SUMMARY_PROMPT_FILE_PATH, 'r') as f:  # Read prompt from file
        summary_prompt_template = f.read()

    summary_prompt = summary_prompt_template.format(history=history)
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(summary_prompt)

    return response.text

# Main game loop
def main():
    child = pexpect.spawn(f"dfrotz -m -q {config.ZORK_FILE_PATH}")
    zork_output = run_zork_command("", child)  # Get initial output
    history = ""

    # Clear the log file at the start
    with open(config.LOG_FILE_PATH, 'w') as log:
        log.write("#################################\n")
        log.write("#######    NEW GAME   ###########\n")
        log.write("#################################\n")

    while True:
        response = get_gemini_suggestion(history, zork_output)

        if response is None:
            print("Error getting suggestion from Gemini. Skipping this turn.")
            continue
        
        try:
            if response.candidates[0].finish_reason == "SAFETY":
                logging.warning(f"Gemini flagged a safety issue:\n{response}")
            else:
                suggestion = response.text
                action = suggestion.split("**")[1].split("**")[0].strip()

                zork_output = run_zork_command(action, child)  # Decreased timeout to 1
                history = history + "\n" + zork_output
                print(zork_output)

        except Exception as e:
            logging.error(f"Error parsing Gemini response: {e}")
            print("Error processing response. Skipping this turn.")

        # Check for game end
        if "RESTART" in zork_output or "QUIT" in zork_output:
            print(summarize_game(history))
            break

        print("Continue playing? (n to stop): ", end='', flush=True)
        choice = getch()
        print(choice)
        if choice.lower() == "n":
            break

    child.terminate()

if __name__ == "__main__":
    main()
