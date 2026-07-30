import joblib
import numpy as np

# Load model
model = joblib.load("models/placement_model.pkl")


def predict_placement(
    cgpa,
    dsa_skill,
    communication,
    internships,
    projects,
    aptitude,
    resume_score,
    mock_interview
):

    # Convert input
    input_data = np.array([[
        cgpa,
        dsa_skill,
        communication,
        internships,
        projects,
        aptitude,
        resume_score,
        mock_interview
    ]])

    # Prediction
    prediction = model.predict(input_data)[0]

    # Probability
    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(input_data)[0][1] * 100
    else:
        probability = 50

    # Suggestions
    suggestions = []

    if cgpa < 7:
        suggestions.append("Improve CGPA")

    if dsa_skill < 7:
        suggestions.append("Practice DSA daily")

    if communication < 7:
        suggestions.append("Improve communication skills")

    if internships < 1:
        suggestions.append("Get at least 1 internship")

    if projects < 2:
        suggestions.append("Build more projects")

    if aptitude < 70:
        suggestions.append("Improve aptitude skills")

    if resume_score < 70:
        suggestions.append("Strengthen resume")

    if mock_interview < 7:
        suggestions.append("Practice mock interviews")

    return prediction, probability, suggestions