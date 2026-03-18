import os
database_name = 'pick-place-random'
#create a new csv
compiled_result_filename = f'{database_name}_compiled_results_perm_4.csv'

for limit in range(1000,8001,1000):
    results_filename = f'results/{database_name}_{limit}_points_perm_4.csv'
    #check if the file exists
    file_exists = os.path.isfile(results_filename)
    if file_exists:
        #skip first line (header) and append to the compile
        with open(results_filename, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                with open(compiled_result_filename, 'a') as compiled_file:
                    compiled_file.writelines(lines[1:])
