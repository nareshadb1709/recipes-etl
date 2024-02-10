import unittest
from unittest.mock import patch, mock_open
import os
import sys
import argparse
from datetime import timedelta  
from etl_scripts import download_json, process_recipes, parse_time, categorize_difficulty, save_to_csv, calculate_averages

class TestETLScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        
        cls.base_directory = os.path.dirname(__file__)
        cls.test_data_dir = os.path.join(cls.base_directory, 'test_data')
        cls.dummy_json_path = os.path.join(cls.test_data_dir, 'test_dummy_json_file.json')
        cls.test_url = "https://bnlf-tests.s3.eu-central-1.amazonaws.com/recipes.json"  # Replace with actual URL to download test data
        
        
        if not os.path.exists(cls.test_data_dir):
            os.makedirs(cls.test_data_dir, exist_ok=True)
        
        
        download_json(cls.test_url, cls.dummy_json_path)

    @classmethod
    def tearDownClass(cls):
        
        if os.path.exists(cls.dummy_json_path):
            os.remove(cls.dummy_json_path)

    def test_download_json(self):
        """Verify that download_json can successfully download and save a file."""
        
        self.assertTrue(os.path.exists(self.dummy_json_path), "Downloaded test data file should exist.")
        self.assertGreater(os.path.getsize(self.dummy_json_path), 0, "Downloaded test data file should not be empty.")

    def test_process_recipes(self):
        """Test the process_recipes function with actual downloaded data."""
        recipes, total_times = process_recipes(self.dummy_json_path)
        self.assertTrue(len(recipes) > 0, "Should process at least one recipe from the downloaded data.")

    def test_parse_time(self):
        """Test parse_time with various ISO 8601 duration strings."""
        self.assertEqual(parse_time("PT15M"), timedelta(minutes=15), "15 minutes should be parsed correctly.")
        self.assertEqual(parse_time("PT1H"), timedelta(hours=1), "1 hour should be parsed correctly.")

    def test_categorize_difficulty(self):
        """Test categorize_difficulty with various total cooking times."""
        self.assertEqual(categorize_difficulty(timedelta(minutes=10)), 'Easy', "Should be categorized as Easy.")
        self.assertEqual(categorize_difficulty(timedelta(minutes=45)), 'Medium', "Should be categorized as Medium.")
        self.assertEqual(categorize_difficulty(timedelta(hours=2)), 'Hard', "Should be categorized as Hard.")

    

if __name__ == '__main__':
    unittest.main()
