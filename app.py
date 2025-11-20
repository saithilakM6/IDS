from flask import Flask, render_template, request
import numpy as np
import pickle

app = Flask(__name__)

# Load pre-trained model, scaler, and label encoder
model = pickle.load(open("best_nids_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
label_encoder = pickle.load(open("label_encoder.pkl", "rb"))

# List of selected features that the model expects
selected_features = [
    "Flow Duration", "Protocol", "Tot Fwd Pkts", "Tot Bwd Pkts",
    "Fwd Pkt Len Max", "Bwd Pkt Len Max", "Flow Byts/s", "Flow Pkts/s",
    "Hour", "Minute", "Second"
]

# Predefined attack samples for demonstration purposes
attack_samples = {
    "Benign": [
        [112641719.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.026633116, 8.0, 31.0, 1.0],
        [112641466.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.026633176, 8.0, 33.0, 50.0],
        [112638623.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.026633848, 8.0, 36.0, 39.0]
    ],
    "FTP-BruteForce": [
        [19.0, 6.0, 1.0, 1.0, 0.0, 0.0, 0.0, 105263.1579, 10.0, 33.0, 26.0],
        [3.0, 6.0, 1.0, 1.0, 0.0, 0.0, 0.0, 666666.6667, 10.0, 33.0, 26.0],
        [3.0, 6.0, 1.0, 1.0, 0.0, 0.0, 0.0, 666666.6667, 10.0, 33.0, 26.0]
    ],
    "SSH-Bruteforce": [
        [555650.0, 6.0, 22.0, 22.0, 640.0, 976.0, 8265.994781, 79.18653829, 2.0, 1.0, 50.0],
        [560585.0, 6.0, 22.0, 22.0, 640.0, 976.0, 8221.768331, 78.48943514, 2.0, 1.0, 50.0],
        [530547.0, 6.0, 22.0, 20.0, 640.0, 976.0, 8657.102952, 79.16358023, 2.0, 1.0, 50.0]
    ],
    "DoS attacks-GoldenEye": [
        [6010454.0, 6.0, 4.0, 4.0, 285.0, 972.0, 209.135616, 1.331014263, 9.0, 27.0, 46.0],
        [6005042.0, 6.0, 4.0, 4.0, 422.0, 662.0, 180.5149739, 1.33221383, 9.0, 27.0, 46.0],
        [6003639.0, 6.0, 4.0, 4.0, 548.0, 972.0, 253.1797798, 1.332525157, 9.0, 27.0, 46.0]
    ],
    "DoS attacks-Slowloris": [
        [3863707.0, 6.0, 8.0, 2.0, 230.0, 0.0, 238.1132938, 2.588187976, 11.0, 0.0, 12.0],
        [1023719.0, 6.0, 4.0, 2.0, 230.0, 0.0, 224.6710279, 5.860983336, 11.0, 0.0, 15.0],
        [830593.0, 6.0, 6.0, 2.0, 230.0, 0.0, 1107.642371, 9.631672793, 11.0, 0.0, 16.0]
    ],
    "DoS attacks-Hulk": [
        [1793.0, 6.0, 3.0, 4.0, 364.0, 935.0, 724484.1049, 3904.071389, 1.0, 45.0, 27.0],
        [1720.0, 6.0, 3.0, 4.0, 300.0, 935.0, 718023.2558, 4069.767442, 1.0, 45.0, 27.0],
        [191.0, 6.0, 2.0, 0.0, 0.0, 0.0, 0.0, 10471.20419, 1.0, 45.0, 27.0]
    ],
    "DoS attacks-SlowHTTPTest": [
        [21.0, 6.0, 1.0, 1.0, 0.0, 0.0, 0.0, 95238.09524, 10.0, 12.0, 14.0],
        [3.0, 6.0, 1.0, 1.0, 0.0, 0.0, 0.0, 666666.6667, 10.0, 12.0, 14.0],
        [3.0, 6.0, 1.0, 1.0, 0.0, 0.0, 0.0, 666666.6667, 10.0, 12.0, 14.0]
    ]
}

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Handles the user input and displays the model prediction.
    - GET request displays the input form and attack options.
    - POST request processes the input, makes a prediction, and displays the result.
    """
    prediction = None
    selected_attack = None
    input_values = []

    if request.method == "POST":
        try:
            # Check if user selected a preset attack type
            if request.form.get("input_type") == "preset":
                selected_attack = request.form.get("attack_type")
                input_values = attack_samples[selected_attack][0]  # Use the first sample from the selected attack
            else:
                # User input values for each feature
                input_values = [float(request.form.get(feature, 0)) for feature in selected_features]

            # Scale the input values before making the prediction
            scaled_input = scaler.transform([input_values])

            # Make the prediction using the loaded model
            prediction = model.predict(scaled_input)[0]

            # Convert the numerical prediction back to the attack label
            prediction = label_encoder.inverse_transform([prediction])[0]

        except Exception as e:
            # If there is an error (e.g., missing input), show an error message
            prediction = f"Error: {str(e)}"

    return render_template("index.html",
                           features=selected_features,
                           prediction=prediction,
                           input_values=input_values,
                           attack_samples=attack_samples,
                           selected_attack=selected_attack)

if __name__ == "__main__":
    # Run the Flask application in debug mode for development
    app.run(debug=True)  # Set to False in production
