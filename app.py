from flask import Flask, render_template, request
import numpy as np
import pickle

# Load model (optional now)
model = pickle.load(open("heart_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

app = Flask(__name__)

# ==============================
# RULE-BASED HEART LOGIC
# ==============================
def get_heart_result(ca, cp, exang, thal):

    # Default
    prediction = 0
    stage = "Low Risk"

    # 🔴 CA RULE (Strongest)
    if ca == 0:
        return "No Heart Disease", "Low Risk"
    elif ca == 1:
        prediction = 1
        stage = "Low Risk"
    elif ca == 2:
        prediction = 1
        stage = "Medium Risk"
    elif ca == 3:
        return "Heart Disease Present", "High Risk"

    # 🔴 CP RULE
    if cp == 0:
        return "No Heart Disease", "Low Risk"
    elif cp == 1:
        stage = "Low Risk"
    elif cp == 2:
        stage = "Medium Risk"
    elif cp == 3:
        return "Heart Disease Present", "High Risk"

    # 🔴 EXANG RULE
    if exang == 0:
        return "No Heart Disease", "Low Risk"
    else:
        prediction = 1
        if stage == "Low Risk":
            stage = "Medium Risk"
        else:
            stage = "High Risk"

    # 🔴 THAL RULE
    if thal == 0:
        return "No Heart Disease", "Low Risk"
    elif thal == 1:
        prediction = 1
        if stage == "Low Risk":
            stage = "Medium Risk"
    elif thal == 2:
        return "Heart Disease Present", "High Risk"

    prediction_text = "Heart Disease Present" if prediction == 1 else "No Heart Disease"
    return prediction_text, stage


# ==============================
# HOME
# ==============================
@app.route('/')
def home():
    return render_template('index.html')


# ==============================
# PREDICT
# ==============================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Inputs
        age = float(request.form['age'])
        sex = int(request.form['sex'])
        cp = int(request.form['cp'])
        trestbps = float(request.form['trestbps'])
        chol = float(request.form['chol'])
        fbs = int(request.form['fbs'])
        restecg = int(request.form['restecg'])
        thalach = float(request.form['thalach'])
        exang = int(request.form['exang'])
        oldpeak = float(request.form['oldpeak'])
        slope = int(request.form['slope'])
        ca = int(request.form['ca'])
        thal = int(request.form['thal'])

        # (Optional ML prediction — not used for decision)
        features = [age, sex, cp, trestbps, chol, fbs,
                    restecg, thalach, exang, oldpeak,
                    slope, ca, thal]

        final_features = np.array(features).reshape(1, -1)
        scaled_features = scaler.transform(final_features)
        model_prediction = model.predict(scaled_features)[0]

        # ✅ RULE-BASED RESULT
        prediction_text, stage = get_heart_result(ca, cp, exang, thal)

        # Image selection
        if stage == "Low Risk":
            stage_image = "low_risk.png"
        elif stage == "Medium Risk":
            stage_image = "medium_risk.png"
        else:
            stage_image = "high_risk.png"

        return render_template(
            'result.html',
            prediction=prediction_text,
            stage=stage,
            stage_image=stage_image
        )

    except Exception as e:
        return f"Error: {e}"


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)