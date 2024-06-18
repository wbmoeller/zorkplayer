This project is an experiment using AI (Gemini) to play a text adventure. It uses an interpreter for the old infocom games (frotz) and passes text back and forth between the interpreter and Gemini.

As part of the experiment I've written very little of the code myself. I asked Gemeni to generate the code in python and iterated, telling it the current error, issue or improvement and then copying the new code. In general it's done a decent job of moving towards a working solution...though if I hear "I'm sorry, you're right." one more time. But, I was able to get Gemini to play Zork with no experience in AI and limited experience with python in under a day.

For running locally:
1) Run with python3
2) make sure you have a python environement set up with pexpect, google-generativeai, getch
  a) Note: I'm on a mac, so I installed these in a virtual environment. Don't forget to run "source .venv/bin/activate" to get it back
3) create a local 'config.py' with the following properties:
  a) GEMINI_API_KEY="key" (The key is generated from the Google AI Studio here https://aistudio.google.com/)
  b) PROMPT_FILE_PATH = "ZTUU.prompt" (a prompt passed to gemini that contains the previous gameplay and most recent response from the interpreter)
  c) LOG_FILE_PATH = "gemini_suggestions.log" (file that can be watched to see gemini's thought process)
  d) ZORK_FILE_PATH = "games/ZTUU.Z5" (a z-code game file that you want to play)

Todo:
- I get a timeout with pexpect every time.  haven't dug in yet
- Gemini seems to do a decent job of learning from past mistakes (getting eaten by a GRU), but might be able to improve the prompt more
- Consider summarizing prior games when the game ends and saving that to pass into future prompts.  right now it "learns" from prior runs through the game within the same run of zp.py...but i think i can persist that learning across zp.py runs
- Drop the extra newlines from the accumulated output...it's ever-growing :-)

![Alt text](/images/playing_game.png?raw=true "Gemini playing Zork Underground")
