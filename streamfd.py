import streamlit as st
from graphviz import Digraph
import json
import os
from io import StringIO

# --- Helper Functions ---

def draw_node(dot, node_name, node_type):
    """Draws a node with the appropriate shape."""
    if node_type == "Process":
        dot.node(node_name, node_name, shape="ellipse")
    elif node_type == "External Entity":
        dot.node(node_name, node_name, shape="square")
    elif node_type == "Data Store":
        dot.node(node_name, node_name, shape="cylinder")
    elif node_type == "Event":
        dot.node(node_name, node_name, shape="circle")
    elif node_type == "Gateway":
        dot.node(node_name, node_name, shape="diamond")
    elif node_type == "Component":
        dot.node(node_name, node_name, shape="component")
    elif node_type == "Node":
        dot.node(node_name, node_name, shape="box3d")
    elif node_type == "Class":
        dot.node(node_name, node_name, shape="record")
    elif node_type == "Entity":
        dot.node(node_name, node_name, shape="box")
    else:
        dot.node(node_name, node_name, shape="ellipse")


def generate_data_flow_diagram(nodes, flows, output_format="png"):
    """Generates a data flow diagram with standard symbols."""
    dot = Digraph(comment='Data Flow Diagram', format=output_format)

    for node in nodes:
        draw_node(dot, node["name"], node["type"])

    for flow in flows:
        dot.edge(flow["source"], flow["destination"], label=flow["label"])

    return dot

def generate_bpmn_diagram(nodes, flows, output_format="png"):
    dot = Digraph(comment='BPMN Diagram', format=output_format)
    for node in nodes:
        draw_node(dot, node["name"], node["type"])
    for flow in flows:
        dot.edge(flow["source"], flow["destination"], label=flow["label"])
    return dot

def generate_uml_diagram(nodes, flows, output_format="png"):
    dot = Digraph(comment='UML Diagram', format=output_format)
    for node in nodes:
        draw_node(dot, node["name"], node["type"])
    for flow in flows:
        dot.edge(flow["source"], flow["destination"], label=flow["label"])
    return dot

def generate_erd_diagram(nodes, flows, output_format="png"):
    dot = Digraph(comment='ERD Diagram', format=output_format)
    for node in nodes:
        draw_node(dot, node["name"], node["type"])
    for flow in flows:
        dot.edge(flow["source"], flow["destination"], label=flow["label"])
    return dot

def generate_process_flow_diagram(nodes, flows, output_format="png"):
    dot = Digraph(comment='Process Flow Diagram', format=output_format)
    for node in nodes:
        draw_node(dot, node["name"], node["type"])
    for flow in flows:
        dot.edge(flow["source"], flow["destination"], label=flow["label"])
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
            st.text(dot.source)
        else:
            st.graphviz_chart(dot)
    except Exception as e:
        st.error(f"Error displaying diagram: {e}")

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

    From data flow diagrams to UML and BPMN, this tool provides a structured environment to define the components of your system and their interactions. It supports the creation of different diagram types with customizable nodes and flows, allowing for clear and comprehensive documentation.

    Use the navigation in the sidebar to select the specific type of diagram you want to create or learn more about. This tool aims to streamline your documentation process and improve communication among your project stakeholders.
    """)

def dfd_page():
    st.header("Data Flow Diagrams (DFDs)")
    dfd_description = f"""
    Illustrate the movement and transformation of data through a system.\n
    **Elements:** Processes (transform data), Data Stores (hold data), External Entities (sources/destinations), Data Flows (data movement).
    """
    st.write(dfd_description)
    diagram_page_logic(st.session_state, 'dfd', ["Process", "External Entity", "Data Store"], generate_data_flow_diagram)

def bpmn_page():
    st.header("Business Process Model and Notation (BPMN)")
    bpmn_description = f"""
Model business processes from start to finish.\n
**Elements:** Events (triggers), Activities (tasks), Gateways (decisions), Sequence Flows (order), Message Flows (communication).
"""
    st.write(bpmn_description)
    diagram_page_logic(st.session_state, 'bpmn', ["Event", "Gateway", "Process"], generate_bpmn_diagram)

def uml_page():
    st.header("UML Diagrams")
    uml_description = f"""
Visualize software system structure and behavior.\n
**Elements:** Components (modules), Interfaces (interactions), Nodes (hardware/software), Artifacts (software elements), Classes (objects), Relationships (connections).
"""
    st.write(uml_description)
    diagram_page_logic(st.session_state, 'uml', ["Component", "Node", "Class"], generate_uml_diagram)

def erd_page():
    st.header("Entity-Relationship Diagrams (ERDs)")
    erd_description = f"""
Model data entities and their relationships.\n
**Elements:** Entities (objects), Attributes (properties), Relationships (associations), Cardinality (multiplicity).
"""
    st.write(erd_description)
    diagram_page_logic(st.session_state, 'erd', ["Entity", "Attribute"], generate_erd_diagram)

def process_flow_page():
    st.header("Process Flow Diagrams and Decision Flowcharts")
    process_flow_description = f"""
Show sequences of actions and decision-making logic.\n
**Elements:** Processes (actions), Decisions (choices), Start/End (beginnings/endings), Flows (direction).
"""
    st.write(process_flow_description)
    diagram_page_logic(st.session_state, 'process_flow', ["Process", "Decision", "Start/End"], generate_process_flow_diagram)

def diagram_page_logic(session_state, diagram_type, node_types, generate_function):
    if f'{diagram_type}_nodes' not in session_state:
        session_state[f'{diagram_type}_nodes'] = []
    if f'{diagram_type}_flows' not in session_state:
        session_state[f'{diagram_type}_flows'] = []

    col1, col2 = st.columns(2)

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
        for i, node in enumerate(session_state[f'{diagram_type}_nodes']):
            st.write(f"{node['type']}: {node['name']}  [<a href='#' id='delete_{diagram_type}_node_{i}'>Delete</a>]", unsafe_allow_html=True)
            st.markdown(f"""
            <script>
            document.getElementById('delete_{diagram_type}_node_{i}').addEventListener('click', function() {{
                Streamlit.setSessionState({{{diagram_type}_nodes: {json.dumps(session_state[f'{diagram_type}_nodes'][:i] + session_state[f'{diagram_type}_nodes'][i+1:])}}});
            }});
            </script>
            """, unsafe_allow_html=True)

    with col2:
        st.header("Data Flows")
        node_names = [node["name"] for node in session_state[f'{diagram_type}_nodes']]
        source = st.selectbox("Source:", [""] + node_names, key=f'{diagram_type}_source')
        destination = st.selectbox("Destination:", [""] + node_names, key=f'{diagram_type}_dest')
        label = st.text_input("Label:", key=f'{diagram_type}_label')
        if st.button("Add Data Flow", key=f'{diagram_type}_add_flow'):
            if source and destination and label and source != destination:
                session_state[f'{diagram_type}_flows'].append({"source": source, "destination": destination, "label": label})
                st.success(f"Data flow '{label}' added.")
            elif not source or not destination or not label:
                st.warning("Please fill in all fields for the data flow.")
            elif source == destination:
                st.warning("Source and destination cannot be the same.")
        for i, flow in enumerate(session_state[f'{diagram_type}_flows']):
            st.write(f"{flow['source']} -> {flow['destination']}: {flow['label']} [<a href='#' id='delete_{diagram_type}_flow_{i}'>Delete</a>]", unsafe_allow_html=True)
            st.markdown(f"""
            <script>
            document.getElementById('delete_{diagram_type}_flow_{i}').addEventListener('click', function() {{
                Streamlit.setSessionState({{{diagram_type}_flows: {json.dumps(session_state[f'{diagram_type}_flows'][:i] + session_state[f'{diagram_type}_flows'][i+1:])}}});
            }});
            </script>
            """, unsafe_allow_html=True)

    st.header("Diagram")
    output_format = st.selectbox("Select output format:", ["png", "svg", "pdf", "dot"], key=f'{diagram_type}_output_format')
    filename = st.text_input("Enter filename (without extension):", key=f'{diagram_type}_filename', value=f"{diagram_type}_diagram")


    if st.button("Generate, Display and Save Diagram", key=f'{diagram_type}_gen'):
        if session_state[f'{diagram_type}_nodes'] and session_state[f'{diagram_type}_flows']:
            dot = generate_function(session_state[f'{diagram_type}_nodes'], session_state[f'{diagram_type}_flows'], output_format)
            # Display diagram - Full width, adjust font size
            st.graphviz_chart(dot, use_container_width=True)
            # Save diagram
            filepath = save_diagram(dot, filename, output_format)
            if filepath:
                st.success(f"Diagram saved as: {filepath}")
        else:
            st.warning("Please add nodes and data flows to generate the diagram.")

                
if __name__ == "__main__":
    main()