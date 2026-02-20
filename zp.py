import pexpect
import logging
import openai
from google import genai
from anthropic import Anthropic
from getch import getch
import sys
import time
import argparse
import importlib.util
import os

# TODO
# - fix timeout of expect
# - in order to reduce number of tokens, periodically summarize the game so far and replace the history
# - extract the RAG into a service.  the RAG is what generates the prompt each time
# - is it possible (or even idomatic) to keep the files open for writing?
# - switch to using a database for the RAG instead of files
# - move the AI behind an interface that can be swapped out by service provider or model
# - modularize
# - add unit tests
# - start scoring the AI models based on the score it reached, number of rounds, (?)

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def run_zork_command(command, child, config):
    """Runs a command in Frotz using pexpect, with a timeout. 
       Returns text after the last '>'.
    """
    child.sendline(command)
    return get_last_zork_output(child, config)

def get_last_zork_output(child, config):
    try:
        child.expect(">", timeout=5)
    except pexpect.TIMEOUT:
        print(".")
    
    # full text of the game so far including the prompt for the next action
    output = child.before.decode('utf-8', errors='replace')

    return parse_zork_output(output)

def parse_zork_output(output):
    """
    Extracts the most recent response from Zork's output, handling multi-line responses,
    blank lines, and cases where the game ends (e.g., player death, winning).
    """
    lines = output.splitlines()

    # Find the index of the last ">" prompt
    last_prompt_index = None
    for i, line in enumerate(reversed(lines)):
        if line.strip().startswith(">"):
            last_prompt_index = len(lines) - 1 - i  # Convert to forward index
            break

    # If no prompt was found, return everything
    if last_prompt_index is None:
        return output  # Return everything for the initial prompt

    # Handle restart/quit prompt differently
    if "RESTART" in lines[-1] or "QUIT" in lines[-1]:
        start_index = last_prompt_index  # Return everything after the last prompt
    else:
        # Otherwise, extract the lines between the last two prompts (or since the last prompt)
        second_to_last_prompt_index = None
        for i in range(last_prompt_index - 1, -1, -1):
            if lines[i].strip().startswith(">"):
                second_to_last_prompt_index = i
                break

        start_index = second_to_last_prompt_index + 1 if second_to_last_prompt_index is not None else 0

    return "\n".join(lines[start_index:]).strip()

def create_ai_client(config):
    """Creates and returns an AI client for the configured provider."""
    if config.AI_PROVIDER == "gemini":
        return genai.Client(api_key=config.GEMINI_API_KEY)
    elif config.AI_PROVIDER == "openai":
        return openai.OpenAI(api_key=config.OPENAI_API_KEY)
    elif config.AI_PROVIDER == "claude":
        return Anthropic(api_key=config.CLAUDE_API_KEY)
    else:
        raise ValueError(f"Invalid AI provider: {config.AI_PROVIDER}")

def get_ai_response(prompt, config, client):
    """Gets a response from the configured AI provider."""

    try:
        if config.AI_PROVIDER == "gemini":
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
                config={"max_output_tokens": 500}
            )
            return response.text
        elif config.AI_PROVIDER == "openai":
            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Zork player."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
            )
            return response.choices[0].message.content
        elif config.AI_PROVIDER == "claude":
            response = client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            raise ValueError(f"Invalid AI provider: {config.AI_PROVIDER}")

    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        return None

def get_ai_suggestion(zork_history, zork_output, past_summaries, config, client, total_input_token_count, total_output_token_count):
    """Gets a suggested command from the configured AI provider."""
    with open(config.PROMPT_FILE_PATH, 'r') as prompt_file:
        prompt_template = prompt_file.read()
    prompt = prompt_template.format(zork_history=zork_history, zork_output=zork_output, past_summaries=past_summaries)

    start = time.time()
    suggestion = get_ai_response(prompt, config, client)
    print(f"[history: {len(zork_history)} chars | response: {len(suggestion)} chars | time: {time.time() - start:.1f}s]")

    # capture approximate costs into our debug file
    with open(config.DEBUG_LOG_FILE_PATH, 'a') as debug_file:
        debug_file.write(f"################################\n")
        input_token_count = approximate_token_count(config, prompt)
        total_input_token_count += input_token_count
        debug_file.write(f"$$$ Input Tokens: ~{input_token_count}\n")
        debug_file.write(f"$$$ Input Token Total for Game: ~{total_input_token_count}\n")
        # NOTE: i'm not actually sure if the entire response is counted for output tokens
        #   or if it's just the output response text. assuming the output text for now
        output_token_count = approximate_token_count(config, suggestion)
        total_output_token_count += output_token_count
        debug_file.write(f"$$$ Output Tokens: ~{output_token_count}\n")
        debug_file.write(f"$$$ Output Token Total for Game: ~{total_output_token_count}\n")            
        debug_file.write(f"============ Gemini Suggestion:\n{suggestion}\n")

    with open(config.AI_SUGGESTIONS_FILE_PATH, 'a') as suggestions_file:
        suggestions_file.write(f"################################\n")
        suggestions_file.write(f"################################\n")
        # suggestions_file.write(f"=== zork_history:\n{zork_history}\n")
        suggestions_file.write(f"=== most recent zork_output:\n{zork_output}\n")
        suggestions_file.write(f"============ Gemini Suggestion:\n{suggestion}\n")

    # Try including gemini's thought process in the running summary to improve model performance
    # Note: this didn't perform much better once i cleaned up the history and most recent response from gemini
    # with open(config.SUMMARY_FILE_PATH, 'a') as f:
    #    f.write(f"============ Gemini Suggestion:\n{response.text}\n")

    return suggestion, total_input_token_count, total_output_token_count

def summarize_game(history, config, client):
    """Asks the AI provider to summarize the game based on the history."""
    with open(config.SUMMARY_PROMPT_FILE_PATH, 'r') as f:
        summary_prompt_template = f.read()
    summary_prompt = summary_prompt_template.format(history=history)
    summary = get_ai_response(summary_prompt, config, client)

    with open(config.SUMMARY_FILE_PATH, 'a') as f:
        f.write("-----------\n")
        f.write(summary + "\n")
    return summary

def aggregate_summaries(config, client):
    """Asks the AI provider to create an aggregate summary of the summaries in the file."""
    with open(config.SUMMARY_FILE_PATH, "r") as all_summaries_file:
        all_summaries = all_summaries_file.read()
    with open(config.AGGREGATE_SUMMARY_PROMPT_FILE_PATH, "r") as aggregate_summary_prompt_file:
        prompt_template = aggregate_summary_prompt_file.read()
    prompt = prompt_template.format(all_summaries=all_summaries)

    return get_ai_response(prompt, config, client)

def approximate_token_count(config, text):
    """Approximates the number of tokens in a string based on the 3.5 words/token rule."""

    words = text.split()
    num_words = len(words)
    return round(num_words / config.APPROX_WORDS_PER_TOKEN)  # Round to the nearest integer

# Main game loop
def main():
    parser = argparse.ArgumentParser(description="Play Zork with AI assistance.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode: prompt after each turn.")
    parser.add_argument("-c", "--config", default="configs/config.py", help="Path to config.py file (default: configs/config.py)")
    args = parser.parse_args()

    # Load config module dynamically
    if not os.path.exists(args.config):
        parser.print_usage()
        print(f"error: config file not found: {args.config}")
        print(f"       copy configs/example_config.py to {args.config} and fill in your API keys.")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("config", args.config)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    client = create_ai_client(config)
    child = pexpect.spawn(f"dfrotz -m -q {config.ZORK_FILE_PATH}")
    new_game_header = """
    #################################
    #######  NEW GAME  ###########
    #################################
    """

    # Clear the log file at the start
    with open(config.AI_SUGGESTIONS_FILE_PATH, 'w') as suggestions_file:
        suggestions_file.write(new_game_header)
    # Debug counters for cost
    total_input_token_count = 0
    total_output_token_count = 0
    # put a marker in our debug log
    with open(config.DEBUG_LOG_FILE_PATH, 'a') as debug_file:
        debug_file.write(new_game_header)

    # Read past summaries
    try:
        with open(config.SUMMARY_FILE_PATH, 'r') as all_summaries_file:
            past_summaries = all_summaries_file.read()
            num_summaries = past_summaries.count("-----------")
    except FileNotFoundError:
        past_summaries = ""
        num_summaries = 0

    # Get the initial prompt
    zork_output = get_last_zork_output(child, config)
    print(zork_output)
    history = zork_output

    while True:
        suggestion, total_input_token_count, total_output_token_count = get_ai_suggestion(history, zork_output, past_summaries, config, client, total_input_token_count, total_output_token_count)
        if suggestion is None:
            print("Error getting suggestion from AI provider. Skipping this turn.")
            continue
        
        try:
            action = suggestion.split("**")[1].split("**")[0].strip()
            zork_output = run_zork_command(action, child, config)
            zork_action_and_response = ">" + action + "\n\n" + zork_output
            history = history + "\n" + zork_action_and_response
            print(zork_action_and_response)
        except Exception as e:
            logging.error(f"Error parsing AI response: {e}")
            print("Error processing response. Skipping this turn.")

        # Check for game end
        if "RESTART" in zork_output or "QUIT" in zork_output:
            summary = summarize_game(history, config, client)
            print(summary)

            # Only aggregate summaries if there are enough
            if num_summaries >= 9:
                aggregated_summary = aggregate_summaries(config, client)
                with open(config.SUMMARY_FILE_PATH, 'w') as f:
                    f.write(aggregated_summary)

            # Prompt for restart
            print("Restart game? (y/n): ", end='', flush=True)
            choice = getch()
            print(choice)
            if choice.lower() == "y":
                zork_output = run_zork_command("RESTART", child, config) # Restart game
                history = "" # Reset history for the new game
                # Clear the log file for the new game
                with open(config.AI_SUGGESTIONS_FILE_PATH, 'w') as log:
                    log.write("#################################\n")
                    log.write("#######  NEW GAME  ###########\n")
                    log.write("#################################\n")
            else:
                break

        # Ask user if they want to continue (only in interactive mode)
        if args.interactive:
            print("Continue playing? (y to continue): ", end='', flush=True)
            choice = getch()
            print(choice)
            if choice.lower() != "y":
                break

    child.terminate()

if __name__ == "__main__":
    main()
