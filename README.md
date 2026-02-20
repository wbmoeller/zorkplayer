# Zork Player
This project is an experiment using AI (initially Gemini) to play a text adventure. It uses an interpreter for the old infocom games (frotz) and passes text back and forth between the interpreter and Gemini.

As part of the experiment I've written very little of the code myself. I asked Gemeni to generate the code in python and iterated, telling it the current error, issue or improvement and then copying the new code. In general it's done a decent job of moving towards a working solution...though if I hear "I'm sorry, you're right." one more time. But, I was able to get Gemini to play Zork with no experience in AI and limited experience with python in under a day.

## Thoughts on AI
Feb 19, 2026
- It's pretty interesting, after updating the project to use gemini-3.0-flash...it plays the game decently. It makes appropriate decisions, doesn't seem to get stuck in loops, in 30 moves it got 40 points.
- Claude Code did a great job analyzing this old project and making quick updates. Even spotted a bug in the pexpect matching.
- I'm curious to start using Claude Code to clean the project up. At the time I was using gemini to write the code and it fell to pieces. But that was before agentic ai - i started using windsurf a few months later and it was a game changer.

(Keeping this for posterity - written around Nov 2024)
_Disclaimer: I'm early in playing around with building apps with AI and all of my opinions are formed from the latest iteration of Gemini, which isn't the best AI tool for writing code_
- It was very easy to get started writing a program in a (mostly) unfamiliar language and domain. I described what I wanted to build and it made suggestions and output mostly working code. I could iterate with it when there was a bug or error and improve on the code as we went.
- It did a very good job of finding tools and libraries to support my project, suggesting the frotz interpreter and writing the code to interface with the AI assistants with ease. I particularly like that it didn't just write the code, but it pointed me at the websites needed to get things set up and the steps I needed to go through with python to configure dependent libraries.
- As the program got more complicated, gemini started to abreviate the code in the python file (lots of "# ... (same as before)") and i needed to ask gemini to print the entire contents of zp.py pretty often. might be able to solve this with a better initial prompt
- Once I asked it to re-architect the code into multiple files things went downhill fast. It started mixing in old code (and old bugs) and even completely changing how some of the functions worked with no apparent reason. It also got challenging when I asked to print the contents of a file...because it would apply "code enhancements" to the file each time, which changed interfaces that other files were dependent on.
- It's pretty fun watching gemini play zork...and it's not very good at it. There are a couple of things that I should be able to fix, like when they go back to a place previously visited gemini thinks that it didn't move while the game thinks they're in the new location. This could be fixed by a better prompt around the current game state...or by having gemini "look" when it gets lost like this.
- Zork underground seems to be _much_ less forgiving of a game than the original Zork. In Zork the AI will get stuck in an endless loop in the forest or around the canyon. The grues eat the player consistently in Zork Underground.

## Running Locally
1. Run with python3
2. make sure you have a python environement set up and 'pip install' the following libraries
    - pexpect
    - google-genai
    - anthropic
    - openai
    - getch
  - Note: I'm on a mac, so I installed these in a virtual environment. Don't forget to run "source .venv/bin/activate" to get it back
3. make a copy of ./configs/example_config.py to ./configs/config_<game>.py and add the key for your APIs. gemini was easy to set up [here](https://aistudio.google.com/)
4. you can `tail -f ai_suggestions.log` while the game is running to see how gemini comes up with it's actions. sometimes the explanations are priceless :-) 

## Todo
- I get a timeout with pexpect every time. haven't dug in yet
- Tried running it with the original zork...performance is pretty crummy. It gets stuck in the forest going in circles. It also gets stuck in the canyon (permanently) trying to climb down. I tried including the gemini thought process and it does _slightly_ better, but still gets stuck.
- Ask gemini for architectural improvements
  -  It suggested an agent-based architecture but when I asked it to apply the architecture the code kinda unraveled (it mixed in old bugs and old versions of the code with the new architecture). Haven't gotten back to this yet
  -  It suggested using scoring to improve the performance over time
- Consider moving the summary into a database
- I think there's an AI architectural pattern (RAG) this is implicitly following where the summaries are injected back into the next iteration. Officially separate that out into its own module
- Abstract out the game interpreter into a module
- Generate tests
- Handle going back to a previuos location better. Zork doesn't print anything when you go back, you just get the prompt...and this often confuses Gemini about the current game state

## Results
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

![Alt text](/images/playing_game.png?raw=true "Gemini playing Zork Underground")
