from sympy.physics.mechanics import ReferenceFrame, Point
from visualization_frame import VisualizationFrame
from camera import PerspectiveCamera
from server import create_server
import json
import os
import distutils
import pydy_viz

try:
    from IPython.core.display import Javascript, HTML, display
except ImportError:
    pass

#TODOS: implement display() methods


class Scene(object):
    """
    Scene class holds all the data required for the visualizations/
    animation of a system.

    It has methods for inputting the numerical data from the numerical
    integrations of Equations of Motions and convert them to JSON
    values, which can be then parsed by Javascripts(webgls).

    A scene object takes a ReferenceFrame, and a Point as required
    arguments. The reference_frame and point act as the inertial
    frame and origin with respect to which all objects are oriented
    and rendered in the visualizations

    A scene needs to be supplied with visualization_frames, Cameras,
    and Light objects, as optional arguments.
    A scene can also be supplied with the height and width of the
    browser window where visualization would be displayed.
    Default is 800 * 800.


    """

    def __init_(self, reference_frame, origin, *visualization_frames,
                **kwargs):
        """
        Initializes a Scene instance.
        It requires a reference frame and a point to be initialized.

        Parameters:
        ===========

        reference_frame : ReferenceFrame
            All the transformations would be carried out with respect to
            this reference frame.

        origin : Point
            All the transformations would be carried out with respect to
            this point.

        visualization_frames : VisualizationFrame
            A tuple of visualization frames which are to visualized in the
            scene.

        name : str, optional
            Name of Scene object.

        width : int or float, optional
            width of the canvas used for visualizations.Default is 800.

        height : int or float
            height of the canvas used for visualizations.Default is 800.

        camera : Camera, optional
            camera with which to display the object. Default is
            PerspectiveCamera, with reference_frame and origin same as
            defined for this scene.
        """

        try:
            self._name = kwargs['name']
        except KeyError:
            self._name = 'unnamed'

        try:
            self._width = kwargs['width']
        except KeyError:
            self._width = 800

        try:
            self._height = kwargs['height']
        except KeyError:
            self._height = 800

        try:
            self.cameras = kwargs['cameras']
        except KeyError:
            self.cameras = [PerspectiveCamera(self._reference_frame,
                                              self._origin)]

        try:
            self.lights = kwargs['lights']
        except KeyError:
            #TODO add Light
            pass

        self._reference_frame = reference_frame
        self._origin = origin

        self.visualization_frames = [vis_frame for vis_frame in
                                     visualization_frames]

    @property
    def name(self):
        """
        Returns Name of Scene.
        """
        return self._name

    @name.setter
    def name(self, new_name):
        """
        sets name of scene.
        """
        if not isinstance(new_name, str):
            raise TypeError('Name should be a valid str.')
        else:
            self._name = new_name

    @property
    def origin(self):
        """
        returns Origin of the Scene.

        """
        return self._origin

    @origin.setter
    def origin(self, new_origin):
        """
        sets origin of the scene
        """
        if not isinstance(new_origin, Point):
            raise TypeError('''origin should be a valid Point Object''')
        else:
            self._origin = new_origin

    @property
    def reference_frame(self):
        """
        returns reference_frame of the Scene.
        """
        return self._reference_frame

    @reference_frame.setter
    def reference_frame(self, new_reference_frame):
        """
        Sets reference frame for the scene.
        """
        if not isinstance(new_reference_frame, ReferenceFrame):
            raise TypeError('''reference_frame should be a valid
                                ReferenceFrame object.''')
        else:
            self._reference_frame = new_reference_frame

    def _generate_data(self, dynamic_variables, constant_variables,
                       dynamic_values, constant_values):
        """
        This method is called from the generate_visualization_dict()
        method or generate_visualization_json() method
        For more information view Docstrings for those methods.

        """
        self._scene_data = {}
        self._scene_data['name'] = self._name
        self._scene_data['height'] = self._height
        self._scene_data['width'] = self._width
        self._scene_data['frames'] = []
        self._scene_data['cameras'] = []

        for frame in self.visualization_frames + self.cameras:

            frame.generate_transformation_matrix(self._reference_frame,
                                                 self._origin)
            frame.generate_numeric_transform_function(dynamic_variables,
                                                      constant_variables)
            frame.evaluate_transformation_matrix(dynamic_values,
                                                 constant_values)

            if isinstance(frame, VisualizationFrame):
                self._scene_data['frames'].append(
                    frame.generate_visualization_dict())
            else:
                self._scene_data['cameras'].append(
                    frame.generate_visualization_dict())

        return self._scene_data

    def generate_visualization_dict(self, dynamic_variables,
                                    constant_variables, dynamic_values,
                                    constant_values):
        """
        generate_visualization_dict() method generates
        a dictionary of visualization data


        Parameters
        ==========
        dynamic_variables : Sympifyable list or tuple
            This contains all the dynamic symbols or state variables
            which are required for solving the transformation matrices
            of all the frames of the scene.

        constant_variables : Sympifyable list or tuple
            This contains all the symbols for the parameters which are
            used for defining various objects in the system.

        dynamic_values : list or tuple
            initial states of the system. The list or tuple
            should be respective to the state_sym.

        constant_values : list or tuple
            values of the parameters. The list or tuple
            should be respective to the par_sym.

        Returns
        =======

        The dictionary contains following keys:
        1) Width of the scene.
        2) Height of the scene.
        3) name of the scene.
        4) frames in the scene, which contains sub-dictionaries
           of all the visualization frames information.


        """
        self._data_dict = self._generate_data(dynamic_variables,
                                              constant_variables,
                                              dynamic_values,
                                              constant_values)

        return self._data_dict

    def generate_visualization_json(self, dynamic_variables,
                                    constant_variables, dynamic_values,
                                    constant_values, save_to='data.json'):
        """
        generate_visualization_json() method generates a json str, which is
        saved to file.

        Parameters
        ==========
        dynamic_variables : Sympifyable list or tuple
            This contains all the dynamic symbols or state variables
            which are required for solving the transformation matrices
            of all the frames of the scene.

        constant_variables : Sympifyable list or tuple
            This contains all the symbols for the parameters which are
            used for defining various objects in the system.

        dynamic_values : list or tuple
            initial states of the system. The list or tuple
            should be respective to the state_sym.

        constant_values : list or tuple
            values of the parameters. The list or tuple
            should be respective to the par_sym.

        save_to : str
            path to the file where to write the generated data JSON.
            the path should be chosen such as to have the write
            permissions to the user.


        """
        self.saved_json_file = save_to
        self._data_dict = self._generate_data(dynamic_variables,
                                              constant_variables,
                                              dynamic_values,
                                              constant_values)
        outfile = open(self.saved_json_file)
        outfile.write(json.dumps(self._data_dict, indent=4,
                                 separators=(',', ': ')))
        outfile.close()

    def _display_from_ipython(self):
        raise NotImplemented

    def _display_from_interpreter(self):
        raise NotImplemented

    def display(self):
        """
        display method can be used in two ways.
        When called from IPython notebook, it shows the visualization
        in the form of output cell in the IPython notebook.
        If it is called from python interpreter or
        IPython interpreter(not notebook), It generates an html file,
        in the current directory, which can be opened in the webgl
        compliant browser for viewing the visualizations.
        The simulation data is used from this scene, hence
        all simulation data generation methods should be called before
        calling this method

        """
        #First copy static files to current working directory
                #Copy static files to directory
        try:
            project_pydy_dir = os.path.join(os.getcwd, '.pydy_viz')
            os.mkdir(project_pydy_dir)
            static_dir = os.path.join(os.path.dirname(pydy_viz.__file__),
                                      'static')
            distutils.dir_util.copy_tree(static_dir, project_pydy_dir)
        except OSError:
            #If static exist, no need to overwrite anything
            pass

        try:
            config = get_ipython().config
            if config['KernelApp']['parent_appname'] == \
               'ipython-notebook':
                self._display_from_ipython()
            else:
                self._display_from_interpreter()

        except:
            self._display_from_interpreter()

