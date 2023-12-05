import warnings
import pandas as pd
import json
import csv
import requests
from typing import Dict, List, Any
import logging
import numpy as np
import concurrent.futures
import os
import re
from tweety import Twitter
import datetime
import time

# API call
def fetch_additional_info(app, tweet_id):
    try:
        tweet = app.tweet_detail(f"https://twitter.com/dbdevletbahceli/status/{tweet_id}")
    except Exception as e:
        # logging.error(f"An error occurred scraping {tweet_id}: {e}")
        return None

    return tweet

# Extract the additional info from API response
def parse_api_response(tweet):
    if tweet is None:
        return {
        'tweet_id': '',
        'tweet_type': "deleted",
        'hashtags': [],
        'mentions': [],
        'lang': '',
        'favorite_count': 0,
        'created_at': '',
        'text': '',
        'parent_tweet_id': '',         
    }
    
    # Extracting data directly from the tweet object
    lang = getattr(tweet, 'language', '')
    favorite_count = getattr(tweet, 'likes', 0)  # Assuming favorite_count is a property
    
    created_at = getattr(tweet, 'created_on', '')
    if isinstance(created_at, datetime.datetime):
        created_at = created_at.strftime('%Y-%m-%d %H:%M:%S %Z')    
    
    text = getattr(tweet, 'text', '')
    tweet_id = getattr(tweet, 'id', '')

    # New:
    # Assuming hashtags are stored in a list of hashtag objects within the tweet object
    hashtags = [hashtag["text"] for hashtag in getattr(tweet, 'hashtags', [])]    
    mentions = getattr(tweet, 'user_mentions', [])
    mentions_data = [{'id': getattr(user, 'id', ''), 'name': getattr(user, 'name', '')} for user in mentions]    
    parent_tweet_id = getattr(tweet, 'replied_to', '')
    # tweet_type = parsed_data.get('__typename', '')

    return {
        'tweet_id': tweet_id,
        'tweet_type': "Tweet",
        'hashtags': hashtags,
        'mentions': mentions_data,
        'lang': lang,
        'favorite_count': favorite_count,
        'created_at': created_at,
        'text': text,
        'parent_tweet_id': parent_tweet_id,         
    }
# Last function in the process, which converts dataframe to csv file
def custom_write_csv(df: pd.DataFrame, output_path: str, data_name: str):
    file_name = os.path.join(output_path, f'output_{data_name}.csv')
    try:
        df.to_csv(file_name, mode='a', index=False, header=False)
    except Exception as e:
        logging.error(f'Failed to write chunk {e}')
        

# Processes a chunk of data. The function is used in process_data_in_parallel, which chunks the given df into 10 chunks
def process_chunk(app, df_chunk: pd.DataFrame, output_path: str, data_name: str):
    results = []

    for idx, row in df_chunk.iterrows():
        row_dict = row.to_dict()
        try:
            api_response = fetch_additional_info(app, row_dict['tweet_id'])
            additional_info = parse_api_response(api_response)
            row_dict.update(additional_info)
            time.sleep(0.1)
        except Exception as e: 
            logging.error(f'Failed to process chunk {e}')

        results.append(row_dict)
    result_df = pd.DataFrame(results)        
    custom_write_csv(result_df, output_path, data_name)  # Pass output_path and data_name to custom_write_csv

# Used for parallel processing, main function here is process_chunk
def process_data_in_parallel(df, output_path: str, data_name: str):
    app = Twitter("session")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        chunks = np.array_split(df, 10)
        # Use a lambda function to pass the output_path and data_name arguments to process_chunk
        futures = [executor.submit(process_chunk, app, chunk, output_path, data_name) for chunk in chunks]
        concurrent.futures.wait(futures)

# processes a file, which is written for .txt, calls process_data_in_parallel
def process_file(file_path, output_path):
    logging.info(f'Processing file path: {file_path}')
    # Extract data_name from the file path
    data_name = os.path.basename(file_path).replace('.txt', '')
    
    # Read txt file and convert it to DataFrame
    with open(file_path, 'r') as file:
        tweet_ids = [int(line.strip()) for line in file]
    df = pd.DataFrame(tweet_ids, columns=['tweet_id'])
    # Create the output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Write the header to the output file
    output_file = os.path.join(output_path, f'output_{data_name}.csv')
    header_df = pd.DataFrame(columns=['tweet_id', 'tweet_type', 'hashtags', 'mentions', 'lang', 'favorite_count', 'created_at', 'text', 'parent_tweet_id'])
    header_df.to_csv(output_file, index=False)
    
    # Process each chunk in parallel
    process_data_in_parallel(df, output_path, data_name)


def extract_number(filename):
    # Regular expression to match a sequence of digits
    match = re.search(r'_(\d+)\.txt$', filename)
    return int(match.group(1)) if match else 0

def process_all_files_in_folder(folder_path, output_folder_path, start_from_file=0):
    # Get all files in folder_path that end with .txt
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    # Sort files based on the numeric part of the filename
    sorted_files = sorted(files, key=extract_number)
    
    for index, file_name in enumerate(sorted_files, start=0):  # start enumeration from 0 for human-readable file numbers
        # Skip files before the 14th file
        if index < start_from_file:
            continue
        
        file_path = os.path.join(folder_path, file_name)
        logging.info(f'Processing file: {file_name}')
        process_file(file_path, output_folder_path)

if __name__ == "__main__":
    warnings.filterwarnings(action='ignore', category=FutureWarning)
    
    # Configure logging to write to a file and the console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(filename='processing_test.log'),
            logging.StreamHandler()
        ]
    )
    
    input_folder_path = '/home/esener/thesis/Thesis/data/testFolder'
    output_folder_path = '../../data/output/testFolder'

    # Create output folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)  
    process_all_files_in_folder(input_folder_path, output_folder_path, start_from_file=0)
    # process_file(input_file, output_folder_path)
    logging.info('Done processing all files')