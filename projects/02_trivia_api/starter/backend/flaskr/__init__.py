import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

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
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
    return response


  '''
  get_page_questions 
  '''
  def get_page_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [q.format() for q in selection]
    current_qs = questions[start:end]
    return current_qs
  
  '''
  get_formatted_categories
  '''
  def get_formatted_categories():
    categories = Category.query.order_by(Category.id).all()
    categories = [c.format() for c in categories]
    categories = {k: v for d in categories for k, v in d.items()}
    return categories

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories", methods=["GET"])
  def retrieve_categories():
    categories = get_formatted_categories()
    return jsonify({
      'success': True,
      'categories': categories,
      'current_category': None,
      })

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
  @app.route("/questions", methods=["GET"])
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_qs = get_page_questions(request, selection)
    if len(current_qs) == 0:
      abort(404)

    categories = get_formatted_categories()

    return jsonify({
      'success': True,
      'questions': current_qs,
      'total_questions': len(selection),
      'categories': categories,
      'current_category': None,
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:qid>", methods=["DELETE"])
  def delete_question(qid):
    q = Question.query.filter(Question.id==qid).delete()
    db.session.commit()
    return jsonify({
      'success': True,
      'id': qid,
      })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods=["POST"])
  def create_question():
    try:
      body = request.get_json()
      new_q = Question(**body)
      db.session.add(new_q)
      db.session.commit()

      return jsonify({
        'success': True,
        })

    except:
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
  @app.route("/questions/search", methods=["POST"])
  def search_questions():
    search_term = request.get_json()['searchTerm']
    selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    current_qs = get_page_questions(request, selection)


    return jsonify({
      'success': True,
      'questions': current_qs,
      'total_questions': len(selection),
      'current_category': None,
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<int:cid>/questions", methods=["GET"])
  def retrieve_category_questions(cid):
    selection = Question.query.filter(Question.category==cid).all()
    current_qs = get_page_questions(request, selection)
    if len(current_qs) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_qs,
      'total_questions': len(selection),
      'current_category': cid
      })


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
  @app.route("/quizzes", methods=["POST"])
  def play_quiz():
    try:
      body = request.get_json()
      prev_qs = body['previous_questions']
      cid = body['quiz_category']['id']
      print(prev_qs, cid)

      if cid == 0:
        selection = Question.query.filter(Question.id.notin_(prev_qs)).all()
      else:
        selection = Question.query.filter(Question.category==cid, Question.id.notin_(prev_qs)).all()
      
      current_qs = [q.format() for q in selection]

      if selection:
        q = current_qs[random.randint(0, len(selection)-1)]
      else:
        q = None

      return jsonify({
        'success': True,
        'question': q,
        })

    except:
      abort(422)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def not_found(error):
     return jsonify({
       'success': False,
       'error': 400,
       'message': "Bad request"
     }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "Resource not found"
    }), 404
  
  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': "Method not allowed"
    }), 405
  
  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': "Unprocessable entity"
    }), 422
  
  return app