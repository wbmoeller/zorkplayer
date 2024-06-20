import pexpect
import logging
import google.generativeai as genai
from getch import getch
import sys
import argparse
import importlib.util
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_zork_command(command, child):
    """Runs a command in Frotz using pexpect, with a timeout."""
    child.sendline(command)
    try:
        child.expect("> ", timeout=1)  
    except pexpect.TIMEOUT:
        print(".")
    return child.before.decode('utf-8', errors='replace').strip()

def get_gemini_suggestion(zork_history, zork_output, past_summaries, config):
    """Gets a suggested command from Gemini, incorporating past summaries."""
    with open(config.PROMPT_FILE_PATH, 'r') as f:
        prompt_template = f.read()
    prompt = prompt_template.format(zork_history=zork_history, zork_output=zork_output, past_summaries=past_summaries)

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    try:
        response = model.generate_content(prompt)

        with open(config.LOG_FILE_PATH, 'a') as log:
            log.write(f"============ Gemini Suggestion:\n{response.text}\n-------------------\n")

        return response
    except Exception as e:  
        logging.error(f"Error generating Gemini suggestion: {e}")
        return None  

def summarize_game(history, config):
    """Asks Gemini to summarize the game based on the history."""
    with open(config.SUMMARY_PROMPT_FILE_PATH, 'r') as f:  
        summary_prompt_template = f.read()

    summary_prompt = summary_prompt_template.format(history=history)
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    response = model.generate_content(summary_prompt)

    summary = response.text
    with open(config.SUMMARY_FILE_PATH, 'a') as f:
        f.write("-----------\n")  
        f.write(summary + "\n")  

    return summary

def aggregate_summaries(config):
    """Asks Gemini to create an aggregate summary of the summaries in the file."""
    with open(config.SUMMARY_FILE_PATH, "r") as f:
        all_summaries = f.read()

    with open(config.AGGREGATE_SUMMARY_PROMPT_FILE_PATH, "r") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(all_summaries=all_summaries)

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    response = model.generate_content(prompt)

    return response.text

# Main game loop
def main():
    parser = argparse.ArgumentParser(description="Play Zork with Gemini AI assistance.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode: prompt after each turn.")
    parser.add_argument("-c", "--config", default="configs/config.py", help="Path to config.py file (default: configs/config.py)")
    args = parser.parse_args()

    # Load config module dynamically
    spec = importlib.util.spec_from_file_location("config", args.config)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    child = pexpect.spawn(f"dfrotz -m -q {config_module.ZORK_FILE_PATH}")

    # Clear the log file at the start
    with open(config_module.LOG_FILE_PATH, 'w') as log:
        log.write("#################################\n")
        log.write("#######  NEW GAME  ###########\n")
        log.write("#################################\n")

    # Read past summaries
    try:
        with open(config_module.SUMMARY_FILE_PATH, 'r') as f:
            past_summaries = f.read()
            num_summaries = past_summaries.count("-----------")
    except FileNotFoundError:
        past_summaries = ""
        num_summaries = 0

    # Get the initial prompt
    zork_output = run_zork_command("", child)  
    history = ""

    while True:
        response = get_gemini_suggestion(history, zork_output, past_summaries, config_module)

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

        # Check for game end and enough summaries
        if ("RESTART" in zork_output or "QUIT" in zork_output) and num_summaries >= 9: 
            summary = summarize_game(history, config_module)
            print(summary)

            # Aggregate summaries and rewrite file
            aggregated_summary = aggregate_summaries(config_module)
            with open(config_module.SUMMARY_FILE_PATH, 'w') as f:
                f.write(aggregated_summary)
            
            break

        # Ask user if they want to continue (only in interactive mode)
        if args.interactive: 
            print("Continue playing? (n to stop): ", end='', flush=True)
            choice = getch()
            print(choice)
            if choice.lower() == "n":
                break

    child.terminate()

if __name__ == "__main__":
    main()
