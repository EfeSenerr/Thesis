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

# Define the transformation function
def extract_fields(json_obj):
    tweet_id = json_obj.get('tweet_id', '')
    tweet_type = json_obj.get('tweet_type', '')
    hashtags = json_obj.get('hashtags', [])
    mentions = json_obj.get('mentions', [])
    return {
        'tweet_id': tweet_id,
        'tweet_type': tweet_type,
        'hashtags': hashtags,
        'mentions': mentions
    }

# API call
def fetch_additional_info(tweet_id):
    url = "https://cdn.syndication.twimg.com/tweet-result"
    querystring = {"id": tweet_id, "lang": "en", "token": "x"}
    payload = ""
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://platform.twitter.com",
    "Connection": "keep-alive",
    "Referer": "https://platform.twitter.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers"
    }
    try:
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        if response.status_code != 200:
            # print(f"Failed to fetch additional info for tweet_id {tweet_id}")
            return None
    except Exception as e:
        logging.error(f'Failed to fetch additional info for tweet_id {tweet_id}')
        return None
    return response.text

# Extract the additional info from API response
def parse_api_response(api_response):
    if not api_response:
        return {}
    try:
        parsed_data = json.loads(api_response)
    except json.JSONDecodeError:
        logging.error(f'Failed: parse_api_response. Error.')
        return {}
    
    lang = parsed_data.get('lang', '')
    favorite_count = parsed_data.get('favorite_count', 0)
    created_at = parsed_data.get('created_at', '')
    text = parsed_data.get('text', '')
    parent_tweet_id = parsed_data.get('parent', {}).get('id_str', '')

    # New:
    hashtags = parsed_data.get('entities', {}).get('hashtags', '')
    mentions = parsed_data.get('user_mentions', {}).get('user_mentions', '')
    tweet_type = parsed_data.get('__typename', '')
    tweet_id = parsed_data.get('id_str', '')

    return {
        'tweet_id': tweet_id,
        'tweet_type': tweet_type,
        'hashtags': hashtags,
        'mentions': mentions,
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
def process_chunk(missing_tweet_ids, output_path: str, data_name: str):
    results = []
    
    for tweet_id in missing_tweet_ids:
        try:
            api_response = fetch_additional_info(tweet_id)
            additional_info = parse_api_response(api_response)
            result_row = {'tweet_id': tweet_id}
            result_row.update(additional_info)
        except Exception as e: 
            logging.error(f'Failed to process tweet_id {tweet_id}: {e}')

        results.append(result_row)
    
    result_df = pd.DataFrame(results)
    custom_write_csv(result_df, output_path, data_name)  # Pass output_path and data_name to custom_write_csv

# Used for parallel processing, main function here is process_chunk
def process_data_in_parallel(missing_tweet_ids, output_path: str, data_name: str):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        chunks = np.array_split(missing_tweet_ids, 10)
        # Use a lambda function to pass the output_path and data_name arguments to process_chunk
        executor.map(lambda chunk: process_chunk(chunk, output_path, data_name), chunks)

# processes a file, which is written for .txt, calls process_data_in_parallel
def process_file(file_path, output_path):
    logging.info(f'Processing file path: {file_path}')
    # Extract data_name from the file path
    data_name = os.path.basename(file_path).replace('.csv', '')
    
    # Get only the missing tweet IDs
    missing_tweet_ids = get_missing_tweet_ids_from_file(file_path)
    # Create the output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    # Process each chunk in parallel

    # Write the header to the output file
    output_file = os.path.join(output_path, f'output_{data_name}.csv')
    header_df = pd.DataFrame(columns=['tweet_id', 'tweet_type', 'hashtags', 'mentions', 'lang', 'favorite_count', 'created_at', 'text', 'parent_tweet_id'])
    header_df.to_csv(output_file, index=False)

    process_data_in_parallel(missing_tweet_ids, output_path, data_name)

def extract_number(filename):
    # Regular expression to match a sequence of digits
    match = re.search(r'_(\d+)\.csv$', filename)
    return int(match.group(1)) if match else 0

def process_all_files_in_folder(folder_path, output_folder_path, start_from_file=0):
    # Get all files in folder_path that end with .txt
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    # Sort files based on the numeric part of the filename
    sorted_files = sorted(files, key=extract_number)
    
    for index, file_name in enumerate(sorted_files, start=0):  # start enumeration from 0 for human-readable file numbers
        # Skip files before the 14th file
        if index < start_from_file:
            continue
        
        file_path = os.path.join(folder_path, file_name)
        logging.info(f'Processing file: {file_name}')
        process_file(file_path, output_folder_path)

def get_missing_tweet_ids_from_file(file_path):
    try:
        df = pd.read_csv(file_path, dtype={'tweet_id': 'Int64'}, usecols=['tweet_id', 'text', 'tweet_type'])
        # Filter out rows with empty 'text' or other critical fields
        missing_tweets = df[df['text'].isna() & df['tweet_id'].notna()]['tweet_id']
        return missing_tweets.to_list()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except pd.errors.EmptyDataError:
        logging.warning(f"No data in file: {file_path}")
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")

    return []

if __name__ == "__main__":
    warnings.filterwarnings(action='ignore', category=FutureWarning)
    
    # Configure logging to write to a file and the console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(filename='processing_missing_tweets.log'),
            logging.StreamHandler()
        ]
    )
    
    input_folder_path = '/home/esener/thesis/Thesis/data/output/stream_tweetids_2022-07_splitted'
    output_folder_path = '../data/output/missing_tweets/2_stream_tweetids_2022-07_splitted'

    # Create output folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)  
    process_all_files_in_folder(input_folder_path, output_folder_path, start_from_file=0)
    # process_file(input_file, output_folder_path)
    logging.info('Done processing all files')