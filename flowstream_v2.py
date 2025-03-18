import streamlit as st
from graphviz import Digraph
import json
import os
from io import StringIO

# --- Helper Functions ---

def draw_node(dot, node_name, node_type):
    """Draws a node with the appropriate shape."""
    shape_map = {
        "Process": "ellipse",
        "External Entity": "square",
        "Data Store": "cylinder",
        "Event": "circle",
        "Gateway": "diamond",
        "Component": "component",
        "Node": "box3d",
        "Class": "record",
        "Entity": "box",
        "Attribute": "oval",  # Added shape for Attribute
        "Decision": "diamond", # Added shape for Decision
        "Start/End": "ellipse", # Added shape for Start/End
    }
    shape = shape_map.get(node_type, "ellipse")
    dot.node(node_name, node_name, shape=shape)


def generate_diagram(nodes, connections, output_format="png", fontsize="12", layout="dot", diagram_type="dfd", label_position='c'):
    """Generates a diagram with customizable options."""
    dot = Digraph(comment=f'{diagram_type.upper()} Diagram', format=output_format,
                    engine=layout,
                    node_attr={'fontsize': str(fontsize), 'fontname': 'Arial'},
                    edge_attr={'fontsize': str(fontsize), 'fontname': 'Arial', 'color': '#00000080', 'bgcolor': '#ffffffcc', 'labeldistance': '1.5', 'labelposition': label_position}) # Added labeldistance and labelposition

    active_nodes = set()
    for connection in connections:
        active_nodes.add(connection["source"])
        active_nodes.add(connection["destination"])

    for node in nodes:
        if node["name"] in active_nodes or not connections: # Ignore nodes not in any connection (unless no connections exist)
            draw_node(dot, node["name"], node["type"])

    for connection in connections:
        dot.edge(connection["source"], connection["destination"], label=connection["label"], bgcolor='#ffffffcc', arrowhead='vee',
                 arrowtail='vee' if connection.get("bidirectional", False) else None,
                 dir='both' if connection.get("bidirectional", False) else 'forward', minlen='2')
        if connection.get("bidirectional", False):
            dot.edge(connection["destination"], connection["source"], label="", style='invis', minlen='2') # Invisible edge for spacing

    return dot

def save_diagram(dot, filename, output_format):
    """Saves the generated diagram to a file."""
    try:
        if output_format == "dot":
            with open(filename + ".dot", "w") as f:
                f.write(dot.source)
            return filename + ".dot"
        else:
            filepath = dot.render(filename, format=output_format, view=False, directory=".")
            return filepath
    except Exception as e:
        st.error(f"Error saving diagram: {e}")
        return None

def display_diagram(dot, output_format):
    """Displays the generated diagram in the Streamlit app."""
    try:
        if output_format == "dot":
            st.text_area("DOT Source", dot.source, height=300)
        else:
            st.graphviz_chart(dot, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying diagram: {e}")

def load_data(diagram_type, filename=""):
    """Loads previously saved nodes and connections from a JSON file."""
    if not filename:
        st.warning("Please select a file to load.")
        return None, None
    filepath = f"{diagram_type}_data_{filename}.json"
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
                return data.get("nodes", []), data.get("connections", [])
            except json.JSONDecodeError:
                st.warning(f"Could not decode JSON from {filepath}. Starting with empty data.")
                return [], []
    else:
        st.warning(f"File '{filepath}' not found.")
        return [], []

def save_data(diagram_type, nodes, connections, filename=""):
    """Saves the current nodes and connections to a JSON file with a given filename."""
    if not filename:
        st.warning("Please enter a filename to save.")
        return
    filepath = f"{diagram_type}_data_{filename}.json"
    data = {"nodes": nodes, "connections": connections}
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    st.success(f"Data saved to {filepath}")

def get_available_data_files(diagram_type):
    """Gets a list of available data files for the given diagram type."""
    files = []
    for filename in os.listdir("."):
        if filename.startswith(f"{diagram_type}_data_") and filename.endswith(".json"):
            name = filename[len(f"{diagram_type}_data_"):-len(".json")]
            files.append(name)
    return files

# --- Streamlit App ---

def main():
    st.title("Design Documentation Tool")

    pages = {
        "Introduction": introduction_page,
        "Data Flow Diagrams (DFDs)": dfd_page,
        "Business Process Model and Notation (BPMN)": bpmn_page,
        "UML Diagrams": uml_page,
        "Entity-Relationship Diagrams (ERDs)": erd_page,
        "Process Flow Diagrams and Decision Flowcharts": process_flow_page,
    }

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Select Document Type", list(pages.keys()))
    pages[page]()

# --- Page Functions ---

def introduction_page():
    st.header("Introduction: Design Documentation Tool")
    st.write("""
    Welcome to the Design Documentation Tool! This application is designed to help you create and visualize various types of diagrams essential for documenting complex systems, especially those involving AI and data management.

    From data flow diagrams to UML and BPMN, this tool provides a structured environment to define the components of your system and their interactions. It supports the creation of different diagram types with customizable nodes and connections, allowing for clear and comprehensive documentation.

    Use the navigation in the sidebar to select the specific type of diagram you want to create or learn more about. This tool aims to streamline your documentation process and improve communication among your project stakeholders.
    """)

def dfd_page():
    st.header("Data Flow Diagrams (DFDs)")
    dfd_description = f"""
    Illustrate the movement and transformation of data through a system.\n
    **Elements:** Processes (transform data), Data Stores (hold data), External Entities (sources/destinations), Data Flows (data movement).
    """
    st.write(dfd_description)
    diagram_page_logic(st.session_state, 'dfd', ["Process", "External Entity", "Data Store"], "Data Flows")

def bpmn_page():
    st.header("Business Process Model and Notation (BPMN)")
    bpmn_description = f"""
Model business processes from start to finish.\n
**Elements:** Events (triggers), Activities (tasks), Gateways (decisions), Sequence Flows (order), Message Flows (communication).
"""
    st.write(bpmn_description)
    diagram_page_logic(st.session_state, 'bpmn', ["Event", "Gateway", "Process"], "Sequence/Message Flows")

def uml_page():
    st.header("UML Diagrams")
    uml_description = f"""
Visualize software system structure and behavior.\n
**Elements:** Components (modules), Interfaces (interactions), Nodes (hardware/software), Artifacts (software elements), Classes (objects), Relationships (connections).
"""
    st.write(uml_description)
    diagram_page_logic(st.session_state, 'uml', ["Component", "Node", "Class"], "Relationships")

def erd_page():
    st.header("Entity-Relationship Diagrams (ERDs)")
    erd_description = f"""
Model data entities and their relationships.\n
**Elements:** Entities (objects), Attributes (properties), Relationships (associations), Cardinality (multiplicity).
"""
    st.write(erd_description)
    diagram_page_logic(st.session_state, 'erd', ["Entity", "Attribute"], "Relationships")

def process_flow_page():
    st.header("Process Flow Diagrams and Decision Flowcharts")
    process_flow_description = f"""
Show sequences of actions and decision-making logic.\n
**Elements:** Processes (actions), Decisions (choices), Start/End (beginnings/endings), Flows (direction).
"""
    st.write(process_flow_description)
    diagram_page_logic(st.session_state, 'process_flow', ["Process", "Decision", "Start/End"], "Flows")


def diagram_page_logic(session_state, diagram_type, node_types, connection_label):
    """
    Manages the UI logic for a specific diagram type.
    """
    if f'{diagram_type}_nodes' not in session_state:
        session_state[f'{diagram_type}_nodes'] = []
    if f'{diagram_type}_connections' not in session_state:
        session_state[f'{diagram_type}_connections'] = []

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.header("Nodes")
        node_name = st.text_input("Node Name:", key=f'{diagram_type}_node_name')
        node_type = st.selectbox("Node Type:", node_types, key=f'{diagram_type}_node_type')
        if st.button("Add Node", key=f'{diagram_type}_add_node'):
            if node_name:
                session_state[f'{diagram_type}_nodes'].append({"name": node_name, "type": node_type})
                st.success(f"Node '{node_name}' added.")
            else:
                st.warning("Please enter a node name.")
        for i, node in enumerate(session_state[f'{diagram_type}_nodes'][:] ): # Iterate over a copy
            col_node, col_delete_node = st.columns([3, 1])
            with col_node:
                st.markdown(f"- {node['type']}: {node['name']}")
            with col_delete_node:
                if st.button("🗑️", key=f'delete_{diagram_type}_node_{i}'):
                    del session_state[f'{diagram_type}_nodes'][i]
                    st.rerun()

    with col2:
        st.header(connection_label)
        node_names = [node["name"] for node in session_state[f'{diagram_type}_nodes']]
        source = st.selectbox("Source:", [""] + node_names, key=f'{diagram_type}_source')
        destination = st.selectbox("Destination:", [""] + node_names, key=f'{diagram_type}_dest')
        label = st.text_input("Label:", key=f'{diagram_type}_label')
        bidirectional = st.checkbox("Bidirectional", key=f'{diagram_type}_bidirectional')
        if st.button(f"Add {connection_label[:-1]}" if connection_label.endswith("s") else f"Add {connection_label}", key=f'{diagram_type}_add_connection'):
            if source and destination and label and source != destination:
                session_state[f'{diagram_type}_connections'].append(
                    {"source": source, "destination": destination, "label": label, "bidirectional": bidirectional}
                )
                st.success(f"{connection_label[:-1].capitalize() if connection_label.endswith('s') else connection_label.capitalize()} '{label}' added.")
            elif not source or not destination or not label:
                st.warning(f"Please fill in all fields for the {connection_label.lower()}.")
            elif source == destination:
                st.warning("Source and destination cannot be the same.")
        for i, connection in enumerate(session_state[f'{diagram_type}_connections'][:]): # Iterate over a copy
            col_connection, col_delete_connection = st.columns([4, 1])
            with col_connection:
                bidirectional_arrow = "<->" if connection['bidirectional'] else "->"
                st.markdown(f"- {connection['source']} {bidirectional_arrow} {connection['destination']}: {connection['label']}")
            with col_delete_connection:
                if st.button("🗑️", key=f'delete_{diagram_type}_connection_{i}'):
                    del session_state[f'{diagram_type}_connections'][i]
                    st.rerun()

        save_filename = st.text_input("Save As:", key=f'{diagram_type}_save_filename')
        if st.button("Save", key=f'{diagram_type}_save'):
            save_data(diagram_type, session_state[f'{diagram_type}_nodes'], session_state[f'{diagram_type}_connections'], save_filename)

    with col3:
        st.header("Load")
        available_files = get_available_data_files(diagram_type)
        if available_files:
            load_filename = st.selectbox("Select File to Load:", [""] + available_files, key=f'{diagram_type}_load_filename')
        else:
            st.info("No saved data files found.")
            load_filename = ""

        if st.button("Load", key=f'{diagram_type}_load_button'):
            if load_filename:
                loaded_nodes, loaded_connections = load_data(diagram_type, load_filename)
                if loaded_nodes is not None and loaded_connections is not None:
                    session_state[f'{diagram_type}_nodes'] = loaded_nodes
                    session_state[f'{diagram_type}_connections'] = loaded_connections
                    st.success(f"Data loaded from {diagram_type}_data_{load_filename}.json")
                else:
                    st.warning("Could not load data.")
            else:
                st.warning("Please select a file to load from.")

        if st.button("Reset", key=f'{diagram_type}_reset'):
            session_state[f'{diagram_type}_nodes'] = []
            session_state[f'{diagram_type}_connections'] = []
            st.rerun() # Force a rerun to clear the UI immediately

    st.header("Diagram")
    output_format = st.selectbox("Select output format:", ["png", "svg", "pdf", "dot"], key=f'{diagram_type}_output_format')
    layout_options = ["dot", "neato", "fdp", "sfdp", "twopi", "circo"]
    layout_style = st.selectbox("Select Layout Style:", layout_options, index=layout_options.index("dot"),
                                key=f'{diagram_type}_layout')
    label_position_options_dict = {
        'n': 'Top',
        'ne': 'Top-Right',
        'e': 'Right',
        'se': 'Bottom-Right',
        's': 'Bottom',
        'sw': 'Bottom-Left',
        'w': 'Left',
        'nw': 'Top-Left',
        'c': 'Center'
    }
    label_position_key_list = list(label_position_options_dict.keys())
    label_position_display_list = list(label_position_options_dict.values())
    label_position_index = label_position_key_list.index('c')
    selected_label_position_display = st.selectbox("Label Position:", label_position_display_list, index=label_position_index,
                                   key=f'{diagram_type}_label_position_display')
    label_position = [k for k, v in label_position_options_dict.items() if v == selected_label_position_display][0]

    fontsize_options = list(range(8, 31, 2))
    default_fontsize_index = fontsize_options.index(12)
    fontsize = st.selectbox("Select Font Size:", fontsize_options, index=default_fontsize_index, key=f'{diagram_type}_fontsize')

    label_distance = st.slider("Label Distance:", min_value=1.0, max_value=5.0, value=1.5, step=0.1,
                                 key=f'{diagram_type}_label_distance',
                                 help="Controls the distance of edge labels from the edges.")

    filename = st.text_input("Enter filename (without extension):", key=f'{diagram_type}_filename',
                                value=f"{diagram_type}_diagram")

    if st.button("Generate and Display Diagram", key=f'{diagram_type}_gen'):
        if session_state[f'{diagram_type}_nodes'] and session_state[f'{diagram_type}_connections']:
            dot = generate_diagram(session_state[f'{diagram_type}_nodes'],
                                     session_state[f'{diagram_type}_connections'], output_format, fontsize,
                                     layout_style, diagram_type, label_position, st.session_state[f'{diagram_type}_label_distance'])
            st.graphviz_chart(dot, use_container_width=True)
            filepath = save_diagram(dot, filename, output_format)
            if filepath:
                st.success(f"Diagram saved as: {filepath}")
        else:
            st.warning("Please add nodes and connections to generate the diagram.")
            
if __name__ == "__main__":
    main()