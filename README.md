# DFA Minimizer and Visualizer
This Python project allows you to:
- Read a Deterministic Finite Automaton (DFA) from an XML file
- Remove unreachable states
- Minimize the DFA using partitioning
- Visualize both the original and minimized DFA graphs interactively
- Export the minimized DFA as XML

## Features
- **Interactive visualization:** Switch between original and minimized DFA with a button
- **Graphical legend:** Understand node colors (start, final, other states)
- **XML input/output:** Easily integrate with other automata tools

## Requirements
- Python 3.x
- `networkx`
- `matplotlib`

Install requirements with:
pip install networkx matplotlib

## Usage
1. Place your DFA XML file as `input.xml` in the project directory.  
   The XML format should match the provided sample.
2. Run the main script:
    ```
    python project.py
    ```
3. Use the button in the plot window to switch between the original and minimized DFA.
4. The minimized DFA will be saved as `output.xml`.