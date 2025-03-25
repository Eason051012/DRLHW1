from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

GRID_SIZE = 5
start = None
end = None
obstacles = set()

@app.route("/")
def index():
    return render_template("index.html", grid_size=GRID_SIZE)

@app.route("/update_grid", methods=["POST"])
def update_grid():
    global start, end, obstacles, GRID_SIZE

    data = request.json
    row, col, cell_type = data["row"], data["col"], data["type"]
    GRID_SIZE = int(data.get("size", GRID_SIZE))

    if cell_type == "start":
        start = (row, col)
    elif cell_type == "end":
        end = (row, col)
    elif cell_type == "obstacle":
        if (row, col) in obstacles:
            obstacles.remove((row, col))
        elif len(obstacles) < GRID_SIZE - 2:
            obstacles.add((row, col))

    return jsonify({"start": start, "end": end, "obstacles": list(obstacles)})

@app.route("/generate_policy_and_value", methods=["POST"])
def generate_policy_and_value():
    global GRID_SIZE

    data = request.get_json()
    GRID_SIZE = int(data.get("size", GRID_SIZE))

    gamma = 0.9
    reward = -1
    max_iterations = 50

    directions = ['↑', '↓', '←', '→']
    actions = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1)}

    # 初始化 policy：非障礙與非終點才設定策略
    policy = [[
        random.choice(directions) if (i, j) not in obstacles and (i, j) != end else ''
        for j in range(GRID_SIZE)
    ] for i in range(GRID_SIZE)]

    # 初始化 value：全部為 0
    value = [[0.0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # 終點設為 0 是策略評估的終止點
    if end:
        value[end[0]][end[1]] = 0.0

    # 策略評估
    for _ in range(max_iterations):
        new_value = [[0.0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if (i, j) in obstacles or (i, j) == end:
                    continue
                a = policy[i][j]
                if a == '':
                    continue
                di, dj = actions[a]
                ni, nj = i + di, j + dj
                if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and (ni, nj) not in obstacles:
                    new_value[i][j] = reward + gamma * value[ni][nj]
                else:
                    new_value[i][j] = reward + gamma * value[i][j]
        value = new_value

    return jsonify({
        "policy": policy,
        "value": value,
        "start": start,
        "end": end,
        "obstacles": list(obstacles),
        "size": GRID_SIZE
    })

if __name__ == "__main__":
    app.run(debug=True)
