from flask import Flask, Response, request
import json
import pyodbc

app = Flask(__name__)

conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=26.166.82.69,4000;'
                      'Database=PythonIdz;'
                      'UID=admin;'
                      'PWD=123')


@app.route('/api', methods=['GET'])
def get_all_questions():
    cursor = conn.cursor()
    cursor.execute('SELECT Question, Answer FROM Questions')
    rows = cursor.fetchall()

    questions = {}
    for row in rows:
        question, answer = row
        questions[question] = answer

    json_data = json.dumps({'questions': questions}, ensure_ascii=False).encode('utf-8')
    return Response(json_data, content_type='application/json; charset=utf-8')


@app.route('/api/questions', methods=['GET'])
def get_questions_by_test():
    test_id = request.args.get('test_id')

    cursor = conn.cursor()
    cursor.execute('SELECT Question, Answer FROM Questions WHERE TestId = ?', test_id)
    rows = cursor.fetchall()

    questions = [{'question': row[0], 'answer': row[1]} for row in rows]

    json_data = json.dumps({'questions': questions}, ensure_ascii=False).encode('utf-8')
    return Response(json_data, content_type='application/json; charset=utf-8')


def write_to_database(count, points, Username, TestId, DateOfPassage):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (TestId, Username, DateOfPassage, NumberOfPoints, NumberOfQuestions) VALUES (?, ?, ?, ?, ?)", TestId, Username, DateOfPassage, points, count)
    conn.commit()


@app.route('/api/tests', methods=['GET'])
def get_tests():
    cursor = conn.cursor()
    cursor.execute('SELECT Id, TestName FROM Tests')
    rows = cursor.fetchall()

    tests = [{'id': row[0], 'name': row[1]} for row in rows]

    json_data = json.dumps({'tests': tests}, ensure_ascii=False).encode('utf-8')
    return Response(json_data, content_type='application/json; charset=utf-8')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
