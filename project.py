import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Patch

# Read DFA from XML file
def read_dfa_from_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    alphabets = [alphabet.attrib['letter'] for alphabet in root.find('Alphabets')]
    states = [state.attrib['name'] for state in root.find('States').findall('state')]
    initial_state = root.find('States').find('initialState').attrib['name']
    final_states = [final.attrib['name'] for final in root.find('States').find('FinalStates').findall('finalState')]
    transitions = []
    for transition in root.find('Transitions').findall('transition'):
        transitions.append({
            'source': transition.attrib['source'],
            'destination': transition.attrib['destination'],
            'label': transition.attrib['label']
        })

    return alphabets, states, initial_state, final_states, transitions

# Remove unreachable states
def remove_unreachable_states(states, initial_state, transitions):
    reachable_states = set()
    stack = [initial_state]

    while stack:
        state = stack.pop()
        if state not in reachable_states:
            reachable_states.add(state)
            for trans in transitions:
                if trans['source'] == state and trans['destination'] not in reachable_states:
                    stack.append(trans['destination'])

    new_transitions = [t for t in transitions if t['source'] in reachable_states and t['destination'] in reachable_states]
    return list(reachable_states), new_transitions

# Merge equivalent states
def minimize_dfa(states, final_states, transitions):
    non_final_states = set(states) - set(final_states)
    partition = [set(final_states), non_final_states]

    def get_block(state):
        for i, block in enumerate(partition):
            if state in block:
                return i
        return -1

    while True:
        new_partition = []
        for block in partition:
            split_blocks = {}
            for state in block:
                key = tuple((trans['label'], get_block(trans['destination'])) for trans in transitions if trans['source'] == state)
                if key not in split_blocks:
                    split_blocks[key] = set()
                split_blocks[key].add(state)
            new_partition.extend(split_blocks.values())

        if new_partition == partition:
            break
        partition = new_partition

    new_states = ['q' + ''.join(sorted(block)) for block in partition]
    state_map = {state: new_state for block, new_state in zip(partition, new_states) for state in block}

    new_transitions = []
    for trans in transitions:
        source = state_map[trans['source']]
        destination = state_map[trans['destination']]
        label = trans['label']
        if {'source': source, 'destination': destination, 'label': label} not in new_transitions:
            new_transitions.append({'source': source, 'destination': destination, 'label': label})

    new_initial_state = state_map[initial_state]
    new_final_states = {state_map[state] for state in final_states}

    return new_states, new_initial_state, list(new_final_states), new_transitions

# Draw DFA graph
def draw_dfa(ax_graph, ax_legend, states, transitions, start_state, final_states, title="DFA"):
    G = nx.DiGraph()

    # Add nodes and edges
    G.add_nodes_from(states)
    for transition in transitions:
        G.add_edge(transition['source'], transition['destination'], label=transition['label'])

    pos = nx.spring_layout(G)

    ax_graph.clear()
    
    # Color nodes
    nx.draw_networkx_nodes(G, pos, ax=ax_graph, nodelist=states, node_color='lightblue', node_size=500)
    nx.draw_networkx_nodes(G, pos, ax=ax_graph, nodelist=[start_state], node_color='lightgreen', node_size=500)
    nx.draw_networkx_nodes(G, pos, ax=ax_graph, nodelist=final_states, node_color='lightpink', node_size=500)

    # Draw edges and labels
    nx.draw_networkx_edges(G, pos, ax=ax_graph, arrows=True, node_size=500, width=1.5, arrowsize=20)
    nx.draw_networkx_labels(G, pos, ax=ax_graph, font_size=10)

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, ax=ax_graph, edge_labels=edge_labels, font_size=10)

    ax_graph.set_title(title)
    ax_graph.axis('off')

    # Clear legend axis and add legend elements
    ax_legend.clear()
    
    legend_elements = [
        Patch(facecolor='lightgreen', edgecolor='black', label='Start State'),
        Patch(facecolor='lightpink', edgecolor='black', label='Final State'),
        Patch(facecolor='lightblue', edgecolor='black', label='Other States')
    ]
    
    ax_legend.legend(handles=legend_elements)
    ax_legend.axis('off')

# Write DFA to XML file
def write_dfa_to_xml(file_path, alphabets, states, initial_state, final_states, transitions):
    root = ET.Element("Automata", type="DFA")

    alphabet_elem = ET.SubElement(root, "Alphabets", numberOfAlphabets=str(len(alphabets)))
    for letter in alphabets:
        ET.SubElement(alphabet_elem, "alphabet", letter=letter)

    states_elem = ET.SubElement(root, "States", numberOfStates=str(len(states)))
    for state in states:
        ET.SubElement(states_elem, "state", name=state)

    ET.SubElement(root, "initialState", name=initial_state)

    final_elem = ET.SubElement(root, "FinalStates", numberOfFinalStates=str(len(final_states)))
    for state in final_states:
        ET.SubElement(final_elem, "finalState", name=state)

    trans_elem = ET.SubElement(root, "Transitions", numberOfTrans=str(len(transitions)))
    for trans in transitions:
        ET.SubElement(trans_elem, "transition", source=trans['source'], destination=trans['destination'], label=trans['label'])

    tree = ET.ElementTree(root)
    tree.write(file_path)

# Main program execution
input_file = "input.xml"
output_file = "output.xml"

alphabets, states, initial_state, final_states, transitions = read_dfa_from_xml(input_file)

# Reduce DFA
states_reachable, transitions_reachable = remove_unreachable_states(states, initial_state, transitions)
states_minimized, initial_minimized_state, final_minimized_states, minimized_transitions = minimize_dfa(
    states_reachable,
    final_states,
    transitions_reachable
)

# Save minimized DFA to XML file
write_dfa_to_xml(output_file,
                 alphabets,
                 states_minimized,
                 initial_minimized_state,
                 final_minimized_states,
                 minimized_transitions)

print(f"Minimized DFA saved to {output_file}")

# Create figure and axes for the graph and legend
fig = plt.figure(figsize=(12, 8))
ax_graph = fig.add_axes([0.05, 0.1, 0.7, 0.8])  # Axis for graph (left side)
ax_legend = fig.add_axes([0.8, 0.4, 0.15, 0.2])  # Axis for legend (right side)

# Variable to track which DFA is currently displayed
showing_original = True

# Function to switch between original and minimized DFA
def switch_dfa(event):
    global showing_original
    showing_original = not showing_original
    
    if showing_original:
        draw_dfa(ax_graph,
                 ax_legend,
                 states,
                 transitions,
                 initial_state,
                 final_states,
                 title="Original DFA")
        button.label.set_text("Show Minimized DFA")
        
    else:
        draw_dfa(ax_graph,
                 ax_legend,
                 states_minimized,
                 minimized_transitions,
                 initial_minimized_state,
                 final_minimized_states,
                 title="Minimized DFA")
        button.label.set_text("Show Original DFA")
    
    fig.canvas.draw_idle()

# Create a button to switch between DFAs
button_ax = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(button_ax, 'Show Minimized DFA')
button.on_clicked(switch_dfa)

# Initial display of the original DFA
draw_dfa(ax_graph,
         ax_legend,
         states,
         transitions,
         initial_state,
         final_states,
         title="Original DFA")

plt.show()
