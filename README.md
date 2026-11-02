⚽ Football IQ — Transfer Value Predictor
Football IQ is a football analytics project that estimates a player's market value using machine learning and historical Transfermarkt data. It also lets users compare two players and explore historical market-value patterns through an interactive Streamlit dashboard.

The project is built as a portfolio and learning project. Its predictions are model estimates, not official Transfermarkt valuations, transfer fees, or financial advice.
Project Features
1. Player Valuation
- Enter a player's profile, including age, height, preferred foot, position, and sub-position.
- Add performance statistics from the previous 365 days: goals, assists, minutes played, yellow cards, and red cards.
- Generate an estimated market value in euros.
- View a valuation summary with player details, a value tier, and a comparison with historical valuation records in the training dataset.
- Download an individual prediction as a CSV file.
- When the local player database is available and a player is matched, show the player's photo, club information, and historical market-value timeline.
2. Player Comparison
- Enter separate details and recent performance statistics for two players.
- Estimate each player's market value using the same trained model.
- View a head-to-head result, value difference, and side-by-side statistics.
- Compare goals, assists, minutes, goal contributions per 90 minutes, cards, age, and height.
- Download the comparison report as a CSV file.
3. Market Analytics
Explore historical valuation records with interactive filters for:
- Player position
- Valuation year
- Player age range
The analytics dashboard includes:
- Number of filtered records, average value, median value, and unique players
- Market-value distribution across value ranges
- Average market value by position
- Average market value by age group
- Average market-value trend over time
- A top-10 leaderboard based on each player's latest record within the selected filters
- CSV export of the filtered records
Machine Learning Approach
The application uses a Gradient Boosting regression model saved as models/best_model.pkl.

The model uses player profile and performance information, including:
Feature	Description
age	Player age
height_in_cm	Player height in centimetres
position	Broad playing position
sub_position	More specific playing position
foot	Preferred foot
goals_last_365_days	Goals in the previous 365 days
assists_last_365_days	Assists in the previous 365 days
minutes_last_365_days	Minutes played in the previous 365 days
yellow_cards_last_365_days	Yellow cards in the previous 365 days
red_cards_last_365_days	Red cards in the previous 365 days
valuation_year	Year associated with the valuation


The model was evaluated using a chronological holdout split, with earlier valuation records used for training and records from 2025 onward used for testing.
Reported Test Performance
Metric	Result
R² score	0.445
Mean Absolute Error (MAE)	Approximately €2.33 million


These results represent a baseline model. An R² score of 0.445 means the model explains part, but not all, of the variation in the held-out data. The MAE indicates that predictions can differ from recorded market values by several million euros. Individual estimates may be substantially inaccurate, especially for unusual players or circumstances.
Technology Stack
- Python — application and data-processing language
- Streamlit — interactive dashboard
- Pandas and NumPy — data manipulation and numerical operations
- scikit-learn — machine-learning pipeline
- Joblib — saving and loading the trained model
- DuckDB — local player-profile and valuation-history queries
- Altair — interactive charts
Repository Structure
football-transfer-value-predictor/
│
├── app.py                         # Streamlit dashboard
├── .gitignore                     # Files excluded from Git
│
├── dataset/
│   └── training_data.csv          # Prepared model-training dataset
│
├── models/
│   └── best_model.pkl             # Trained Gradient Boosting model
│
└── src/
    ├── build_dataset.py           # Builds the prepared dataset
    ├── train_model.py              # Trains and evaluates models
    ├── predict.py                  # Command-line prediction script
    ├── inspect_columns.py          # Dataset inspection utility
    ├── inspect_data.py             # Dataset inspection utility
    └── inspect_samples.py          # Dataset inspection utility
The raw DuckDB database is intentionally excluded from this GitHub repository because it is approximately 201 MB and exceeds GitHub's 100 MB per-file limit. The application expects it at:
dataset/transfermarkt-datasets.duckdb
Without that local database, the main prediction and market-analytics features can still use the included model and CSV dataset, but player profile matching, photos, club details, and individual historical valuation timelines will not be available.
Run the Project Locally
1. Clone the repository
git clone https://github.com/Deepakr10-si/football-transfer-value-predictor.git
cd football-transfer-value-predictor
2. Create and activate a virtual environment
Windows PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1
macOS / Linux:
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
python -m pip install streamlit pandas numpy scikit-learn joblib duckdb altair
4. Run the dashboard
python -m streamlit run app.py
Streamlit will print a local address in the terminal. Open that address in your browser to use the dashboard.
The repository already includes dataset/training_data.csv and models/best_model.pkl, so model training is not required just to launch the dashboard. The raw DuckDB file is optional for the profile and player-history features described above.

Data Source and Acknowledgment
The project uses historical football player and market-valuation data from the Transfermarkt datasets project by dcaribou. The prepared training_data.csv is included in this repository; the full raw DuckDB database is not.

Please consult the original dataset project for its data details, attribution requirements, and applicable terms before redistributing or reusing the underlying data.
Limitations and Considerations
- Market value is influenced by many factors that are not fully represented by the model, such as contract length, injuries, club finances, league conditions, reputation, and transfer-market demand.
- User-entered player details and statistics affect the estimate. Incorrect or unrealistic inputs can produce misleading results.
- Historical records are not a live transfer-market feed. The dashboard does not retrieve real-time valuations.
- The reported test metrics describe performance on a historical holdout dataset; they do not guarantee accuracy for a particular player or a future transfer window.
- Player-profile information available in the source database may not exactly match the profile at every historical valuation date.
Future Improvements
Potential next steps include improving model accuracy, testing additional regression algorithms, adding richer player and contextual features, and strengthening validation across different time periods and player groups.
Author
Created as a football analytics and machine-learning portfolio project.

Repository: Deepakr10-si / football-transfer-value-predictor
