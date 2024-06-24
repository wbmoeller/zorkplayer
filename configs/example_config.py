# I recommend copying this example to a config_<game>.py so that the .gitignore will
# exclude it from pushes to github (and avoid exposing an api key)

# Configuration
AI_PROVIDER = "gemini"  # Choose "gemini", "claude" or "openai"
GEMINI_API_KEY="<ENTER_KEY_HERE>" # API Key for Gemini AI
GEMINI_MODEL="gemini-1.5-flash" # Gemini model to use
OPENAI_API_KEY = "<YOUR_OPENAI_API_KEY>"  
OPENAI_MODEL = "gpt-3.5-turbo"  # Specify your desired OpenAI model
CLAUDE_API_KEY = "<YOUR_CLAUDE_API_KEY>"
CLAUDE_MODEL = "claude-2"  # You can use other Claude models as well
APPROX_WORDS_PER_TOKEN = 3.5 # used for rough calculation of costs, get from ai model documentation

# Game
ZORK_FILE_PATH = "games/ZTUU.Z5" # Location of game file, currently supports z-code file format (interpreter is frontz)

# Prompts
PROMPT_FILE_PATH = "prompts/ZTUU.prompt" # Location of per-turn prompt, relative to run directory
SUMMARY_PROMPT_FILE_PATH = "prompts/summary.prompt" # Location of prompt that summarizes a game, relative to run directory
AGGREGATE_SUMMARY_PROMPT_FILE_PATH = "prompts/aggregate_summary.prompt" # Location of summary aggregation prompt, used to collapse the per-game summaries

# Temp Files and logging
AI_SUGGESTIONS_FILE_PATH = "ai_suggestions.log" # Location of AI suggestions log. tail -f <file> to see the AI's reasoning
DEBUG_LOG_FILE_PATH = "debug.log" # location of debug logging
SUMMARY_FILE_PATH = "summaries.txt"  # Persistent storage for summaries between games
