import subprocess
import sys
import os
from etl_scripts import run_etl_process as etl_process_run
from etl_scripts import ensure_directories as ensure_directories
def run_tests():
    """Run the test suite."""
    test_script_path = os.path.join(os.path.dirname(__file__), 'etl_tests.py')
    result = subprocess.run([sys.executable, test_script_path], capture_output=True, text=True)
    
    print(result.stdout)
    if result.returncode != 0:
        print("Tests failed. Exiting.")
        sys.exit(1)
    else:
        print("All tests passed successfully.")

def run_etl_process():
    """Run the ETL process, managing directory creation and file handling."""
    directories = ensure_directories()
    
    etl_process_run()

if __name__ == '__main__':
    print("Running ETL tests...")
    run_tests()
    
    print("Running ETL process...")
    run_etl_process()
