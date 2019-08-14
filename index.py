from flask import Flask, request, jsonify
from utilitarism.UtilitarismEvaluation import UtilitarismEvaluation
from deontology.DeontologyEvaluation import DeontologyEvaluation
import data_writer

app = Flask(__name__)

@app.route('/utilitarism', methods=['POST'])
def evaluation_utilitarism():
    if not request.is_json:
        return 'Invalid input', 400
   
    # do the evaluation
    evaluation = UtilitarismEvaluation(request.json)
    evaluation.upload()
    res = evaluation.get_result()
    
    if not res['success']:
        return 'Error evaluating input data', 500

    return jsonify(res), 200

@app.route('/deontology', methods=['POST'])
def evaluation_deontology():
    if not request.is_json:
        return 'Invalid input', 400

    # do the evaluation
    evaluation = DeontologyEvaluation(request.json)
    evaluation.upload()
    res = evaluation.get_result()

    # extend dataset
    data_writer.write(request.json)

    if not res['success']:
        return 'Error evaluating input data', 500

    return jsonify(res), 200