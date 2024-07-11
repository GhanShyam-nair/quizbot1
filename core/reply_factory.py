
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):

    if current_question_id is None:
        return False, "No current question to answer."
    
    if not answer.strip():
        return False, "Answer cannot be empty."
    
    # Get existing answers or initialize an empty dict
    answers = session.get('answers', {})
    
    # Record the answer for the current question
    answers[str(current_question_id)] = answer.strip()
    
    # Update the session
    session['answers'] = answers
    
    return True, ""


def get_next_question(current_question_id):
     
    if current_question_id is None:
        # If there's no current question, return the first question
        return PYTHON_QUESTION_LIST[0]['question'], 0
    
    # Find the index of the current question
    current_index = next((index for index, q in enumerate(PYTHON_QUESTION_LIST) if q['id'] == current_question_id), None)
    
    if current_index is None:
        return None, None  # Current question not found
    
    # Check if there's a next question
    if current_index + 1 < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[current_index + 1]
        return next_question['question'], next_question['id']
    else:
        return None, None  # No more questions
    return "dummy question", -1


def generate_final_response(session):

    answers = session.get('answers', {})
    total_questions = len(PYTHON_QUESTION_LIST)
    answered_questions = len(answers)
    
    if answered_questions == 0:
        return "You haven't answered any questions yet."
    
    correct_answers = 0
    for question in PYTHON_QUESTION_LIST:
        question_id = str(question['id'])
        if question_id in answers:
            user_answer = answers[question_id].lower().strip()
            correct_answer = question['answer'].lower().strip()
            if user_answer == correct_answer:
                correct_answers += 1
    
    score_percentage = (correct_answers / total_questions) * 100
    
    response = f"Quiz completed! You answered {answered_questions} out of {total_questions} questions.\n"
    response += f"Your score: {correct_answers} correct answers ({score_percentage:.1f}%).\n\n"
    
    if score_percentage >= 90:
        response += "Excellent job! You have a strong grasp of Python concepts."
    elif score_percentage >= 70:
        response += "Good work! You have a solid understanding of Python, but there's room for improvement."
    elif score_percentage >= 50:
        response += "Not bad! You have a basic understanding of Python, but you might want to review some concepts."
    else:
        response += "It looks like you might need more practice with Python. Don't give up, keep learning!"
    
    return response
