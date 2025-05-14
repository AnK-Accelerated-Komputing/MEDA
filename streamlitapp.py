"Run this script to start the Streamlit app to create CAD models"
import os
import time
from pathlib import Path

import streamlit as st
from streamlit_stl import stl_from_file

from MEDA.text_and_multi_chats import (designers_chat,
                                             multimodal_designers_chat)
from MEDA.create_agents import create_mechdesign_agents
from streamlit_utils.file_handler import FileHandler
from streamlit_utils.parameter_handler import ParameterHandler
from streamlit_utils.prompt_builder import PromptBuilder
from streamlit_utils.state_manager import StateManager
from config.llm_config import LLMConfigSelector, process_custom_llm_config


def render_custom_llm_config():
    """Render the custom LLM configuration controls."""
    model_name = st.text_input("Model Name", "Enter your model name here")
    api_type = st.text_input("API Type", "Enter your API type here")
    api_key = st.text_input(
        "API Key", "Enter your API key here", type="password")
    base_url = st.text_input("Base URL (Optional)") or None
    api_version = st.text_input("API Version (Optional)") or None
    return model_name, api_type, api_key, base_url, api_version


def render_llm_config_sidebar():
    """Render the LLM configuration controls in the sidebar."""
    with st.sidebar:
        st.title("LLM Configuration")

        selector = LLMConfigSelector()
        models_to_select = ["Default GPT-40",
                            "Default O1", "Text LLM", "Multimodal LLM"]
        option_selected = st.selectbox("Select Model Type", models_to_select)
        st.session_state.selected_model = option_selected
        if st.session_state.selected_model == "Default GPT-40":
            model_info = selector.get_default_model_info("gpt-4o")
            config = {
                "model": model_info["model"],
                "api_key": os.environ[model_info["api_key"]],
                "api_type": model_info["api_type"],
                "base_url": os.environ[model_info["base_url"]],
                "api_version": model_info["api_version"]

            }
            st.session_state.llm_config = config
            st.session_state.config_created = True
            st.success("Configuration created successfully!")

        if st.session_state.selected_model == "Default O1":
            model_info = selector.get_default_model_info("o1")
            config = {
                "model": model_info["model"],
                "api_key": os.environ[model_info["api_key"]],
                "api_type": model_info["api_type"],
                "base_url": os.environ[model_info["base_url"]],
                "api_version": model_info["api_version"]

            }
            st.session_state.llm_config = config
            st.session_state.config_created = True
            st.success("Configuration created successfully!")

        if st.session_state.selected_model == "Text LLM":
            available_models = selector.get_available_models(False)
            available_models.append("Custom Model")
            model_name = st.selectbox("Text only LLMs", available_models)
            if model_name == "Custom Model":
                model_name, api_type, base_url, api_version, api_key = render_custom_llm_config()
                config_custom = process_custom_llm_config(
                    model_name, api_type, api_key, base_url, api_version)
                st.session_state.llm_config = config_custom
                st.session_state.config_created = True
                st.success("Configuration created successfully!")
            else:
                model_info = selector.get_model_info(model_name)
                api_key_from_env = selector.get_api_key_from_env(model_name)
                use_env_key = st.checkbox(
                    "Use API key from environment", value=bool(api_key_from_env))
                if use_env_key and api_key_from_env:
                    api_key = api_key_from_env
                    st.success("Using API key from environment")
                else:
                    api_key = st.text_input("API Key", type="password")
                config = selector.create_config(model_name, api_key)
                st.session_state.llm_config = config
                st.session_state.config_created = True
                st.success("Configuration created successfully!")

        if st.session_state.selected_model == "Multimodal LLM":
            available_models = selector.get_available_models(True)
            available_models.append("Custom Model")
            model_name = st.selectbox("Multimodal LLMs", available_models)
            if model_name == "Custom Model":
                model_name, api_type, base_url, api_version, api_key = render_custom_llm_config()
                config_custom = process_custom_llm_config(
                    model_name, api_type, api_key, base_url, api_version)
                st.session_state.llm_config = config_custom
                st.session_state.config_created = True
                st.success("Configuration created successfully!")

            else:
                model_info = selector.get_model_info(model_name)
                api_key_from_env = selector.get_api_key_from_env(model_name)
                use_env_key = st.checkbox(
                    "Use API key from environment", value=bool(api_key_from_env))
                if use_env_key and api_key_from_env:
                    api_key = api_key_from_env
                    st.success("Using API key from environment")
                else:
                    api_key = st.text_input("API Key", type="password")
                config = selector.create_config(model_name, api_key)
                st.session_state.llm_config = config
                st.session_state.config_created = True
                st.success("Configuration created successfully!")


def initialize_session_state():
    "Intialize default state of streamlit UI"
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None
    if 'llm_config' not in st.session_state:
        st.session_state.llm_config = None
    if 'config_created' not in st.session_state:
        st.session_state.config_created = False
    default_state = StateManager.get_default_state()
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if st.session_state.stl_timestamp is None:
        st.session_state.stl_timestamp = time.time()


def render_parameter_controls(python_file_path):
    "Render the parameter controls for the CAD model"
    st.write("### CAD Model Parameters")

    if not python_file_path or not Path(python_file_path).exists():
        return

    handler = ParameterHandler()
    current_params = handler.extract_parameters(python_file_path)

    if not current_params:
        return

    new_params = {}
    for param_name, param_value in current_params.items():
        new_value = st.number_input(
            f"{param_name}",
            value=float(param_value),
            step=0.1,
            format="%.3f",
            key=f"param_{param_name}"
        )
        new_params[param_name] = new_value

    if st.button("Regenerate CAD", key="regenerate_cad"):
        if handler.update_python_file(python_file_path, new_params):
            if handler.execute_python_file(python_file_path):
                st.session_state.stl_timestamp = time.time()
                st.success("CAD model regenerated successfully!")
                st.rerun()


def render_controls():
    "Render the main controls for the Streamlit app"
    agents_list = \
        create_mechdesign_agents(st.session_state.llm_config)
    multimodal_agents = [agents_list[0],
                        agents_list[1],
                        agents_list[2],
                        agents_list[3],
                        agents_list[4],
                        agents_list[6]]
    text_agents = [agents_list[0],
                    agents_list[1],
                    agents_list[2],
                    agents_list[3],
                    agents_list[4],]
    text_prompt = st.text_input("Let's design",
                                value=st.session_state.prompt,
                                placeholder="Enter a text prompt here",
                                key="input_prompt")
    uploaded_file = None
    if st.session_state.selected_model != "Text LLM":
        uploaded_file = st.file_uploader(
            "Upload an engineering drawing image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image_path = FileHandler.save_uploaded_file(uploaded_file)
        if image_path and Path(image_path).exists():
            st.session_state.current_image_path = image_path
            st.image(image_path, caption="Uploaded Image",
                     use_container_width=True)

    if st.button("Generate CAD Model"):
        final_prompt = PromptBuilder.build_prompt(
            text_prompt, st.session_state.current_image_path)
        if final_prompt:
            with st.spinner("Generating CAD model..."):
                try:
                    if st.session_state.selected_model == "Text LLM" or uploaded_file is None:
                        generated_files = designers_chat(
                            text_agents, st.session_state.llm_config, final_prompt)
                    else:
                        generated_files = multimodal_designers_chat(
                            multimodal_agents, st.session_state.llm_config, final_prompt)
                    st.session_state.generated_py_file = generated_files.get(
                        'py')
                    st.session_state.current_stl_path = generated_files.get(
                        'stl')
                    st.rerun()
                except (FileNotFoundError, ValueError) as e:
                    st.error(f"Error generating CAD model: {str(e)}")


def visualization_controls():
    "Render the visualization controls for the CAD model"
    # st.subheader("Visualization Controls")

    controls = {
        'color': st.color_picker("Pick a color", value=st.session_state.color),
        'material': st.selectbox("Select a material",
                                 ["material", "flat", "wireframe"],
                                 index=["material", "flat", "wireframe"].index(st.session_state.material)),
        'auto_rotate': st.toggle("Auto rotation", value=st.session_state.auto_rotate),
        'opacity': st.slider("Opacity", min_value=0.0, max_value=1.0, value=st.session_state.opacity),
        'height': st.slider("Height", min_value=50, max_value=1000, value=st.session_state.height)
    }

    # st.subheader("Camera Controls")
    # camera_controls = {
    #     'cam_v_angle': st.number_input("Camera Vertical Angle", value=st.session_state.cam_v_angle),
    #     'cam_h_angle': st.number_input("Camera Horizontal Angle", value=st.session_state.cam_h_angle),
    #     'cam_distance': st.number_input("Camera Distance", value=st.session_state.cam_distance),
    #     'max_view_distance': st.number_input("Max view distance", min_value=1, value=st.session_state.max_view_distance)
    # }

    for key, value in {**controls}.items():
        st.session_state[key] = value


def render_stl_viewer():
    "Render the STL viewer"
    viewer_key = f'stl_viewer_{st.session_state.stl_timestamp}'
    stl_from_file(
        file_path=st.session_state.current_stl_path,
        color=st.session_state.color,
        material=st.session_state.material,
        auto_rotate=st.session_state.auto_rotate,
        opacity=st.session_state.opacity,
        height=st.session_state.height,
        shininess=100,
        cam_v_angle=st.session_state.cam_v_angle,
        cam_h_angle=st.session_state.cam_h_angle,
        cam_distance=st.session_state.cam_distance,
        max_view_distance=st.session_state.max_view_distance,
        key=viewer_key
    )


def render_download_buttons():
    "Render the download buttons for the CAD files"
    stl_file = st.session_state.current_stl_path
    step_file = stl_file.replace(".stl", ".step")

    left_col, right_col = st.columns([4, 1])
    with left_col:
        with open(step_file, "rb") as file:
            st.download_button(
                label="Download CAD STEP",
                data=file,
                file_name=Path(step_file).name,
                mime="application/octet-stream"
            )
    with right_col:
        with open(stl_file, "rb") as file:
            st.download_button(
                label="Download CAD STL",
                data=file,
                file_name=Path(stl_file).name,
                mime="application/octet-stream"
            )


def render_example_prompts():
    "Render example prompts for the user"
    st.subheader("Example Prompts")
    examples = [
        "A box with a through hole in the center.",
        "Create a pipe of outer diameter 50mm and inside diameter 40mm.",
        "Create a circular plate of radius 2mm and thickness 0.125mm with four holes of radius 0.25mm patterned at distance of 1.5mm from the centre along the axes."
    ]
    for example in examples:
        if st.button(example, key=f"example_{example}"):
            st.session_state.prompt = example
            st.rerun()


def main():
    "Main function to run the Streamlit app"
    st.set_page_config(layout="wide")
    initialize_session_state()

    if st.session_state.current_image_path:
        FileHandler.cleanup_temp_files(st.session_state.current_image_path)
    render_llm_config_sidebar()
    st.title("AnK CAD")

    left_col, middle_col, right_col = st.columns([0.75, 2, 0.5])

    with left_col:
        render_controls()
        visualization_controls()
    with middle_col:
        render_stl_viewer()
        render_download_buttons()
        render_example_prompts()
    with right_col:
        if st.session_state.generated_py_file:
            render_parameter_controls(st.session_state.generated_py_file)


if __name__ == "__main__":
    main()
