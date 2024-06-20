import argparse
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

def aggregate_summaries(summary_file_path):
    """Asks Gemini to create an aggregate summary of the summaries in the file."""

    with open(summary_file_path, "r") as f:
        all_summaries = f.read()

    prompt = f"""
    You are an AI assistant that has been provided with summaries of 10 games of Zork.
    
    Summaries:
    {all_summaries}

    Your task is to analyze these summaries and generate a single, comprehensive summary of the player's overall experience with the game. Include common themes, challenges, successes, and any recurring patterns in the player's actions or decisions.
    """

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response.text

# Main game loop
def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Play Zork with Gemini AI assistance.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode: prompt after each turn.")
    args = parser.parse_args()

    child = pexpect.spawn(f"dfrotz -m -q {config.ZORK_FILE_PATH}")
    zork_output = run_zork_command("", child)  # Get initial output
    history = ""

    # Clear the log file at the start
    with open(config.LOG_FILE_PATH, 'w') as log:
        log.write("#################################\n")
        log.write("#######  NEW GAME  ###########\n")
        log.write("#################################\n")

    # Read past summaries
    try:
        with open(config.SUMMARY_FILE_PATH, 'r') as f:
            past_summaries = f.read()
            num_summaries = past_summaries.count("-----------")
    except FileNotFoundError:
        past_summaries = ""
        num_summaries = 0

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

        # Check for game end and enough summaries
        if ("RESTART" in zork_output or "QUIT" in zork_output): 
            summary = summarize_game(history)
            print(summary)

            if num_summaries >= 9:
                # Aggregate summaries and rewrite file
                aggregated_summary = aggregate_summaries(config.SUMMARY_FILE_PATH)
                print(f"\n--------- Reached 10 summaries, aggregating:\n{aggregated_summary}")
                with open(config.SUMMARY_FILE_PATH, 'w') as f:
                    f.write(aggregated_summary)
            
            break

        # Ask user if they want to continue (only in interactive mode)
        if args.interactive:  # Check if -i/--interactive flag was used
            print("Continue playing? (n to stop): ", end='', flush=True)
            choice = getch()
            print(choice)
            if choice.lower() == "n":
                break

    child.terminate()

if __name__ == "__main__":
    main()
