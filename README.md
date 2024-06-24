This project is an experiment using AI (Gemini) to play a text adventure. It uses an interpreter for the old infocom games (frotz) and passes text back and forth between the interpreter and Gemini.

As part of the experiment I've written very little of the code myself. I asked Gemeni to generate the code in python and iterated, telling it the current error, issue or improvement and then copying the new code. In general it's done a decent job of moving towards a working solution...though if I hear "I'm sorry, you're right." one more time. But, I was able to get Gemini to play Zork with no experience in AI and limited experience with python in under a day.

For running locally:
1) Run with python3
2) make sure you have a python environement set up and 'pip install' pexpect, google-generativeai, anthropic, openai, getch
  a) Note: I'm on a mac, so I installed these in a virtual environment. Don't forget to run "source .venv/bin/activate" to get it back
3) make a copy of ./configs/example_config.py to ./configs/config_<game>.py and add the gemini api key

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
- Tried running it with the original zork...performance is pretty crummy. It gets stuck in the forest going in circles. It also gets stuck in the canyon (permanently) trying to climb down. I tried including the gemini thought process and it does _slightly_ better, but still gets stuck.
- Abstract out the AI api
- Swap from Gemini to OpenAI to see if it does any better
- Ask gemini for architectural improvements
- Consider moving the summary into a database
- I think there's an AI architectural pattern (RAG) this is implicitly following where the summaries are injected back into the next iteration. Officially separate that out into its own module
- Abstract out the game interpreter into a module
- Generate tests

- Handle going back to a previuos location better. Zork doesn't print anything when you go back, you just get the prompt...and this often confuses Gemini about the current game state

![Alt text](/images/playing_game.png?raw=true "Gemini playing Zork Underground")
