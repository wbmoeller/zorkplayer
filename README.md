This project is an initial experiment using AI (Gemini) to play a text adventure. It uses an interpreter for the old infocom games (frotz) and passes back and forth between the interpreter and Gemini.

As part of the experiment, I've written very little of the code myself. I asked Gemeni to generate the code in python and needed to go through several rounds of refinement to get it to this point. In general it's done a decent job of getting around to a working solution...though if I hear "I'm sorry, you're right." one more time...

For running locally:
1) Run with python3
2) make sure you have a python environement set up with pexpect, google-generativeai, getch
  a) Note: I'm on a mac, so I installed these in a virtual environment. Don't forget to run "source .venv/bin/activate" to get it back
3) create a local 'config.py' with GEMINI_API_KEY="key"
  a) The key is generated from the Google AI Studio here https://aistudio.google.com/

Todo:
- Currently keeps saying "go north" because it's only paying attention to the first part of the input
- pexpect gets a timeout every time. haven't dug in yet
- I don't like how it prints the whole thing every time. Probably want to separate out the current prompt from the historical prompts.
