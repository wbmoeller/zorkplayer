# I recommend copying this example to a config_<game>.py so that the .gitignore will
# exclude it from pushes to github (and avoid exposing an api key)

# Configuration
GEMINI_API_KEY="<ENTER_KEY_HERE>" # API Key for Gemini AI
GEMINI_MODEL="gemini-1.5-flash" # Gemini model to use

# Game
ZORK_FILE_PATH = "games/ZTUU.Z5" # Location of game file, currently supports z-code file format (interpreter is frontz)

# Prompts
PROMPT_FILE_PATH = "prompts/ZTUU.prompt" # Location of per-turn prompt, relative to run directory
SUMMARY_PROMPT_FILE_PATH = "prompts/summary.prompt" # Location of prompt that summarizes a game, relative to run directory
AGGREGATE_SUMMARY_PROMPT_FILE_PATH = "prompts/aggregate_summary.prompt" # Location of summary aggregation prompt, used to collapse the per-game summaries

# Temp Files
LOG_FILE_PATH = "debug_suggestions.log" # Location of debug log. tail -f <file> to see gemini's reasoning
SUMMARY_FILE_PATH = "summaries.txt"  # Persistent storage for summaries between games
