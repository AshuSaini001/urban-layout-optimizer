# 🏗️ Generative Urban Layout Optimizer

A Python-based generative design tool that uses **Simulated Annealing** to automatically generate valid, optimized architectural site plans. 

The application visualizes the layout process in real-time using **Streamlit**, ensuring that buildings adhere to strict zoning constraints such as setbacks, neighbor proximity, and plaza preservation.

## 🚀 Live Demo
*(If you deploy it to Streamlit Cloud, paste the link here. e.g., https://my-urban-layout.streamlit.app)*

## 🧩 Key Features

*   **Constraint Satisfaction:** Automatically enforces complex rules:
    *   **Site Setbacks:** Buildings cannot touch the site boundary.
    *   **Plaza Preservation:** A central green zone is kept clear of construction.
    *   **Proximity Rules:** Buildings must maintain a minimum distance from each other.
    *   **Neighbor Logic:** "Type A" buildings require a "Type B" building within a specific radius.
*   **Simulated Annealing:** Uses a probabilistic technique for approximating the global optimum of a given function (minimizing rule violations while maximizing built area).
*   **Interactive UI:** Built with Streamlit to allow users to adjust optimization steps and generate multiple layout iterations instantly.
*   **Visual auditing:** Violations are highlighted in red (collisions, missing neighbors) for easy debugging.

## 🛠️ Tech Stack

*   **Python 3.x**
*   **Streamlit** (Web Interface)
*   **Matplotlib** (Visualization & Geometry plotting)
*   **NumPy / Math** (Calculations)

## 📦 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/urban-layout-optimizer.git
    cd urban-layout-optimizer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Create a requirements.txt file with `streamlit` and `matplotlib` in it)*

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
    *If that fails on Windows, try:*
    ```bash
    python -m streamlit run app.py
    ```

## 🧠 How It Works

1.  **Initialization:** The script places 10 random buildings on the site.
2.  **Mutation:** In every step, the algorithm randomly performs an action:
    *   Moves a building.
    *   Rotates a building.
    *   Adds or removes a building.
3.  **Evaluation (Cost Function):** The layout is scored based on:
    *   **Penalties (+):** Collisions, overlapping the plaza, or missing a neighbor.
    *   **Rewards (-):** Higher total floor area lowers the "energy" score.
4.  **Annealing:** Early in the process, the algorithm accepts "bad" moves to escape local minima. As the "temperature" cools, it only accepts moves that improve the layout.

## 🔮 Future Improvements

*   Add more building shapes (L-shapes, U-shapes).
*   Implement road network generation.
*   3D visualization using PyDeck or Plotly.
