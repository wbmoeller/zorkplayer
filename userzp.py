import pexpect
import time
import os

def run_zork_command(command, child):
    """Runs a command in Frotz using pexpect."""
    child.sendline(command)
    
    # Wait for the prompt, with a timeout
    try:
        child.expect("> ", timeout=2)
    except pexpect.TIMEOUT:
        print(f"Warning: Timed out waiting for prompt after command '{command}'")

    output = child.before.decode('utf-8', errors='replace').strip() # Decode and clean
    return output

# Start Frotz process with -m and -q flags
child = pexpect.spawn("dfrotz -m -q /Users/williammoeller/zorkplayer/ZTUU.Z5")

# Main game loop
while True:
    command = input("Enter your command: ")
    if command.lower() == "quit":
        break
    output = run_zork_command(command, child)
    print(output)

child.terminate()  # Close the Frotz process when done
