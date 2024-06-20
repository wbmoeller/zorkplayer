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
  e) SUMMARY_PROMPT_FILE_PATH = "summary.prompt" (location of prompt that generates summaries)
  f) SUMMARY_FILE_PATH = "zork_summaries.txt" (name of where we persist the summaries)


I found the summary of summaries from Gemini to be entertaining:
> The player's experience with Zork is a consistent pattern of failure, driven by a combination of poor decision-making and a lack of preparation. In every game, the player is tasked by the Grand Inquisitor with exploring the Great Underground Empire (GUE), armed with a useless plastic sword and a brass lantern.
> 
> The player's typical journey begins with being trapped in a tunnel by falling boulders, forcing them to continue deeper into the GUE.  They then explore the GUE's Cultural Center, often visiting the Royal Theater, which is described as cavernous and impressive.
> 
> The player's biggest challenge, and ultimately their downfall in every game, is the grue. These fearsome creatures lurk in dark, unexplored areas, and they quickly devour unsuspecting players. The player repeatedly makes the mistake of venturing into pitch-black areas, usually after dropping their lantern, leading to an inevitable encounter with a grue.
> 
> Despite visiting several locations, the player never manages to complete any puzzles or overcome any major obstacles. This suggests a lack of exploration skills, as they consistently fail to notice clues, gather information, or make strategic decisions. Their actions often seem impulsive and driven by curiosity rather than a plan.
> 
> The player's consistent failure to avoid the grue highlights the importance of preparedness in Zork.  The game rewards players who are cautious, resourceful, and avoid venturing into the unknown without proper tools or strategies.  In contrast, the player's lack of planning and preparedness results in a string of repeated failures, culminating in their demise at the hands of the ever-present grue.

Todo:
- I get a timeout with pexpect every time. haven't dug in yet
- Tweak the prompt
- Handle going back to a previuos location better. Zork doesn't print anything when you go back, you just get the prompt...and this often confuses Gemini about the current game state

![Alt text](/images/playing_game.png?raw=true "Gemini playing Zork Underground")
