import config
import pexpect
import os
import google.generativeai as genai
from getch import getch

def run_zork_command(command, child):
    """Runs a command in Frotz using pexpect."""
    child.sendline(command)
    try:
        child.expect("> ", timeout=2) 
    except pexpect.TIMEOUT:
        print(f"Warning: Timed out waiting for prompt after command '{command}'")
    return child.before.decode('utf-8', errors='replace').strip()

def get_gemini_suggestion(zork_output, prompt_file):
    """Gets a suggested command from Gemini using the Google AI API."""

    with open(prompt_file, 'r') as f:
        prompt_template = f.read()

    prompt = prompt_template.format(zork_output=zork_output)

    # Replace with your actual API key
    genai.configure(api_key=config.GEMINI_API_KEY)

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response


prompt_file_path = "ZTUU.prompt"

# Start Frotz process with -m and -q flags
child = pexpect.spawn("dfrotz -m -q games/ZTUU.Z5")

# get the initial prompt
zork_output = run_zork_command("", child)  

# Main game loop
while True:
    response = get_gemini_suggestion(zork_output, prompt_file_path)

    suggestion = response.text
    print(f"============ Gemini explanation:\n{suggestion}\n-------------------")

    # Extract the action from the text (assuming it's still surrounded by **)
    action = suggestion.split("**")[1].split("**")[0].strip()

    output = run_zork_command(action, child)
    print(output)

    # Ask user if they want to continue (single-character input)
    print("Continue playing? (n to stop): ", end='', flush=True)  # No newline
    choice = getch()  # Get single character
    print(choice)  # Echo the character (optional)
    if choice.lower() == "n":
        break

child.terminate() 
