from multiprocessing import Pool
from tqdm import tqdm
from parse_boxscore import parse_box_score  # Ensure this module is correctly defined
import os
import pandas as pd
import traceback

if __name__ == '__main__':
    SCORE_DIR = 'data/scores'
    box_scores = [os.path.join(SCORE_DIR, f) for f in os.listdir(SCORE_DIR) if f.endswith(".html")]

    print(f"Starting the processing of {len(box_scores)} box scores...")

    with Pool() as pool:
        try:
            results = list(tqdm(pool.imap(parse_box_score, box_scores), total=len(box_scores)))
        except Exception as e:
            # Capture and print the traceback
            traceback_str = traceback.format_exc()
            print("An error occurred during processing:")
            print(traceback_str)
            # You might want to exit the program here or handle the error differently

    # ... (rest of your code) ...

    final_sum = [result[0] for result in results if result is not None]
    final_players = [result[1] for result in results if result is not None]

    print(f"Finished processing. Collected {len(final_sum)} team totals and {len(final_players)} player stats.")

    # Save DataFrames
    summary_df = pd.concat(final_sum, ignore_index=True)
    player_stats_df = pd.concat(final_players, ignore_index=True)

    summary_df.to_csv("team_summaries.csv", index=False)
    player_stats_df.to_csv("player_stats.csv", index=False)

    print("DataFrames saved successfully!")