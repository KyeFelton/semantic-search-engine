import io
import os
import stardog
from tqdm import tqdm

def run_sparql_tests(conn, db_name, test_dir):
    print('Running sparql tests')
    failed_tests = []
    test_count = 0
    input_dir = test_dir + 'input/'
    output_dir = test_dir + 'output/'
    for test_file in tqdm(os.listdir(input_dir)):
        with open(input_dir + test_file, 'r') as f:
            result = conn.select(f.read(), content_type=stardog.content_types.CSV).decode('ascii').split('\n')
        with open(output_dir + test_file[:-4] + '.csv', 'r') as f:
            expected = f.readlines()
        for i in range(0, len(expected)):
            if result[i].strip() != expected[i].strip():
                failed_tests.append([ test_file, i, expected[i].strip(), result[i].strip() ])
                test_count += 1
                break
        test_count += 1  
        

    if len(failed_tests) == 0:
        print('Passed all sparql tests :)')
    else:
        print(f'Failed {len(failed_tests)} tests:')
        for test in failed_tests:
            print(f'Test: {test[0]}')
            print(f'Line: {test[1]}')
            print(f'Expected: {test[2]}')
            print(f'Actual: {test[3]}')