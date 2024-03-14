# Collection Folder

This folder includes the scripts and the Jupyter Notebook that have been used on the Social5 Server to hydrate, preprocess, partially analyze, and visualize the Twitter data.

Explanation for individual files:

- **notebook.ipynb**: This notebook has been used for test purposes before implementing or writing a hydration and analysis script. It includes:
    - example embedded API routes
    - analysis of the number of collected tweets, in order to find out how many tweets have been collected and how many tweets are missing
    - test for API call, collecting missing tweets
    - method for getting the sample tweet data for the topic modeling
    - methods for visualizations that have been used in the thesis and presentations
- **requirements.txt**: all the required packages for hydrating the tweets
- **script_compare_methods.py**: The script has been used to compare the sync and async hydration pipelines.
- **script_hydrate_asynch.py**: This script includes an async hydation process, which is not used in this thesis, since other approaches were found to be faster.
- **script_hydrate_csv_second_batch.py**: This script has been used to collect the tweets in the second batch.
- **script_hydrate_csv_third_batch.py**: This script has been used to collect the tweets in the third batch by finding out the the missing tweets from the first and second batch, and then hydrating the missing tweets.
- **script_hydrate_txt.py**: This script has been used to collect tweets from .txt files that included Tweet IDs.
- **script_split_files.py**: This script has been used to split the .txt files into smaller .csv files. This process made the hydration pipeline much easier.
