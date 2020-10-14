import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(data['current_category'], None)

    def test_404_get(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'], 24)
        self.assertEqual(res.status_code, 200)

    def test_delete_question(self):
        res = self.client().delete('/questions/24')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 24)
        self.assertEqual(res.status_code, 200)

    def test_404_delete(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_questions(self):
        res = self.client().post(
            '/search',
            json={'searchTerm': 'Taj Mahal'}
        )
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], None)
        self.assertEqual(res.status_code, 200)

    def test_search_questions_empty(self):

        res = self.client().post(
            '/search',
            json={'searchTerm': 'NODATA'}
        )
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], None)
        self.assertEqual(res.status_code, 200)

    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category'], 1)
        self.assertEqual(res.status_code, 200)

    def test_404_category_questions(self):

        res = self.client().get('/categories/1000/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(res.status_code, 404)

    def test_quizzes(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': '0',
                'type': 'All'
            }
        })
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)
        self.assertEqual(res.status_code, 200)

    def test_quizzes_category(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)
        self.assertEqual(res.status_code, 200)

    def test_quizzes_category_previousquestions(self):

        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 14],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)
        self.assertEqual(res.status_code, 200)

    def test_quizzes_category_allpreviousquestions(self):

        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 14, 15],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)
        self.assertEqual(res.status_code, 200)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()