from flask import Flask, render_template, make_response, request, Markup, redirect
from openpyxl import Workbook
import pygal
from pygal.style import Style
import requests, pdfkit
import platform
import json
import math
import sendemail
from flask import Flask, session
from findorder import check_customer

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.secret_key = b'_6#y2M"F4D8z\n\xec]/'

#if (platform.system() == 'Darwin'):
config = pdfkit.configuration()
#else:
    #config = pdfkit.configuration(wkhtmltopdf='./bin/wkhtmltopdf')

activity_level = {
    "Sedentary":1.12,
    "Lightly Active":1.23,
    "Moderately Active":1.37,
    "Very Active":1.60,
}

activity_level_female = {
    "Sedentary":1.12,
    "Lightly Active":1.24,
    "Moderately Active":1.39,
    "Very Active":1.57,
}

health_goal = {
    "Maintain": 1.00,
    "Moderate Fat Loss": 0.90,
    "Extreme Fat Loss": 0.80,
    "Moderate Muscle Growth": 1.10,
    "Extreme Muscle Growth": 1.15,
}

health_goal_index = {
    "Maintain": 2,
    "Moderate Fat Loss": 1,
    "Extreme Fat Loss": 0,
    "Moderate Muscle Growth": 3,
    "Extreme Muscle Growth": 4,
}

@app.route("/")
def index():
    return render_template('index.html')
    
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if not ('verified' in session):
        return redirect("https://www.iamclovis.com/products/clovis-custom-nutrition-plan")
    content = json.loads(request.form['json'])
    #print(content)
    #return content
    answer = prepare_answer(content)
    #print(prepare_response(content))
    return render_template('dashboard.html', **answer)

@app.route("/new_request", methods=['GET', 'POST', 'DELETE', 'PUT'])
def new_request():
    session.clear()
    content = json.loads(request.form['json'])
    #if (check_customer(content["email"]) != True):
    #    print('failed')
    #    return 'failed'
    
    session['verified'] = 'yes' 
    print("session" + session['verified'])

    #print(content)
    pdfPlan = getPlanPDF(prepare_plan(content))
    pdfResponse = pdfkit.from_string(prepare_response(content), False, options=options, configuration=config)
    sendemail.scheduleEmail(content["email"], render_template("emailbody.html", name=content["firstname"]), pdfPlan, pdfResponse)
    return 'success'

@app.route("/clovis_store_install")
def clovis_store_install():
    return 'okay!'

def prepare_answer(user_data: list):
    measurements = user_data['measurements']
    #print(measurements)
    height = (float(measurements['feet']) * 12) + (float(measurements['inches']) * 1)
    weight = float(measurements['weight'])
    bmi = (703 * weight / (height * height))
    height = height * 2.54
    act_level = activity_level[user_data['activity_level']] if user_data['gender'] == 'male' else activity_level_female[user_data['activity_level']]


    multiplier_gastric = 0.9 if user_data['gastric_bypass'] == 'yes' else 1.0
    multiplier_pregnant = 1.15 if user_data['pregnant'] == 'yes' else 1.0
    multiplier_hundred_pounds = 0.9 if user_data['hundred_pounds'] == 'yes' else 1.0

    daily_calories = calTotalCalories(weight * 0.453592, 
        height, 
        int(measurements['age']), 
        float(act_level),
        float(health_goal[user_data['health_goal']]),
        (True if user_data['gender'] == 'male' else False),
        multiplier_gastric * multiplier_pregnant * multiplier_hundred_pounds
    )

    answer = {
        "daily_calories": daily_calories, 
        "daily_water": int(weight/2), 
        "my_bmi": "%.2f" % bmi, 
        "my_bmi_class": classifyBMI(bmi)
    }
    return answer

def prepare_response(user_data: list = None):
    return render_template("responsePDF.html", **user_data)

sel_calc = [
    [0.55, 0.35, 0.1],
    [0.57, 0.33, 0.1],
    [0.6, 0.3, 0.1],
    [0.55, 0.35, 0.1],
    [0.55, 0.35, 0.1],
]

sel_calc_pro = [
    [55, 35, 10],
    [57, 33, 10],
    [60, 30, 10],
    [55, 35, 10],
    [55, 35, 10],
]

def calFat(ttlCalories, health_goal):
    return int((ttlCalories * sel_calc[health_goal][0]) / 9)
def calProtein(ttlCalories, health_goal): 
    return int((ttlCalories * sel_calc[health_goal][1]) / 4)
def calNetCarbs(ttlCalories, health_goal):
    return int((ttlCalories * sel_calc[health_goal][2]) / 4)

def prepare_plan(user_data: list):
    measurements = user_data['measurements']
    #print(measurements)
    height = (float(measurements['feet']) * 12) + (float(measurements['inches']) * 1)
    weight = float(measurements['weight'])
    height = height * 2.54
    weight = weight * 0.453592
    act_level = activity_level[user_data['activity_level']] if user_data['gender'] == 'male' else activity_level_female[user_data['activity_level']]
    multiplier_gastric = 0.9 if user_data['gastric_bypass'] == 'yes' else 1.0
    multiplier_pregnant = 1.15 if user_data['pregnant'] == 'yes' else 1.0
    multiplier_hundred_pounds = 0.9 if user_data['hundred_pounds'] == 'yes' else 1.0

    daily_calories = calTotalCalories(weight, 
        height, 
        int(measurements['age']), 
        float(act_level),
        float(health_goal[user_data['health_goal']]),
        (True if user_data['gender'] == 'male' else False),
        multiplier_gastric * multiplier_pregnant * multiplier_hundred_pounds
    )
    daily_fat = calFat(daily_calories, health_goal_index[user_data['health_goal']])
    daily_protein = calProtein(daily_calories, health_goal_index[user_data['health_goal']])
    daily_net_carbs = calNetCarbs(daily_calories, health_goal_index[user_data['health_goal']])

    answer = {
        "age": measurements['age'],
        "height_inches": measurements['inches'],
        "height_feet": measurements['feet'],
        "weight": measurements['weight'],
        "activity_level": user_data['activity_level'],
        "health_goal": user_data['health_goal'],
        "daily_calories": daily_calories, 
        "daily_fat": daily_fat,
        "daily_protein": daily_protein, 
        "daily_net_carbs": daily_net_carbs,
        "daily_fat_percent": sel_calc_pro[health_goal_index[user_data['health_goal']]][0],
        "daily_protein_percent": sel_calc_pro[health_goal_index[user_data['health_goal']]][1], 
        "daily_net_carbs_percent": sel_calc_pro[health_goal_index[user_data['health_goal']]][2],
        "name": user_data['firstname'] + " " + user_data['lastname']
    }
    return answer

def calTotalCalories(weight, height, age, activityLevel, health_goal, isMale, multiplier):
    weight = round(weight)
    height = round(height)
    #print(weight, height, age, activityLevel, health_goal, isMale)
    baseCalVal = (10 * weight) + (height * 6.25) - (age * 5)
    if (isMale):
        baseCalVal += (1* 5)
        minCalVal = 1600
    else:
        baseCalVal -= (1* 161)
        minCalVal = 1300
        
    baseCalVal = math.floor(baseCalVal * activityLevel * health_goal * multiplier)
    baseCalVal = minCalVal if baseCalVal < minCalVal else baseCalVal

    return baseCalVal

def classifyBMI(bmi):
    if ( bmi < 18.5 ):
        return -1
    if ( bmi < 25 ):
        return 0
    if ( bmi < 30):
        return 1
    return 2

options = {
    'page-size': 'B5',
    'margin-top': '0.7in',
    'margin-right': '0.5in',
    'margin-bottom': '0.7in',
    'margin-left': '0.5in',
    'encoding': "UTF-8",
    'custom-header' : [
        ('Accept-Encoding', 'gzip')
    ],
    'no-outline': None
}

chart_style = Style(
    background='#D6D6D3',
    plot_background='#D6D6D3',
    colors=('#FF1068', '#797979', '#FFFFFF'),
    major_guide_stroke_dasharray=None,
    guide_stroke_dasharray=None,
    axis = '#CCC'
)

@app.route("/plan")
def showPlan():
    line_chart = pygal.Bar(width=350, height=293, style=chart_style, legend_at_bottom=True, legend_at_bottom_columns=3, show_y_guides=False, )
    line_chart.add('Fat', [{'value':67}])
    line_chart.add('Protein', [{'value':23}])
    line_chart.add('Net Carbs', [{'value':10}])
    plan = {
        "daily_fat" : "100",
        "age" : "24"
    }
    return render_template('plan.html', chart=line_chart.render_data_uri(), **plan)

@app.route("/pdf")
def makePDF():
    line_chart = pygal.Bar(width=350, height=293, style=chart_style, legend_at_bottom=True, legend_at_bottom_columns=3, show_y_guides=False, )
    line_chart.add('Fat', [{'value':67}])
    line_chart.add('Protein', [{'value':23}])
    line_chart.add('Net Carbs', [{'value':10}])
    pdf = pdfkit.from_string(render_template('plan.html', chart=line_chart.render_data_uri()), False, options=options, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
            'inline; filename=%s.pdf' % 'hello'
    return response


def getPlanPDF(plan):
    line_chart = pygal.Bar(width=350, height=293, style=chart_style, legend_at_bottom=True, legend_at_bottom_columns=3, show_y_guides=False, )
    line_chart.add('Fat', [{'value':plan['daily_fat_percent']}])
    line_chart.add('Protein', [{'value':plan['daily_protein_percent']}])
    line_chart.add('Net Carbs', [{'value':plan['daily_net_carbs_percent']}])
    return pdfkit.from_string(render_template('plan.html', chart=line_chart.render_data_uri(), **plan), False, options=options, configuration=config)

def generateUserResponse():
    return ''

if __name__ == "__main__":
    app.run(debug=True) 