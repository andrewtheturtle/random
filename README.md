# Coffee Knowledge Graph

This project builds an interactive knowledge graph from a CSV of coffee brew experiments.
The goal is to understand how brewing conditions relate to sensory outcomes for different coffees.

This is a learning project and a sandbox for developing knowledge graph concepts (nodes, edges, properties, and queries) that can later be applied to more serious domains (e.g. biomedical or cancer ontologies). Also, this will be a fun tool for coffee newbs and nerds alike who want to explore the rabbit hole...

Code and project generated with the help of ChatGPT 5.2 (and Andrew's 20 bucks)

---

## What this graph represents

Each **brew session** is modeled as an event that connects:

- a specific coffee (bean / roast)
- brewing conditions (grind, dose, water, time, method)
- sensory outcomes (sweetness, acidity, body, flavor notes)

The graph makes it possible to ask questions like:
- *Which brewing conditions worked best for a given coffee?*
- *What grind and timing tend to reduce acidity for this roast?*
- *Which brews are most similar to a favorite cup?*

---

## Project structure

coffee-kg/
├── brews.csv # Input data (brew log)
├── build_coffee_kg.py # CSV → graph → HTML visualization
├── query_coffee_kg.py # Generates subgraphs given a query << in progress >>
├── coffee_kg.html # Generated interactive graph
├── requirements.txt
└── README.md

---

## The GRAPH

The graph is structured around a central `BrewSession` node, which represents a single brewing event. This event connects the inputs (what you used) to the outputs (what you tasted).

### Nodes

- **`BrewSession`**: The central event, linking all components of a single brew. Stores general properties like `brew_date`, `barista`, `dose_g`, etc.
- **`Roaster`**: The company that roasted the coffee, `roaster`.
- **`BeanLot`**: A specific batch of green coffee beans from a roaster, `coffee_name`.
- **`RoastBatch`**: A specific roast of a `BeanLot` (e.g. medium), stores `roast_level`.
- **`Grinder`**: The grinder used.
- **`Brewer`**: The specific brewing device used, identified by its brand and model (e.g., "Hario V60") via `brewer_brand` and `brewer_model`.
- **`SensoryEvaluation`**: The subjective tasting notes and ratings for a brew, stores 0-10 ratings for parameters such as sweetness (`sweetness_0_10`), acidity (`acidity_0_10`), or overall taste (`overall_0_10`).
- **`FlavorNote`**: A single flavor descriptor (e.g., "chocolate", "citrus").

### Edges

- `Roaster` → `PRODUCES` → `BeanLot`
- `BeanLot` → `ROASTED_AS` → `RoastBatch`: stores `roast_date`.
- `BrewSession` → `USES_ROAST` → `RoastBatch`
- `BrewSession` → `USES_GRINDER` → `Grinder`: stores `grind_setting`.
- `BrewSession` → `BREWED_WITH` → `Brewer`: stores the `brew_method` and all method-specific parameters like `bloom_time_sec` or `tamp_level`.
- `BrewSession` → `EVALUATED_AS` → `SensoryEvaluation`
- `SensoryEvaluation` → `HAS_NOTE` → `FlavorNote`: stores the `intensity` of each `FlavorNote`.

To view node or edge properties, simply hover your mouse over each entity in the graph.

---

## Inputs

The `brews.csv` file is where all the data piles in. Here are the columns:

### Required
- `brew_id`: A unique ID for the brew (e.g., "b1").
- `barista`: Who made the coffee.
- `brew_date`: Date of the brew.
- `roaster`: Name of the roaster.
- `coffee_name`: Name of the coffee.
- `roast_level`: e.g., "light", "medium", "dark".
- `brew_method`: The colloquial name for the method (e.g., "pourover", "espresso").
- `brewer_brand`: Brand of the brewing device (e.g., "Hario").
- `brewer_model`: Model of the brewing device (e.g., "V60").
- `dose_g`: Grams of coffee used.
- `total_brew_time_sec`: Total time of the brew in seconds.
- `notes_intensities`: Semi-colon separated key:value pairs for flavor notes (e.g., "chocolate:4;fruit:3").
- `sweetness_0_10`, `acidity_0_10`, `bitterness_0_10`, `body_0_10`, `overall_0_10`: Numerical ratings.

### Optional
- `roast_date`: Date the coffee was roasted.
- `grinder`: The grinder used.
- `grind_setting`: The setting on the grinder.
- `filter_material`: e.g., "paper", "metal".
- `notes_overall`: General free-text notes.

### Method-Specific Optional Parameters
These will appear on the `BREWED_WITH` edge.
- `total_water_g`: Total grams of water used.
- `total_coffee_g`: The final weight of the brewed coffee beverage.
- `water_temp_c`: Water temperature in Celsius.
- `off_boil_wait_sec`: Seconds waited after boiling before starting the brew.
- `bloom_water_g`: Grams of water used for the bloom.
- `bloom_time_sec`: Duration of the bloom in seconds.
- `preinfusion_time_sec`: Time for espresso pre-infusion.
- `tamp_level`: A subjective measure of tamping pressure, you choose any from ["light", "medium", "firm"]; [1-5] where 1 := coffee bed just flat, 3 := coffee bed compressed throughout, 5 := compressed as hard as you could; [lbs of force] if you have a device that measures the force used.
- `agitation_method`: For pourovers, "Rao spin", "stir with spoon", etc.
- `num_pours`: Number of separate pours after the bloom.
- `orientation`: For Aeropress, "standard", "inverted".
- `steep_time_sec`: For Aeropress or French Press, total time coffee steps prior to anything.
- `water_type`: lol
- Any optional parameters can simply be appended to the end of the columns of brews.csv.

---

## How to run

1.  **Clone the repository:**
    Get the project files on your local machine.
    ```bash
    git clone https://github.com/<your-username>/coffee-kg.git
    cd coffee-kg
    ```
    (Replace `<your-username>` with your actual GitHub username if you fork it, or use the original repo URL)

2.  **Set up a virtual environment:**
    It's highly recommended to use a virtual environment to keep dependencies isolated.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    (On Windows, the activate command is `.venv\Scripts\activate`)

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Add your data:**
    Edit `brews.csv` to log your coffee brews.
5.  **Build the graph:**
    ```bash
    python build_coffee_kg.py
    ```
6.  **Explore:**
    Open the generated `coffee_kg.html` in your browser.
