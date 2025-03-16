# Voyager++

Voyager++ is an advanced tool for collecting and analyzing datasets of Ansible roles from Ansible Galaxy. It builds on the original Voyager tool by Ruben Opdebeeck, addressing obsolescence and dependencies while introducing a datamining stage for deeper insights into role version histories. Designed for research projects, such as For-CoaLa, Voyager++ enables flexible data collection, repository analysis, and structural evolution tracking.

## Features

- **Data Collection**: Scrapes Ansible Galaxy for role information.
- **Metadata Extraction**: Extracts structured metadata from collected roles.
- **Repository Cloning**: Fetches role repositories for deeper analysis.
- **Structural Analysis**: Tracks changes in role configurations over versions.
- **Datamining**: Allows users to run custom analysis scripts.

## System Requirements

- **OS**: Linux/macOS/Windows
- **Python**: 3.8+
- **Dependencies**: Managed via [Poetry](https://python-poetry.org/)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/NotArobase/Voyager.git
   cd Voyager++
   ```
2. Install dependencies:
   ```sh
   poetry install
   ```
3. Verify installation:
   ```sh
   poetry run -- python main.py --help
   ```
   Check the help text.

## Usage

### API

For use of the Voyager API, please refer to the readme file found in folder voyager_api.

### Basic Operations

Assumig poetry shell is spawned:

- **Scrape data from Ansible Galaxy**: Collects role information from Ansible Galaxy. Limit the number of collected roles using the option --max-roles INT.
  ```sh
  python main.py --progress --report --dataset my_data galaxy-scrape
  ```
- **Custom scrape with user-defined schema**: Collects role data while filtering unnecessary attributes using a custom schema.
  ```sh
  python main.py --progress --report --dataset my_data custom-scrape --schema path/to/my_schema.json
  ```
- **Extract role metadata**: Extracts structured metadata (e.g., role dependencies, GitHub repositories) from the scraped dataset.
  ```sh
  python main.py --dataset my_data extract-role-metadata
  ```
- **Clone repositories**: Downloads the Git repositories for roles found in metadata.
  ```sh
  python main.py --dataset my_data clone
  ```
- **Extract Git metadata**: Retrieves commit history, branches, and tags from cloned repositories.
  ```sh
  python main.py --dataset my_data extract-git-metadata
  ```
- **Extract structural models** (for semantic version tags): Analyzes the structure of Ansible roles at each versioned release.
  ```sh
  python main.py --dataset my_data extract-structural-models
  ```
- **Extract structural models** (for each commit instead of versions): Captures structural changes in roles at every commit.
  ```sh
  python main.py --dataset my_data extract-structural-models --commits
  ```
- **Run a datamining script**: Executes an external analysis script on the dataset.

  ```sh
  python main.py --dataset my_data datamine-stage --path path/to/my_script.py
  ```

  With every operation:
  Use the --report option to print the details of the process in the console. Use the --delete option to remove the folder of the current stage if it exists already.

## Customization

Voyager++ supports easy customization for specific research needs:

- **Custom Scraping**: Define a JSON schema to filter collected data.
- **Datamining**: Plug in external analysis scripts. Said script must contain two specific functions (see user documentation).
  The tool comes with a number of "default" relevant datamining scripts, stored in Voyager/pipeline/datamine
- **Pipeline Extension**: Modify or add processing stages.

## Troubleshooting

- **Poetry not found?** Ensure it's installed and added to `PATH`. If you have too many problems using Poetry; there exists a poetry-free version of Voyager found at: https://github.com/SarahBlevin/MyVoyager.git where you can download the dependencies in a venv via bash script.
- **Errors in metadata extraction?** Check dataset integrity and rerun the scraping step.

## Future Enhancements

- Frontend integration for better visualization.
- Containerization

For detailed documentation, visit the full [Voyager++ repository](https://github.com/NotArobase/Voyager.git) or read the full user documentation.
## Requirements
- Python >= 3.8
- [Poetry](https://python-poetry.org/docs/#installation)

## Installing
- `cd /path/to/voyager`
- `poetry install`

## Running
- `poetry run -- python main.py`
- Check the help text.

### Examples
Assuming `poetry shell` is spawned.

- `python main.py --progress --report --dataset my_data galaxy-scrape`
  Create a new dataset named `my_data` and start harvesting data from the Ansible Galaxy API.
  Show progress while searching for roles, include a report on the gathered roles.
- `python main.py --dataset my_data extract-role-metadata`
  Extract the harvested API pages into the Galaxy metadata schema.
- `python main.py --report --dataset my_data clone`
  Clone repositories discovered in the harvested Galaxy metadata.
- `python main.py --dataset my_data extract-git-metadata`
  Extract git repository metadata, i.e. commits and tags, from the git repositories.
- `python main.py --dataset my_data extract-structural-models`
  Extract structural models for each git tag that matches the semantic versioning format.
- `python main.py --dataset my_data extract-structural-models --commits`
  Alternative to the previous command, but extract models for each commit rather than each version.
- `python main.py --dataset my_data extract-structural-diffs`
  Distil changes between the structural model versions.

Hint: Commands can be mixed and omitted quite flexibly. For example, executing all phases of the pipeline could be executed in one command as such:
- `python main.py --report --progress --dataset my_data extract-structural-diffs`



# Datamine Analysis Commands

This document explains the execution commands for each analysis script (`test1.py` through `test6.py`), their logic, and how to use them.

---

## Usage

Each analysis script can be executed with custom options using the following command-line syntax:

```bash
python main.py --dataset <dataset_name> datamine-stage --options '{"option_name": value}' --path "data/<script_name>.py"
```

Replace `<dataset_name>` and `<script_name>` with your specific dataset and script names.

### Example:

```bash
python main.py --dataset my_data datamine-stage --options '{"num_modules":2}' --path "data/test1.py"
```

---

## Analysis Scripts

### **Test1 (`test1.py`)**
- **Logic:** Parses YAML files to identify and count how frequently each module is used across different roles.
- **Options:**
  - `num_modules` *(default: 8)* — Number of top modules to display.
- **Example:**
```bash
python main.py --dataset my_data datamine-stage --options '{"num_modules":8}' --path "data/test1.py"
```

---

### **Test2 (`test2.py`)**
- **Logic:** Creates a correlation matrix to visualize the relationships between modules based on their usage across roles.
- **Options:**
  - `num_modules` *(default: 20)* — Number of top modules included in the correlation analysis.
- **Example:**
```bash
python main.py --dataset my_data datamine-stage --options '{"num_modules":20}' --path "data/test2.py"
```

---

### **Test3 (`test3.py`)**
- **Logic:** Computes a transition matrix indicating the likelihood of transitioning from one module to another within the roles' workflows, normalized to show proportional transitions.
- **Options:**
  - `num_modules` *(default: 20)* — Number of top modules to analyze in the transitions.
- **Example:**
```bash
python main.py --dataset my_data datamine-stage --options '{"num_modules":20}' --path "data/test3.py"
```

---

### **Test4 (`test4.py`)**
- **Logic:** Identifies the most common arguments passed to modules and visualizes their frequency across all roles.
- **Options:**
  - `num_arguments` *(default: 25)* — Number of most common arguments to visualize.
- **Example:**
```bash
python main.py --dataset my_data datamine-stage --options '{"num_arguments":25}' --path "data/test4.py"
```

---

### **Test5 (`test5.py`)**
- **Logic:** Calculates how frequently each module uses loops (repeated tasks) and presents this information as a percentage of total module usage.
- **Options:**
  - `num_modules` *(default: 20)* — Number of top modules to visualize based on loop usage.
- **Example:**
```bash
python main.py --dataset my_data datamine-stage --options '{"num_modules":20}' --path "data/test5.py"
```

---

### **Test6 (`test6.py`)**
- **Logic:** Analyzes module usage data to identify strong correlations between modules, highlighting pairs frequently used together.
- **Options:** *(None required by default)*
- **Example:**
```bash
python main.py --dataset my_data datamine-stage --path "data/test6.py"
```

---

### **Test 7: Common Arguments per Module Analysis**

- **Logic:**  
Identifies the most commonly used arguments across Ansible modules and analyzes correlations between these arguments to understand their co-occurrence.

- **Options:**
  - `num_arguments` *(optional, default=20)*: Defines the number of top arguments to analyze.

- **Example:**
```bash
python main.py --dataset my_data datamine-stage --options '{"num_arguments":20}' --path "datamine/test7.py"
```

---


### **Test 8: 'When' Condition Usage Analysis**

**Logic:**  
Analyzes Ansible most used modules to measure how frequently they use conditional statements (when).

- **Options:**
  - `num_arguments` *(optional, default=25)*: Defines the number of top arguments to analyze.

- **Example:**
```bash
python main.py --dataset my_data datamine-stage --options '{"num_arguments":20}' --path "datamine/test8.py"
```
---


---

### **Test9: Module Condition Analysis (`when` Conditions)**

This script analyzes Ansible role YAML files to extract `when` conditions applied to modules. It identifies the most used conditions, their relationships (AND/OR logic), and generates visualizations.
- **Logic:**

- Extracts all `when` conditions associated with each module.
- Normalizes conditions and splits them into AND/OR conditions.
- Generates statistics on condition usage frequency.
- Creates a CSV and JSON file listing conditions per module.
- Produces bar charts visualizing the most used conditions and the modules with the highest number of conditions.

- **Options**
- `num_modules` *(default: 25)*: Number of modules to include in the analysis.

## Example Execution
```bash
python main.py --dataset my_data datamine-stage --options '{"num_modules":25}' --path "datamine/test_conditions.py"

## Output Structure

Executing the scripts will produce organized output files in the following structure:

```
output_directory/
├── my_data/
│   ├── test1/
|   |   |__most_used_modules.png
│   ├── test2/
│   │   ├── modules_par_role.csv
│   │   └── correlation_matrix.png
│   ├── test3/
│   │   ├── module_transition_matrix.csv
│   │   └── module_transition_matrix.png
│   ├── test4/
│   │   ├── common_args_per_module.csv
│   │   └── top_X_arguments.png
│   ├── test5/
│   │   ├── loop_usage_percentage_per_module.csv
│   │   └── top_X_loop_usage.png
│   ├── test6/
│   │   ├── strong_correlations.csv
│   │   └── strong_correlation_matrix.png
│   ├── test7/
│   │   ├── argument_correlation_matrix.csv
│   │   └── argument_correlation_matrix.png
│   ├── test8/
│   │   ├── when_usage_percentage.csv
│   │   └── when_usage_percentage.png
│   ├── test9/
│   │   ├── module_conditions.json
│   │   ├── module_conditions.csv
│   │   ├── top_conditions_usage.png
│   │   └── top_modules_conditioned.png

```
