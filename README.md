# NP-Complexity Project

Study of NP-complete problems: **SAT**, **3-SAT**, and **Subset Sum**.

## Project Structure

```
complexity-project/
├── src/
│   ├── solvers/           # Problem solvers (TODO: implement)
│   │   ├── sat_solver.py
│   │   ├── three_sat_solver.py
│   │   └── subset_sum_solver.py
│   ├── verifiers/         # Solution verifiers (TODO: implement)
│   ├── reductions/        # Polynomial reductions (TODO: implement)
│   ├── benchmarks/        # Generators and analysis
│   ├── utils/             # Utilities (READY)
│   └── cli.py             # Command-line interface
├── tests/                 # Test suite
├── data/                  # Sample instances
├── results/               # Output directory
│   ├── logs/
│   └── plots/
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
├── Dockerfile             # Docker setup
└── main.py                # Entry point
```

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Or Use Docker

```bash
docker build -t np-complexity .
docker run -v $(pwd)/results:/app/results np-complexity
```

### 3. Run

```bash
# Main entry point
python main.py

# CLI commands
python -m src.cli solve sat --file data/sample_sat.cnf
python -m src.cli solve subset-sum --numbers "3,7,1,8,4" --target 12
python -m src.cli benchmark run --problem sat

# Run tests
pytest tests/ -v
```

