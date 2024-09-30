import json
from flask import Flask, request, Response
import requests
from flask_cors import CORS, cross_origin
from agent import format_output, translate
from agrifyCoach import recommend
from agrifyScore import generate_score
from agrifyReport import generate_report
from carbon_calculator import calc_carbon
from datetime import date, timedelta, timezone
from random import randint, uniform
# ---------------Environmental Variable------------------------
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
os.environ["TAVILY_API_KEY"] = os.getenv('TAVILY_API_KEY')

# langchain Monitoring
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Agrifyapp"
# --------------------------------------------------------------

SOIL_DATA_URL = os.getenv('SOILDATA_URL')
CREATE_SOILDATA_URL = os.getenv('CREATE_SOILDATA_URL')
RECOMMENDATION_SUBMISSION_SERVER = os.getenv(
    'RECOMMENDATION_SUBMISSION_SERVER')

DEBUG = True
app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/')
@cross_origin(supports_credentials=True)
def hello():
    return 'AGRIFY AI SERVER'


@app.route('/score', methods=["POST"])
@cross_origin(supports_credentials=True)
def Score():
    try:
        data = request.data.decode()
        data = json.loads(data)
        llm = data.get("model") if data.get("model") else "llama"

        # get farm id from the json sent
        farmId = data.get("FarmId")
        url = SOIL_DATA_URL+farmId

        # read the json recovered
        soilContent = requests.get(url=url)
        data = soilContent.json()

        result = generate_score(llm_name=llm, reflect_sys=None, **data)
        result = format_output(result, "score")
        return Response(json.dumps(result), status=201, mimetype='application/json')
    except:
        return Response(json.dumps({"success": 'false'}), status=404, mimetype='application/json')


@app.route('/recommend', methods=["POST"])
@cross_origin(supports_credentials=True)
def Recommend():
    try:
        # print("entered")
        data = request.data.decode()
        data = json.loads(data)

        llm = data.get("model") if data.get("model") else "llama"
        language = data.get("lang") if data.get("lang") else "English"

        # get farm id from the json sent
        farmId = data.get("FarmId")
        farmer_name = data.get("FarmerName")
        # area = data.get("Area")
        url = SOIL_DATA_URL+farmId

        # read the json recovered
        soilContent = requests.get(url=url)
        data = soilContent.json()
        data["FarmerName"] = farmer_name
        # data["Area"] = area
        # print("Data", data)
        # if data:
        # print(f"using {llm} as model and language as {language}")

        result = recommend(language=language,
                           reflect_sys=None, llm_name=llm, **data)
        result = format_output(result, "recommend")

        score = generate_score(llm_name=llm, reflect_sys=None, **data)
        score_result = format_output(score, "score")["Score"]
        score_result = int(score_result.split('/')[0])

        # Get today's date
        today = date.today()
        # Calculate the date 3 months from now
        three_months_from_now = today + timedelta(days=30 * 3)
        # Format the dates as "YYYY-MM-DDTHH:MM:SS.000Z"
        period_start = today.strftime("%Y-%m-%dT00:00:00.000Z")
        period_end = three_months_from_now.strftime(
            "%Y-%m-%dT23:59:59.000Z")

        result_json = {
            "PeriodStart": period_start,
            "PeriodEnd": period_end,
            "FarmerName": data['FarmerName'],
            "FarmId": data['FarmId'],
            "FarmScore": score_result,
            "RecommendationsIntro": result["Recommendation_intro"],
            "Month1": result["phase_1"],
            "Month2": result["phase_2"],
            "Month3": result["phase_3"],
            "RecommendationsSummary": result["Recommendation_summary"]
        }
        # else:
        #     data = dummy
        #     result = recommend(language=language,
        #                        reflect_sys=None, llm_name=llm, **data)
        #     result = format_output(result, "recommend")

        #     score = generate_score(llm_name=llm, reflect_sys=None, **data)
        #     score_result = eval(format_output(score, "score")["Score"])*100

        #     # Get today's date
        #     today = date.today()
        #     # Calculate the date 3 months from now
        #     three_months_from_now = today + timedelta(days=30 * 3)
        #     # Format the dates as "YYYY-MM-DDTHH:MM:SS.000Z"
        #     period_start = today.strftime("%Y-%m-%dT00:00:00.000Z")
        #     period_end = three_months_from_now.strftime(
        #         "%Y-%m-%dT23:59:59.000Z")

        #     result_json = {
        #         "PeriodStart": period_start,
        #         "PeriodEnd": period_end,
        #         "FarmerName": "John Doe",
        #         "FarmId": farmId,
        #         "FarmScore": score_result,
        #         "RecommendationsIntro": result["Recommendation_intro"],
        #         "Month1": result["phase_1"],
        #         "Month2": result["phase_2"],
        #         "Month3": result["phase_3"],
        #         "RecommendationsSummary": result["Recommendation_summary"]
        #     }
        status = requests.post(
            RECOMMENDATION_SUBMISSION_SERVER, json=result_json)
        if status.status_code == 201:
            response_data = status.json()
            return Response(json.dumps({'success': "true"}), status=status.status_code, mimetype='application/json')
        else:
            return Response(json.dumps({"success": "false", "error": status.text}), status=status.status_code, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"success": "false", "message": f"{e}"}), status=404, mimetype='application/json')


@app.route('/report', methods=["POST"])
@cross_origin(supports_credentials=True)
def Report():
    data = request.data.decode()
    data = json.loads(data)

    llm = data.get("model") if data.get("model") else "llama"
    result = generate_report(llm_name=llm, **data)

    result_dict = {"response": result}
    return json.dumps(result_dict)


@app.route('/soil_data', methods=["POST"])
@cross_origin(supports_credentials=True)
def SoilData():
    try:
        data = request.get_json()

        # Safely access FarmId from the data
        farm_id = data.get('FarmId')

        # Get today's date
        today = date.today()

        # Calculate the date 3 months from now
        three_months_from_now = today + timedelta(days=30 * 3)
        # Format the dates as "YYYY-MM-DDTHH:MM:SS.000Z"
        period_start = today.strftime("%Y-%m-%dT00:00:00.000Z")
        period_end = three_months_from_now.strftime("%Y-%m-%dT23:59:59.000Z")

        result_json = {
            "PeriodStart": period_start,
            "PeriodEnd": period_end,
            "FarmId": farm_id,
            "ClayContent": f"{uniform(0,50):.1f}",
            "CEC": f"{randint(5,50)}",
            "SoilDepth": "20 cm",
            "SiltContent": f"{uniform(0,50):.1f}",
            "SandContent": f"{uniform(0,50):.1f}",
            "SoilMoisture": f"{uniform(0,70):.1f}",
            "SoilPH": f"{uniform(3,9):.1f}",
            "NitrogenContent": f"{uniform(1.5,4.5):.1f}",
            "BulkDensity": f"{uniform(1,3):.1f} g/cm³",
            "Area": 50.0
        }

        response = requests.post(CREATE_SOILDATA_URL, json=result_json)

        if response.status_code == 201:
            return Response(response.text, status=response.status_code, mimetype='application/json')
        else:
            return Response(json.dumps({"success": "false"}), status=response.status_code, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"success": "false", "error": str(e)}), status=500, mimetype='application/json')


@app.route('/translate', methods=["POST"])
@cross_origin(supports_credentials=True)
def Translate():
    data = request.data.decode()
    data = json.loads(data)

    llm = data.get("model") if data.get("model") else "llama"
    message = data.get("message")
    language = data.get("lang")
    result = translate(text=message, language=language, llm_name=llm)
    return json.dumps(result)


@app.route('/calc_carbon', methods=["POST"])
@cross_origin(supports_credentials=True)
def calculate_carbon():
    try:
        data = request.data.decode()
        data = json.loads(data)

        distance = data.get("distance")
        electricity = data.get("electricity")
        meal = data.get("meal")
        waste = data.get("waste")
        country = data.get("country") if data.get("country") else "Nigeria"

        emission_data = calc_carbon(
            distance, electricity, meal, waste, country)
        emission_data.update({"success": "true"})

        return Response(json.dumps(emission_data),
                        status=201, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"success": "false", "emission": f"{e}"}),
                        status=404, mimetype='application/json')


if __name__ == "__main__":
    # Please do not set debug=True in production
    app.run(host="0.0.0.0", port=6000, debug=False)
