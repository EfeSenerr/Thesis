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
import timeit
import httpx
import asyncio
import re
import time

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
def process_chunk(df_chunk: pd.DataFrame, output_path: str, data_name: str):
    results = []

    for idx, row in df_chunk.iterrows():
        row_dict = row.to_dict()
        try:
            api_response = fetch_additional_info(row_dict['tweet_id'])
            additional_info = parse_api_response(api_response)
            row_dict.update(additional_info)
        except Exception as e: 
            logging.error(f'Failed to process chunk {e}')

        results.append(row_dict)
    result_df = pd.DataFrame(results)
    custom_write_csv(result_df, output_path, data_name)  # Pass output_path and data_name to custom_write_csv

# Used for parallel processing, main function here is process_chunk
def process_data_in_parallel(df, output_path: str, data_name: str):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        chunks = np.array_split(df, 10)
        # Use a lambda function to pass the output_path and data_name arguments to process_chunk
        executor.map(lambda chunk: process_chunk(chunk, output_path, data_name), chunks)

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

def process_all_files_in_folder(folder_path, output_folder_path):
    # Get all files in folder_path that end with .txt
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    # Sort files based on the numeric part of the filename
    sorted_files = sorted(files, key=extract_number)
    
    for file_name in sorted_files:
        file_path = os.path.join(folder_path, file_name)
        logging.info(f'Processing file: {file_name}')
        process_file(file_path, output_folder_path)

# Async API call
async def async_fetch_additional_info(tweet_id):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        response_text = await loop.run_in_executor(executor, fetch_additional_info, tweet_id)
    return response_text

# Async function to process a chunk of data
async def async_process_chunk(df_chunk: pd.DataFrame, output_path: str, data_name: str):
    results = []
    loop = asyncio.get_event_loop()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [loop.run_in_executor(executor, fetch_additional_info, row['tweet_id']) for idx, row in df_chunk.iterrows()]
        for future, (idx, row) in zip(asyncio.as_completed(futures), df_chunk.iterrows()):
            response_text = await future
            additional_info = parse_api_response(response_text)
            row_dict = row.to_dict()
            row_dict.update(additional_info)
            results.append(row_dict)

    result_df = pd.DataFrame(results)
    custom_write_csv(result_df, output_path, data_name)

# Function to process data in parallel
async def async_process_data_in_parallel(df, output_path: str, data_name: str):
    chunks = np.array_split(df, 10)
    tasks = [async_process_chunk(chunk, output_path, data_name) for chunk in chunks]
    await asyncio.gather(*tasks)


async def async_process_file(file_path, output_path):
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
    await async_process_data_in_parallel(df, output_path, data_name)

def extract_number(filename):
    # Regular expression to match a sequence of digits
    match = re.search(r'_(\d+)\.txt$', filename)
    return int(match.group(1)) if match else 0

async def async_process_all_files_in_folder(folder_path, output_folder_path):
    # Get all files in folder_path that end with .txt
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    # Sort files based on the numeric part of the filename
    sorted_files = sorted(files, key=extract_number)
    
    for file_name in sorted_files:
        file_path = os.path.join(folder_path, file_name)
        logging.info(f'Processing file: {file_name}')
        await async_process_file(file_path, output_folder_path)


def run_sync():
    input = '/home/esener/thesis/Thesis/data/testFolder'
    output = '/home/esener/thesis/Thesis/data/output/test_Folder'
    # The original synchronous code
    process_all_files_in_folder(input, output)  # replace with your actual arguments

async def run_async():
    input = '/home/esener/thesis/Thesis/data/testFolder'
    output = '/home/esener/thesis/Thesis/data/output/testFolder_asynch'
    # Run the updated asynchronous code
    await async_process_all_files_in_folder(input, output)

def time_async_function():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        start_time = time.time()
        loop.run_until_complete(run_async())
        end_time = time.time()
        return end_time - start_time
    finally:
        loop.close()


if __name__ == "__main__":
    warnings.filterwarnings(action='ignore', category=FutureWarning)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    
    # Configure logging to write to a file and the console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(filename='processing_test.log'),
            logging.StreamHandler()
        ]
    )
    
    input_folder_path = '../data/testFolder'
    output_folder_path = '../data/output/testFolder'

    # Create output folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)  
    # Timing the original synchronous code
    time_sync = timeit.timeit(
        stmt=f"run_sync()",
        setup="from __main__ import run_sync",
        number=1  # Adjust the number of repetitions as needed
    )
    print(f"Time taken by original synchronous code: {time_sync}")

    # # Timing the updated asynchronous code
    # time_async = timeit.timeit(
    #     stmt=f"run_async()",
    #     setup="from __main__ import run_async",
    #     number=1  # Adjust the number of repetitions as needed
    # )
    # print(f"Time taken by updated asynchronous code: {time_async}")

    elapsed_time = time_async_function()
    print(f"Time taken by updated asynchronous code: {elapsed_time}")

    # process_file(input_file, output_folder_path)
    logging.info('Done processing all files')