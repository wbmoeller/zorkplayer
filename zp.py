import config
import pexpect
import logging
import google.generativeai as genai
from getch import getch
import sys

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

def get_gemini_suggestion(zork_history, zork_output, past_summaries):
    """Gets a suggested command from Gemini, incorporating past summaries."""
    with open(config.PROMPT_FILE_PATH, 'r') as f:
        prompt_template = f.read()
    prompt = prompt_template.format(zork_history=zork_history, zork_output=zork_output, past_summaries=past_summaries)

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
    with open(config.SUMMARY_PROMPT_FILE_PATH, 'r') as f:  
        summary_prompt_template = f.read()

    summary_prompt = summary_prompt_template.format(history=history)
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(summary_prompt)

    summary = response.text
    with open(config.SUMMARY_FILE_PATH, 'a') as f:
        f.write("-----------\n")  # Add separator before the summary
        f.write(summary + "\n")  

    return summary

# Main game loop
def main():
    # Parse command-line arguments
    interactive_mode = False
    for arg in sys.argv[1:]:
        if arg == "-i":
            interactive_mode = True
        elif arg == "-h":
            print("Usage: python zp.py [-i] [-h]")
            print("-i: Interactive mode. Prompts the user after each turn.")
            print("-h: Display this help message.")
            return

    child = pexpect.spawn(f"dfrotz -m -q {config.ZORK_FILE_PATH}")
    
    # Clear the log file at the start
    with open(config.LOG_FILE_PATH, 'w') as log:
        log.write("#################################\n")
        log.write("#######  NEW GAME  ###########\n")
        log.write("#################################\n")

    # Read past summaries
    try:
        with open(config.SUMMARY_FILE_PATH, 'r') as f:
            past_summaries = f.read()
    except FileNotFoundError:
        past_summaries = ""

    # Get the initial prompt
    zork_output = run_zork_command("", child)  # Get initial output
    history = ""

    while True:
        response = get_gemini_suggestion(history, zork_output, past_summaries)

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

        # Check for game end
        if "RESTART" in zork_output or "QUIT" in zork_output:
            print(summarize_game(history))
            break

        # Ask user if they want to continue (only in interactive mode)
        if interactive_mode:
            print("Continue playing? (n to stop): ", end='', flush=True)
            choice = getch()
            print(choice)
            if choice.lower() == "n":
                break

    child.terminate()

if __name__ == "__main__":
    main()
