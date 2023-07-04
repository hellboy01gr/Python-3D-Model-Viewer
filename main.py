import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from imgui.integrations.pygame import PygameRenderer
import pywavefront
import imgui
import time
import numpy as np

from pyimgui_filepicker import *


# Set up the window
pygame.init()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("3D Renderer")
pygame_icon = pygame.image.load('icon.png')
pygame.display.set_icon(pygame_icon)

clock = pygame.time.Clock()

# Set up the OpenGL perspective
glViewport(0, 0, width, height)
glMatrixMode(GL_PROJECTION)
gluPerspective(90, width / height, 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)
glEnable(GL_DEPTH_TEST)

# Initialize camera rotation angles
angle_x = 0
angle_y = 0
dragging = False
last_mouse_pos = (0, 0)
rotation_speed = 0.4
zoom = -5.0
zoom_speed = 0.5

# ImGui initialization
imgui.create_context()
impl = PygameRenderer()

io = imgui.get_io()
io.display_size = (width, height)

# FPS variables
FPSstart_time = pygame.time.get_ticks()
frame_count = 0
fps = str(0)

start_time = 0
frame_times = []

# Mesh loading
def load_mesh(filename):
    scene = pywavefront.Wavefront(filename, collect_faces=True)

    scene_box = (scene.vertices[0], scene.vertices[0])
    for vertex in scene.vertices:
        min_v = [min(scene_box[0][i], vertex[i]) for i in range(3)]
        max_v = [max(scene_box[1][i], vertex[i]) for i in range(3)]
        scene_box = (min_v, max_v)

    scene_size = [scene_box[1][i] - scene_box[0][i] for i in range(3)]
    max_scene_size = max(scene_size)
    scaled_size = 5
    scene_scale = [scaled_size / max_scene_size for i in range(3)]
    scene_trans = [-(scene_box[1][i] + scene_box[0][i]) / 2 for i in range(3)]

    return scene, scene_scale, scene_trans


def render_mesh(scene, scene_scale, scene_trans, frag_color):
    glPushMatrix()
    glScalef(*scene_scale)
    glTranslatef(*scene_trans)

    glColor3f(*frag_color)

    for mesh in scene.mesh_list:
        glBegin(GL_TRIANGLES)
        for face in mesh.faces:
            for vertex_i in face:
                glVertex3f(*scene.vertices[vertex_i])
        glEnd()

    glPopMatrix()

global path
path = "meshes/Sphere.obj"
current_filepicker = None

scene, scene_scale, scene_trans = load_mesh(path)
mesh_color = (0.91, 0.745, 0.675)  # Define the mesh color here

# Main loop
running = True
draw_data = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                dragging = True
                last_mouse_pos = pygame.mouse.get_pos()
            elif event.button == 4:  # Scroll wheel up
                zoom += zoom_speed
            elif event.button == 5:  # Scroll wheel down
                zoom -= zoom_speed
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_pos = pygame.mouse.get_pos()
                dx = mouse_pos[0] - last_mouse_pos[0]
                dy = mouse_pos[1] - last_mouse_pos[1]
                angle_x += dy * rotation_speed
                angle_y += dx * rotation_speed
                last_mouse_pos = mouse_pos

        # ImGui event handling
        impl.process_event(event)

    # Update status FPS
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - FPSstart_time
    frame_count += 1

    if elapsed_time > 1000:
        fps = str(round(frame_count / (elapsed_time / 1000.0), 2))
        FPSstart_time = current_time
        frame_count = 0

    # Update frame times
    current_time = time.time()
    frame_time = current_time - start_time
    frame_times.append(frame_time)
    start_time = current_time

    if len(frame_times) > 100:
        frame_times.pop(0)

    # ImGui new frame
    imgui.new_frame()

    opened_state = True
    # Render ImGui window
    imgui.begin("Settings", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)

    # Window style
    style = imgui.get_style()
    style.window_rounding = 7
    style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.1, 0.9)
    style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.9, 0.2, 0.1, 0.8)
    style.colors[imgui.COLOR_TITLE_BACKGROUND] = (0.6, 0.1, 0, 0.8)
    style.colors[imgui.COLOR_TAB] = (0.8, 0.1, 0, 0.9)
    style.colors[imgui.COLOR_TAB_ACTIVE] = (0.9, 0.2, 0, 0.9)
    style.colors[imgui.COLOR_TAB_UNFOCUSED_ACTIVE] = (0.6, 0.1, 0, 0.9)
    style.colors[imgui.COLOR_TAB_UNFOCUSED] = (0.5, 0, 0, 0.9)
    style.colors[imgui.COLOR_TAB_HOVERED] = (1, 0.2, 0.1, 0.9)

    # Window contents
    with imgui.begin_tab_bar("N/A") as tab_bar:
        if tab_bar.opened:
            with imgui.begin_tab_item("Stats") as Statstab:
                if Statstab.selected:
                    imgui.text_colored("FPS: " + fps, 0.6, 1, 0.4)
                    if len(frame_times) > 0:
                        frame_times_arr = np.array(frame_times)
                        frame_times_arr = frame_times_arr.astype(np.float32)
                        imgui.plot_lines("Frame Time", frame_times_arr, scale_min=0, scale_max=0.05, graph_size=(0, 80))

            with imgui.begin_tab_item("Settings") as Settingstab:
                opened_state = Settingstab.opened
                if Settingstab.selected:
                    changed, rotation_speed = imgui.input_float('Cam Rotation Multiplier', rotation_speed, 0.1)
                    changed, zoom_speed = imgui.input_float('Zoom Multiplier', zoom_speed, 0.1)

                    with imgui.begin_list_box("Viewport Shading", 210, 50) as shading_options:
                        if shading_options.opened:
                            if imgui.button("Solid                       "):
                                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                            
                            if imgui.button("Wireframe                   "):
                                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                            
                    if imgui.button("Select model..."):
                        def callback(selected):
                            global path
                            path = selected
                        current_filepicker = FilePicker("Select a model", callback=callback)
                    if current_filepicker:
                        # Draw filepicker every frame
                        current_filepicker.tick()
                        if not current_filepicker.active:
                            current_filepicker = None
                            scene, scene_scale, scene_trans = load_mesh(path)
                    imgui.text("Current model: " + path)
                    imgui.text_colored("!!! Please select only .obj files with a \n corresponding .mtl file in the same directory", 1, 0, 0)

                    changed, mesh_color = imgui.color_edit3("Mesh color", * mesh_color)
                            
    imgui.end()

    #Menu bar
    with imgui.begin_main_menu_bar() as main_menu_bar:
        if main_menu_bar.opened:
            # first menu dropdown
            with imgui.begin_menu("File", True) as file_menu:
                if file_menu.opened:
                    imgui.menu_item("Open", "Ctrl+O", False, True)
                    imgui.menu_item("Exit", "Alt+F4")

            with imgui.begin_menu("View", True) as view_menu:
                if view_menu.opened:
                    imgui.menu_item("Viewport Shading")

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, zoom)  # Translate along z-axis for zoom
    glRotatef(angle_x, 1, 0, 0)  # Rotate around X-axis
    glRotatef(angle_y, 0, 1, 0)  # Rotate around Y-axis
    
    glRotatef(0.5, 0, 1, 0)  # Add rotation around the Y-axis
    
    # Render the loaded mesh
    render_mesh(scene, scene_scale, scene_trans, mesh_color)

    # Render ImGui
    imgui.render()
    if draw_data is None:
        draw_data = imgui.get_draw_data()
    impl.render(draw_data)

    # Flip the display
    pygame.display.flip()
    clock.tick(60)
