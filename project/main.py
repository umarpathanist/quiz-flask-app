from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"   # needed for session

# Questions format:
# [question, option1, option2, option3, option4, correct_option_index]
questions = [
    ["Who is Shah Rukh Khan?", "WWE Wrestler", "Plumber", "Actor", "Astronaut", 3],
    ["What is the capital of France?", "Berlin", "Paris", "Rome", "London", 2],
    ["Which planet is known as the Red Planet?", "Earth", "Venus", "Mars", "Jupiter", 3],
    ["What is the largest mammal?", "Shark", "Blue Whale", "Elephant", "Giraffe", 2],
    ["Who wrote 'Romeo and Juliet'?", "William Shakespeare", "Jane Austen", "Charles Dickens", "Homer", 1],
    ["What is the square root of 64?", "8", "10", "6", "12", 1],
    ["Which country is known as the Land of the Rising Sun?", "India", "South Korea", "Japan", "China", 3],
    ["Who painted the Mona Lisa?", "Claude Monet", "Pablo Picasso", "Leonardo da Vinci", "Vincent van Gogh", 3],
    ["What is the fastest land animal?", "Horse", "Lion", "Cheetah", "Elephant", 3],
    ["Which ocean is the largest?", "Indian Ocean", "Pacific Ocean", "Atlantic Ocean", "Arctic Ocean", 2],
    ["What is the smallest country in the world?", "San Marino", "Vatican City", "Monaco", "Liechtenstein", 2]
]

prizes = [100000, 320000, 400000, 450000, 500000, 1000000, 2000000, 3000000, 4000000, 5000000, 6000000]

# Path to JSON file to store results
RESULTS_FILE = os.path.join(app.root_path, "results.json")


def load_results():
    """Load all saved results from results.json (returns list)."""
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_result(name, amount, status):
    """Append one student's result to results.json."""
    results = load_results()
    results.append({
        "name": name,
        "amount": amount,
        "status": status
    })
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


@app.route("/", methods=["GET", "POST"])
def home():
    # Page where student enters their name
    if request.method == "POST":
        student_name = request.form.get("name", "").strip()
        if not student_name:
            # reload with error
            return render_template("index.html", error="Please enter your name.")
        session["student_name"] = student_name
        # start quiz at first question
        return redirect(url_for("quiz"))
    return render_template("index.html")


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    # Ensure we have a student name
    if "student_name" not in session:
        return redirect(url_for("home"))

    student_name = session["student_name"]

    if request.method == "GET":
        # First question
        q_index = 0
        current_prize = 0

    else:
        # Coming from submitted form / POST
        q_index = int(request.form["q_index"])
        current_prize = int(request.form["current_prize"])
        selected = int(request.form["answer"])         # 1,2,3,4
        correct = questions[q_index][5]                # correct option index

        if selected == correct:
            # Correct answer → update prize and go to next question
            current_prize = prizes[q_index]
            q_index += 1

            # If no more questions → quiz finished
            if q_index >= len(questions):
                save_result(student_name, current_prize, "finished")
                return render_template(
                    "result.html",
                    name=student_name,
                    message="Congratulations! You finished the quiz! 🎉",
                    amount=current_prize
                )
        else:
            # Wrong answer → game over
            save_result(student_name, current_prize, "failed")
            return render_template(
                "result.html",
                name=student_name,
                message="Wrong answer! Game Over ❌",
                amount=current_prize
            )

    # Show current question
    question = questions[q_index]
    return render_template(
        "quiz.html",
        name=student_name,
        q_index=q_index,
        current_prize=current_prize,
        question_text=question[0],
        option_a=question[1],
        option_b=question[2],
        option_c=question[3],
        option_d=question[4]
    )


@app.route("/results")
def all_results():
    """Return all students' results in JSON format."""
    results = load_results()
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
