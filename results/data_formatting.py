import os
database_name = 'pick-place-random'
#create a new csv
compiled_result_filename = f'results/{database_name}_compiled_results.csv'

for limit in range(500,6501,500):
    results_filename = f'results/{database_name}_{limit}_points.csv'
    #check if the file exists
    file_exists = os.path.isfile(results_filename)
    if file_exists:
        #skip first line (header) and append to the compile
        with open(results_filename, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                with open(compiled_result_filename, 'a') as compiled_file:
                    compiled_file.writelines(lines[1:])

