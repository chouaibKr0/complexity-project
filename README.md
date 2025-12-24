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

## What YOU Need to Implement (TODO)

### Solvers (`src/solvers/`)

1. **SAT Solver** - `sat_solver.py`
   - `_brute_force()`: Enumerate all 2^n assignments
   - `_backtrack()`: Backtracking with pruning
   - `_dpll()`: DPLL algorithm with unit propagation

2. **3-SAT Solver** - `three_sat_solver.py`
   - Same algorithms, specialized for 3-literal clauses

3. **Subset Sum Solver** - `subset_sum_solver.py`
   - `_brute_force()`: Try all 2^n subsets
   - `_backtrack()`: Backtracking with pruning
   - `_dynamic_programming()`: O(n*T) DP approach

### Verifiers (`src/verifiers/`)

- `verify_sat_solution()`: Check if assignment satisfies CNF
- `verify_3sat_solution()`: Same for 3-SAT
- `verify_subset_sum_solution()`: Check if subset sums to target

### Reductions (`src/reductions/`)

- `reduce_sat_to_3sat()`: Polynomial reduction SAT → 3-SAT
- `reduce_3sat_to_subset_sum()`: Polynomial reduction 3-SAT → Subset Sum

### Benchmarks (`src/benchmarks/`)

- `generators.py`: Random instance generation
- `runner.py`: Benchmark execution
- `analysis.py`: Results analysis and plotting

## Utilities (Already Implemented)

- **Configuration**: `src/utils/config.py` - YAML + env config
- **Logging**: `src/utils/logging.py` - Structured logging
- **Timing**: `src/utils/timer.py` - Performance monitoring
- **Progress**: `src/utils/progress.py` - Progress bars
- **Serialization**: `src/utils/serialization.py` - Results saving
- **Validation**: `src/utils/validation.py` - Input validation
- **Errors**: `src/utils/errors.py` - Error handling
- **Parsers**: `src/utils/parsers.py` - DIMACS CNF parsing
- **Experiment Tracking**: `src/utils/experiment.py`

## File Formats

### DIMACS CNF (SAT/3-SAT)

```
c Comment line
p cnf <num_vars> <num_clauses>
1 -2 3 0    <- clause (x1 OR NOT x2 OR x3)
-1 2 0      <- clause (NOT x1 OR x2)
```

### Subset Sum

```
n <num_elements>
t <target>
<number1>
<number2>
...
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_sat_solver.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```
