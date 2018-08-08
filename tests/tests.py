# -*- coding:UTF-8 -*-
__author__ = "ChenQing"
__date__ = "2018-07-25 14:47"

import unittest
from application import app

class ApplicationTest(unittest.TestCase):
    def setUp(self):
        print('setup')
    '''
    def setUpClass(cls):
        print('setup class')
    '''
    def tearDown(self):
        print('tearDown')

    def test1(self):
        print('test1')
    def test2(self):
        print('test2')