"Initializes the state manager for the application."
class StateManager:
    """
    Manages the state for the application.
    """
    @staticmethod
    def get_default_state():
        "Returns the default state for the application."
        return {
            'stl_timestamp': None,
            'prompt': "",
            'current_stl_path': 'data/MEDA.stl',
            'current_image_path': None,
            'generated_py_file': None,
            'color': "#FF9900",
            'material': "material",
            'auto_rotate': True,
            'opacity': 1.0,
            'height': 500,
            'cam_v_angle': 30,
            'cam_h_angle': 45,
            'cam_distance':0,
            'max_view_distance': 2000
        }