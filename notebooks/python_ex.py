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

warnings.filterwarnings(action='ignore', category=FutureWarning)
logging.basicConfig(filename='processing.log', level=logging.INFO)

# data_name = 'streamV2_tweetnet_2023-06'

# # Read the JSONL file
# df = pd.read_json(f'../data/{data_name}.jsons', lines=True)

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
        #logging.error(f'Failed to fetch additional info for tweet_id {tweet_id}')
        return None
    return response.text


def parse_api_response(api_response):
    if not api_response:
        return {}
    try:
        parsed_data = json.loads(api_response)
    except json.JSONDecodeError:
        print(f"Failed to parse API response: {api_response}")
        return {}
    
    lang = parsed_data.get('lang', '')
    favorite_count = parsed_data.get('favorite_count', 0)
    created_at = parsed_data.get('created_at', '')
    text = parsed_data.get('text', '')
    parent_tweet_id = parsed_data.get('parent', {}).get('id_str', '')
    
    return {
        'lang': lang,
        'favorite_count': favorite_count,
        'created_at': created_at,
        'text': text,
        'parent_tweet_id': parent_tweet_id
    }


def write_row_to_csv(row):
    try:
        with open('output_{data_name}.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['tweet_id', 'tweet_type', 'hashtags', 'mentions', 'lang', 'favorite_count', 'created_at', 'text', 'parent_tweet_id'])
            writer.writerow(row)
    except Exception as e:
        print(f"Failed to write row to CSV: {e}")


# Function to process a single JSON object (this includes the API call)
def process_json_object(json_obj):
    try: 
        # Extract initial fields
        row = extract_fields(json_obj)
        
        # Fetch additional info from API (You'll have to add your API logic)
        api_response = fetch_additional_info(row['tweet_id'])
        
        # Parse the API response
        additional_info = parse_api_response(api_response)
        
        # Merge initial data and additional info
        row.update(additional_info)
        
        # Write the row to CSV
        write_row_to_csv(row)
    except Exception as e:
        print(f"Failed to process JSON object: {e}")


def custom_write_csv(df: pd.DataFrame, file_name: str):
    try:
        df.to_csv(file_name, mode='a', index=False, header=False)
    except Exception as e:
        print(f"Failed to write chunk: {e}")

# Define a function to process a chunk of data
def process_chunk(df_chunk: pd.DataFrame, file_name: str):
    results = []
    for idx, row in df_chunk.iterrows():
        row_dict = row.to_dict()
        api_response = fetch_additional_info(row_dict['tweet_id'])
        additional_info = parse_api_response(api_response)
        row_dict.update(additional_info)
        # Convert hashtags and mentions array to a comma-separated string
        row_dict['hashtags'] = ','.join(row_dict['hashtags']) if isinstance(row_dict['hashtags'], (list, tuple)) else ''
        row_dict['mentions'] = ','.join(row_dict['mentions']) if isinstance(row_dict['mentions'], (list, tuple)) else ''
        results.append(row_dict)
    result_df = pd.DataFrame(results)
    # Filter the DataFrame to only include the columns specified in the schema
    result_df = result_df[['tweet_id', 'tweet_type', 'hashtags', 'mentions', 'lang', 'favorite_count', 'created_at', 'text', 'parent_tweet_id']]
    custom_write_csv(result_df, file_name)

def process_data_in_parallel(df, output_file):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        chunks = np.array_split(df, 10)
        # Use a lambda function to pass the file_name argument to process_chunk
        executor.map(lambda chunk: process_chunk(chunk, output_file), chunks)

folder_path = './streamV2_tweetnet_2023-06_splitted'
output_folder_path = '../data/output/streamV2_tweetnet_2023-06_splitted'
# os.makedirs(output_folder_path, exist_ok=True)  # Create output folder if it doesn't exist

def process_file(file_path):
    # Extract data_name from the file path
    data_name = os.path.basename(file_path).replace('.jsons', '')
    df = pd.read_json(file_path, lines=True)
    output_file = os.path.join(output_folder_path, f'output_{data_name}.csv')  # Update this line to use output_folder_path

    # Write the header to the output file
    header_df = pd.DataFrame(columns=['tweet_id', 'tweet_type', 'hashtags', 'mentions', 'lang', 'favorite_count', 'created_at', 'text', 'parent_tweet_id'])
    header_df.to_csv(output_file, index=False)
    
    # Process each chunk in parallel
    process_data_in_parallel(df, output_file)

def process_all_files_in_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.jsons'):
            file_path = os.path.join(folder_path, file_name)
            print(f'Processing file: {file_name}')  # Print the file name for tracking
            process_file(file_path)

if __name__ == "__main__":
    os.makedirs(output_folder_path, exist_ok=True)  # Create output folder if it doesn't exist
    process_all_files_in_folder(folder_path)