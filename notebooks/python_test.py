import os

def split_file(file_path, lines_per_file, output_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Get the base name of the input file (without extension)
    base_name = os.path.basename(file_path).rsplit('.', 1)[0]

    for i in range(0, len(lines), lines_per_file):
        # Construct the path for the smaller files
        small_file_name = f"{base_name}_{i // lines_per_file}.txt"
        small_file_path = os.path.join(output_path, small_file_name)
        with open(small_file_path, 'w') as small_file:
            small_file.writelines(lines[i:i + lines_per_file])

# Ensure the output directory exists
os.makedirs('../data/streamV2_tweetids_2023-03', exist_ok=True)

# Call the function
split_file('../data/streamV2_tweetids_2023-03.txt', 100000, '../data/streamV2_tweetids_2023-03')