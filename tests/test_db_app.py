"""
It is a module which make a simple test of main.py from main_app directory
"""
import unittest
from unittest.mock import patch
from db_app.db_app import app

class TestDbApp(unittest.TestCase):
    '''Create a class for testing'''
    def setUp(self):
        ''' Create a test client'''
        app.config['TESTING'] = True
        self.client = app.test_client()