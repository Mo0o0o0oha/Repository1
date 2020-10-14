import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    def after_request(response):
        response.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type, Authorization, true'
        )
        response.headers.add(
          'Access-Control-Allow-Methods', 'GET,PUT,POST, DELETE, OPTIONS'
        )
        return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def retrieve_categories():
        '''
        Fetches a dictionary of categories in which the keys are the ids and
        the value is the corresponding string of the category.
        '''
        try:
            categories = Category.query.order_by(Category.id).all()

            return jsonify({
              'success': True,
              'categories': {
                category.id: category.type for category in categories
              }
            })
        except Exception:
            abort(422)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        '''
        Endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        '''
        try:

            page = request.args.get('page', 1, type=int)
            questions = Question.query \
                .order_by(Question.id) \
                .paginate(page=page, per_page=QUESTIONS_PER_PAGE)
            questions_flist = [
              question.format() for question in questions.items
            ]
            categories = Category.query.order_by(Category.id).all()
            categories_formatted = {
              category.id: category.type for category in categories
            }
            if len(questions_flist) == 0:
                abort(404)
            else:
                return jsonify({
                  'success': True,
                  'questions': questions_flist,
                  'total_questions': questions.total,
                  'categories': categories_formatted,
                  'current_category': None,
                })
        except Exception as e:
            if '404' in str(e):
                abort(404)
            else:
                abort(422)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.query \
              .filter(Question.id == question_id) \
              .one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
              'success': True,
              'deleted': question_id,
            })
        except Exception as e:
            if '404' in str(e):
                abort(404)
            else:
                abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        '''
        Endpoint to create a new question
        '''
        request_data = request.get_json()
        question = request_data.get('question', None)
        answer = request_data.get('answer', None)
        difficulty = request_data.get('difficulty', None)
        category = request_data.get('category', None)
        try:
            question = Question(
              question=question,
              answer=answer,
              difficulty=difficulty,
              category=category
            )
            question.insert()
            return jsonify({
              'success': True,
              'created': question.id,
            })
        except Exception:
            abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/search', methods=['POST'])
    def search_question():
        '''
        Endpoint to search questions based on a term
        '''
        request_data = request.get_json()
        search = request_data.get('searchTerm', None)
        try:
            questions = Question.query \
              .order_by(Question.id) \
              .filter(Question.question.ilike('%{}%'.format(search)))
            questions_flist = [
              question.format() for question in questions
            ]
            return jsonify({
              'success': True,
              'questions': questions_flist,
              'total_questions': len(questions.all()),
              'current_category': None,
            })
        except Exception:
            abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        '''
        Create a GET endpoint to get questions based on category.
        '''
        try:
            page = request.args.get('page', 1, type=int)
            questions = Question.query \
                .order_by(Question.id) \
                .filter(Question.category == category_id) \
                .paginate(page=page, per_page=QUESTIONS_PER_PAGE)
            questions_flist = [
              question.format() for question in questions.items
            ]
            if len(questions_flist) == 0:
                abort(404)
            else:
                return jsonify({
                  'success': True,
                  'questions': questions_flist,
                  'total_questions': questions.total,
                  'current_category': category_id
                })
        except Exception as e:
            if '404' in str(e):
                abort(404)
            else:
                abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def retrieve_quizzes():
        '''
        Endpoint to get questions to play the quiz.
        '''
        try:
            questions = None
            request_data = request.get_json()
            quiz_category = request_data.get('quiz_category', None)
            previous_qids = request_data.get('previous_questions', None)
            category_id = quiz_category.get('id')
            if category_id == CATEGORY_ALL:
                questions = Question.query.all()
            else:
                questions = Question.query \
                    .filter(Question.category == category_id) \
                    .all()
            questions_flist = [q.format() for q in questions]
            avaliable_ids = [q.get('id') for q in questions_flist]
            ids = list(set(avaliable_ids).difference(previous_qids))
            if len(ids) == 0:
                return jsonify({
                  'success': True,
                  'question': None
                })
            else:
                random_question = random.choice(ids)
                question = Question.query.get(random_question)

                return jsonify({
                  'success': True,
                  'question': question.format()
                })

        except Exception:
            abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
      @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500
  return app

    