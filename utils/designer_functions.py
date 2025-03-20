"""
This module provides functions for creating various CAD models using CadQuery.
"""

import cadquery as cq
from cadquery import exporters
from typing import Annotated, Callable, List, Tuple
from pathlib import Path
from math import *
from typing_extensions import Annotated
from ocp_vscode import *
from mechdesignagents.test.agents_v2 import *

# # Set up work directory for code execution
workdir = Path("./NewCADs")

# Custom decorator for registration


def register_cad_function(description: str):
    def decorator(func: Callable):
        User.register_function(
            function_map={func.__name__: func}
        )
        functioncall_agent.register_for_llm(description=description)(func)
        return func
    return decorator


# Function for creating a plate
@register_cad_function(description="Create a CAD plate model.")
def create_plate(length: Annotated[float, "Length of the plate"],
                 width: Annotated[float, "Width of the plate"],
                 thickness: Annotated[float, "Thickness of the plate"]) -> str:
    plate = cq.Workplane("XY").box(length, width, thickness)
    show_object(plate)
    file_path = workdir / "plate.stl"
    cq.exporters.export(plate, str(file_path))
    return f"Plate model created and saved as {file_path}"


# Function for creating a box
@register_cad_function(description="Create a CAD box model.")
def create_box(width: Annotated[float, "Width of the box"],
               height: Annotated[float, "Height of the box"],
               depth: Annotated[float, "Depth of the box"]) -> str:
    box = cq.Workplane("XY").box(width, height, depth)
    show_object(box)
    file_path = workdir / "box.stl"
    cq.exporters.export(box, str(file_path))
    return f"Box model created and saved as {file_path}"


# Function for creating a cylinder
@register_cad_function(description="Create a CAD cylinder model.")
def create_cylinder(radius: Annotated[float, "Radius of the cylinder"],
                    height: Annotated[float, "Height of the cylinder"]) -> str:
    cylinder = cq.Workplane("XY").circle(radius).extrude(height)
    show_object(cylinder)
    file_path = workdir / "cylinder.stl"
    cq.exporters.export(cylinder, str(file_path))
    return f"Cylinder model created and saved as {file_path}"


# Function for creating a cone
@register_cad_function(description="Create a CAD cone model.")
def create_cone(base_radius: Annotated[float, "Radius of the cone base"],
                height: Annotated[float, "Height of the cone"],
                top_radius: Annotated[float, "Radius of the cone top"]) -> str:
    # Create the cone shape with a loft operation
    cone = cq.Workplane("XY").circle(base_radius).workplane(
        offset=height).circle(top_radius).loft()
    show_object(cone)
    # Export the result to an STL file
    file_path = workdir / "cone.stl"
    exporters.export(cone, str(file_path))
    return f"Cone model created and saved as {file_path}"

# Function for creating a sphere


@register_cad_function(description="Create a CAD sphere model.")
def create_sphere(radius: Annotated[float, "Radius of the sphere"]) -> str:
    # Create the sphere
    sphere = cq.Workplane("XY").sphere(radius)
    show_object(sphere)
    # Export the result to an STL file
    file_path = workdir / "sphere.stl"
    exporters.export(sphere, str(file_path))
    return f"Sphere model created and saved as {file_path}"


# Function for creating a plate with centered hole
@register_cad_function(description="Create a CAD plate with a centered hole.")
def create_plate_with_hole(length: Annotated[float,
                                             "Length of the plate"],
                           width: Annotated[float,
                                            "Height of the plate"],
                           thickness: Annotated[float,
                                                "Thickness of the plate"],
                           center_hole_dia: Annotated[float,
                                                      "Diameter of the center hole"]) -> str:
    # Create the plate with a centered hole
    result = (cq.Workplane("XY").box(length, width, thickness).faces(
        ">Z").workplane().hole(center_hole_dia))
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "plate_with_hole.stl"
    exporters.export(result, str(file_path))
    return f"Plate model created and saved as {file_path}"


# Function for creating a torus
@register_cad_function(description="Create a CAD torus model.")
def create_torus(major_radius: Annotated[float,
                                         "Major radius (distance from torus center to tube center)"],
                 minor_radius: Annotated[float,
                                         "Minor radius (radius of the tube)"]) -> str:
    # Draw a 2D circle for the minor radius (the tube of the torus)
    torus = cq.Solid.makeTorus(major_radius, minor_radius)
    show(torus)
    file_path = workdir / "torus.stl"
    exporters.export(torus, str(file_path))
    return f"Torus model created and saved as {file_path}"


# Function for creating a rectangular tube
@register_cad_function(description="Create a CAD rectangular tube model.")
def create_rectangular_tube(outer_width: Annotated[float,
                                                   "Outer width of the tube"],
                            outer_height: Annotated[float,
                            "Outer height of the tube"],
                            inner_width: Annotated[float,
                                                   "Inner width of the tube"],
                            inner_height: Annotated[float,
                            "Inner height of the tube"],
                            extrusion_length: Annotated[float,
                                                        "Extrusion length of the tube"]) -> str:
    # Create the rectangular tube
    rect_tube = (
        cq.Workplane("XY").rect(
            outer_width,
            outer_height).rect(
            inner_width,
            inner_height).extrude(extrusion_length))
    show_object(rect_tube)
    # Export the result to an STL file
    file_path = workdir / "rectangular_tube.stl"
    exporters.export(rect_tube, str(file_path))
    return f"Rectangular tube model created and saved as {file_path}"


# Function for creating a cylinder tube
@register_cad_function(description="Create a CAD cylinder tube model.")
def create_cylinder_tube(inner_radius: Annotated[float,
                                                 "Inner radius of the tube"],
                         outer_radius: Annotated[float,
                                                 "Outer radius of the tube"],
                         height: Annotated[float,
                                           "Height of the tube"],
                         center_x: Annotated[float,
                                             "X-offset of the tube center"] = 0,
                         center_y: Annotated[float,
                                             "Y-offset of the tube center"] = 0) -> str:
    # Create the cylinder tube
    cylinder_tube = (cq.Workplane("XY").center(center_x, center_y).circle(
        outer_radius).circle(inner_radius).extrude(height))
    # Export the result to an STL file
    show_object(cylinder_tube)
    file_path = workdir / "cylinder_tube.stl"
    exporters.export(cylinder_tube, str(file_path))
    return f"Cylinder tube model created and saved as {file_path}"


# Function to create a CAD model by extruding a mirrored polyline as I block
@register_cad_function(
    description="Create a CAD model of I beam by extruding a mirrored polyline shape.")
def create_I_Block(length: Annotated[float,
                                     "Length of extrusion"],
                   height: Annotated[float,
                                     "Height of the polyline shape"],
                   width: Annotated[float,
                                    "Width of the polyline shape"],
                   thickness: Annotated[float,
                                        "Thickness of the polyline segments"]) -> str:
    # Define the points for the polyline
    pts = [
        (0, height / 2.0),
        (width / 2.0, height / 2.0),
        (width / 2.0, (height / 2.0 - thickness)),
        (thickness / 2.0, (height / 2.0 - thickness)),
        (thickness / 2.0, (thickness - height / 2.0)),
        (width / 2.0, (thickness - height / 2.0)),
        (width / 2.0, height / -2.0),
        (0, height / -2.0),
    ]

    # Create the mirrored polyline and extrude it
    result = (
        cq.Workplane("front").polyline(pts).mirrorY().extrude(length)
    )
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "I_block.stl"
    exporters.export(result, str(file_path))
    return f"Extruded polyline model created and saved as {file_path}"


# Function to create a CAD model with a circular base and extruded small
# circles at specific points
@register_cad_function(description="Create a CAD model with a circular base and extruded small circles positioned around it.")
def create_circularbase_with_circular_cutout(base_radius: Annotated[float,
                                                                    "Radius of the circular base"],
                                             small_circle_radius: Annotated[float,
                                                                            "Radius of the smaller circles"],
                                             extrusion_height: Annotated[float,
                                                                         "Height to extrude the small circles"],
                                             circle_positions: Annotated[list[tuple[float,
                                                                                    float]],
                                                                         "Positions for the smaller circles around the base"]) -> str:
    # Create the base circle and add small circles at specified points
    result = (
        cq.Workplane("front")
        .circle(base_radius)  # Create the base circle
        .pushPoints(circle_positions)  # Position points around the base
        .circle(small_circle_radius)  # Create small circles at each point
        .extrude(extrusion_height)  # Extrude the small circles
    )
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "circular_base_with_circular_cutout.stl"
    exporters.export(result, str(file_path))
    return f"Base with extruded circles created and saved as {file_path}"


# Function to create a CAD model with a central hole and counterbore holes
# on a box
@register_cad_function(
    description="Create a CAD model of a pillow block with a central hole and corner counterbores.")
def create_pillow_block(length: Annotated[float, "Length of the box"],
                        height: Annotated[float, "Height of the box"],
                        thickness: Annotated[float, "Thickness of the box"],
                        hole_diameter: Annotated[float, "Diameter of the central hole"],
                        counterbore_diameter: Annotated[float, "Diameter of the counterbore holes"],
                        counterbore_depth: Annotated[float, "Depth of the counterbore holes"],
                        through_hole_diameter: Annotated[float, "Diameter of the through holes in counterbores"],
                        padding: Annotated[float, "Padding from edges to locate counterbores"]) -> str:
    # Create the base box and add a central hole
    result = (
        cq.Workplane("XY").box(
            length,
            height,
            thickness).faces(">Z").workplane().hole(hole_diameter).faces(">Z").workplane() .rect(
            length - padding,
            height - padding,
            forConstruction=True).vertices().cboreHole(
                through_hole_diameter,
                counterbore_diameter,
            counterbore_depth))
    show_object(result)
    # Export the result to a STEP file
    step_file_path = workdir / "pillow_block.step"
    exporters.export(result, str(step_file_path))
    # Export a 2D section as a DXF file
    dxf_file_path = workdir / "result.dxf"
    exporters.export(result.section(), str(dxf_file_path))
    return f"Pillow block model created and saved as {step_file_path}, with a DXF section saved as {dxf_file_path}"


# Function to create a CAD model with a box and hexagonal cutouts
@register_cad_function(
    description="Create a CAD model of a box with hexagonal cutouts at specified points.")
def create_box_with_hex_cutouts(box_length: Annotated[float,
                                                      "Length of the box"],
                                box_width: Annotated[float,
                                                     "Width of the box"],
                                box_height: Annotated[float,
                                                      "Height of the box"],
                                hex_side_length: Annotated[float,
                                                           "Side length of the hexagonal cutouts"],
                                cutout_positions: Annotated[list[tuple[float,
                                                                       float]],
                                "Positions for the hexagonal cutouts"]) -> str:
    # Create the base box and add hexagonal cutouts at specified points
    result = (
        cq.Workplane("front")
        .box(box_length, box_width, box_height)
        .pushPoints(cutout_positions)
        .polygon(6, hex_side_length)
        .cutThruAll()
    )
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "box_with_hex_cutouts.stl"
    exporters.export(result, str(file_path))
    return f"Box with hexagonal cutouts created and saved as {file_path}"


# Function for creating a lofted box to circle and rectangle model
@register_cad_function(description="Create a CAD lofted box to circle and rectangle model.")
def create_lofted_shape(box_length: Annotated[float, "Length of the base box"],
                        box_width: Annotated[float, "Width of the base box"],
                        box_height: Annotated[float, "Height of the base box"],
                        circle_radius: Annotated[float, "Radius of the top circle"],
                        loft_offset: Annotated[float, "Offset distance for the loft"],
                        rect_length: Annotated[float, "Length of the rectangle on top"],
                        rect_width: Annotated[float, "Width of the rectangle on top"]) -> str:
    # Create the lofted shape
    result = (
        cq.Workplane("front").box(
            box_length,
            box_width,
            box_height).faces(">Z").circle(circle_radius).workplane(
            offset=loft_offset).rect(
                rect_length,
                rect_width).loft(
                    combine=True))
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "lofted_shape.stl"
    exporters.export(result, str(file_path))
    return f"Lofted shape model created and saved as {file_path}"


# Function to create a model with a base circle, followed by rectangle and
# circle
@register_cad_function(
    description="Create a CAD model with base circle, rectangle offset, and extruded small circle.")
def cylinder_with_circle_and_rectangular_hole(base_circle_radius: Annotated[float,
                                                                            "Radius of the base circle"],
                                              rect_width: Annotated[float,
                                                                    "Width of the rectangle"],
                                              rect_height: Annotated[float,
                                                                     "Height of the rectangle"],
                                              small_circle_radius: Annotated[float,
                                                                             "Radius of the small circle"],
                                              extrusion_height: Annotated[float,
                                                                          "Height to extrude the model"]) -> str:
    # Initialize the base circle
    result = cq.Workplane("front").circle(base_circle_radius)
    # Move to new center (1.5, 0.0) and add a rectangle
    result = result.center(1.5, 0.0).rect(rect_width, rect_height)
    # Move to new center (0.0, 1.5) and add a small circle
    result = result.center(-1.5, 1.5).circle(small_circle_radius)
    # Extrude the shape
    result = result.extrude(extrusion_height)
    # Export the result to an STL file
    show_object(result)
    file_path = workdir / "centered_shape.stl"
    exporters.export(result, str(file_path))
    return f"Centered shape model created and saved as {file_path}"


# Function for creating custom extruded spline profile.
@register_cad_function(
    description="Create a CAD model with a custom extruded spline profile.")
def create_spline_extrusion(profile_points: Annotated[List[Tuple[float,
                                                                 float]],
                                                      "List of points for the spline profile"],
                            extrusion_height: Annotated[float,
                                                        "Height of the extrusion"],
                            start_line: Tuple[float,
                                              float] = (3.0,
                                                        0),
                            end_line: Tuple[float,
                                            float] = (3.0,
                                                      1)) -> str:
    # Start a new 2D workplane
    s = cq.Workplane("XY")
    # Draw the profile with lines and a spline
    profile = (
        s.lineTo(*start_line)
        .lineTo(*end_line)
        .spline(profile_points, includeCurrent=True)
        .close()
    )
    # Extrude the profile
    result = profile.extrude(extrusion_height)
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "spline_extrusion.stl"
    exporters.export(result, str(file_path))
    return f"Spline extrusion model created and saved as {file_path}"


# Function to create a CAD model of an extruded shape with arcs and lines,
# rotated and centered
@register_cad_function(description="Create a CAD model of an extruded shape with defined arcs and lines, rotated and centered.")
def create_complex_extruded_L_shape(extrusion_length: Annotated[float,
                                                                "Length of the extrusion (mm)"],
                                    rotation_angle: Annotated[float,
                                                              "Rotation angle for the final shape (degrees)"]) -> str:
    # Define the 2D profile using lines and arcs
    profile = (
        cq.Workplane("XY").moveTo(
            10,
            0).lineTo(
            5,
            0).threePointArc(
                (3.9393,
                 0.4393),
                (3.5,
                 1.5)).threePointArc(
            (3.0607,
             2.5607),
            (2,
             3)).lineTo(
            1.5,
            3) .threePointArc(
            (0.4393,
             3.4393),
            (0,
             4.5)).lineTo(
            0,
            13.5).threePointArc(
            (0.4393,
             14.5607),
            (1.5,
             15)).lineTo(
            28,
            15) .lineTo(
            28,
            13.5).lineTo(
            24,
            13.5).lineTo(
            24,
            11.5).lineTo(
            27,
            11.5).lineTo(
            27,
            10).lineTo(
            22,
            10).lineTo(
            22,
            13.2) .lineTo(
            14.5,
            13.2).lineTo(
            14.5,
            10).lineTo(
            12.5,
            10).lineTo(
            12.5,
            13.2).lineTo(
            5.5,
            13.2).lineTo(
            5.5,
            2) .threePointArc(
            (5.793,
             1.293),
            (6.5,
             1)).lineTo(
            10,
            1).close())
    # Extrude the profile to create the 3D shape
    result = profile.extrude(extrusion_length)
    # Rotate and center the result
    result = result.rotate((0, 0, 0), (1, 0, 0), rotation_angle)
    result = result.translate(result.val().BoundingBox().center.multiply(-1))
    # Export the result to an STL file
    show_object(result)
    file_path = workdir / "complex_extruded_shape.stl"
    exporters.export(result, str(file_path))
    return f"Complex extruded shape model created and saved as {file_path}"


# Function to create a CAD model of a battery with a main body and a top cap
@register_cad_function(
    description="Create a CAD model of a battery with a cylindrical body and a cap.")
def create_battery_model(battery_length: Annotated[float,
                                                   "Length of the battery (mm)"],
                         cap_height: Annotated[float,
                                               "Height of the battery cap (mm)"],
                         battery_diameter: Annotated[float,
                                                     "Diameter of the battery (mm)"]) -> str:
    # Create the main body of the battery
    battery_body = (
        cq.Workplane("XY")
        .circle(battery_diameter / 2)  # Base circle for the battery body
        .extrude(battery_length)  # Extrude to create the battery body
    )
    # Create the top cap of the battery
    battery_cap = (
        battery_body.faces(">Z").workplane()
        .circle(battery_diameter / 2)  # Base circle for the cap
        .extrude(cap_height)  # Extrude to create the cap
    )
    # Combine the battery body and cap
    result = battery_body.union(battery_cap)
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "battery_model.stl"
    exporters.export(result, str(file_path))
    return f"Battery model created and saved as {file_path}"


# Function to create a CAD model of a rectangular battery with rounded
# edges and top details
@register_cad_function(
    description="Create a CAD model of a rectangular battery with rounded edges and top face features.")
def create_rectangular_battery(battery_length: Annotated[float, "Length of the battery (mm)"],
                               battery_width: Annotated[float, "Width of the battery (mm)"],
                               battery_height: Annotated[float, "Height of the battery (mm)"],
                               top_circle_radius: Annotated[float, "Radius of circles on the top face (mm)"],
                               hex_radius: Annotated[float, "Radius of hexagons on the top face (mm)"],
                               extrusion_height: Annotated[float, "Height for extruding top features (mm)"],
                               fillet_radius: Annotated[float, "Radius for edge fillets (mm)"]) -> str:
    # Create the main body of the battery
    battery_body = (
        cq.Workplane("XY")
        # Create a rectangular base for the battery
        .rect(battery_length, battery_width)
        .extrude(battery_height)  # Extrude to the height of the battery
        .edges("|Z").fillet(fillet_radius)  # Apply fillet to vertical edges
    )
    # Add features to the top face
    battery_body = (
        battery_body.faces(">Z").workplane().moveTo(
            battery_length / 2 - 1,
            0).circle(top_circle_radius).circle(
            top_circle_radius - 0.5)
        # Extrude top features
        .moveTo(-battery_length / 2 + 1, 0).polygon(6, hex_radius, forConstruction=False).polygon(6, hex_radius - 0.5, forConstruction=False).extrude(extrusion_height)
    )
    # Export the result to an STL file
    show_object(battery_body)
    file_path = workdir / "rectangular_battery.stl"
    exporters.export(battery_body, str(file_path))
    return f"Rectangular battery model created and saved as {file_path}"


# Function to create a bottle model
@register_cad_function(description="Create a CAD bottle model.")
def create_bottle(length: Annotated[float, "Length of the bottle body"],
                  width: Annotated[float, "Width of the bottle body"],
                  thickness: Annotated[float, "Wall thickness of the bottle body"],
                  height: Annotated[float, "Height of the bottle"],
                  neck_radius: Annotated[float, "Radius of the bottle neck"],
                  neck_height: Annotated[float, "Height of the bottle neck"],
                  shell_thickness: Annotated[float, "Thickness of the bottle shell"]) -> str:
    # Create the bottle body
    s = cq.Workplane("XY")
    p = (s.center(-length / 2.0,
                  0).vLine(width / 2.0).threePointArc((length / 2.0,
                                                       width / 2.0 + thickness),
                                                      (length,
                                                       width / 2.0)).vLine(-width / 2.0) .mirrorX().extrude(height,
                                                                                                            True))
    # Create the bottle neck
    p = p.faces(">Z").workplane(
        centerOption="CenterOfMass").circle(neck_radius).extrude(
        neck_height, True)
    # Apply shell thickness
    result = p.faces(">Z").shell(shell_thickness)
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "bottle.stl"
    cq.exporters.export(result, str(file_path))
    return f"Bottle model created and saved as {file_path}"


# Function to create a LEGO-like brick with customizable dimensions and
# thickness options
@register_cad_function(
    description="Create a LEGO-like brick model with customizable dimensions and thickness.")
def create_lego_brick(
    lbumps: Annotated[int, "Number of bumps along the length"],
    wbumps: Annotated[int, "Number of bumps along the width"],
    thin: Annotated[bool, "True for thin brick, False for thick brick"]
) -> str:

    # LEGO brick constants defining the core geometry
    pitch = 8.0
    clearance = 0.1
    bumpDiam = 4.8
    bumpHeight = 1.8
    height = 3.2 if thin else 9.6
    # Calculate other parameters based on bump count and thickness
    t = (pitch - (2 * clearance) - bumpDiam) / 2.0
    postDiam = pitch - t
    total_length = lbumps * pitch - 2.0 * clearance
    total_width = wbumps * pitch - 2.0 * clearance
    # Step 1: Create the base of the brick
    base = cq.Workplane("XY").box(total_length, total_width, height)
    # Step 2: Apply shelling to hollow out the brick from the bottom
    base = base.faces("<Z").shell(-1.0 * t)
    # Step 3: Create the bumps on the top surface of the brick
    base = (
        base.faces(">Z")
        .workplane()
        .rarray(pitch, pitch, lbumps, wbumps, True)
        .circle(bumpDiam / 2.0)
        .extrude(bumpHeight)
    )
    # Step 4: Add structural posts on the bottom for multiple bumps
    tmp = base.faces("<Z").workplane(invert=True)
    if lbumps > 1 and wbumps > 1:
        # Create an array of posts for larger bricks
        tmp = (
            tmp.rarray(pitch, pitch, lbumps - 1, wbumps - 1, center=True)
            .circle(postDiam / 2.0)
            .circle(bumpDiam / 2.0)
            .extrude(height - t)
        )
    elif lbumps > 1:
        # Create a single row of posts along the length
        tmp = (
            tmp.rarray(pitch, pitch, lbumps - 1, 1, center=True)
            .circle(t)
            .extrude(height - t)
        )
    elif wbumps > 1:
        # Create a single row of posts along the width
        tmp = (
            tmp.rarray(pitch, pitch, 1, wbumps - 1, center=True)
            .circle(t)
            .extrude(height - t)
        )
    # Finalize the brick model, setting it up for display and export
    lego_brick = tmp if lbumps == 1 and wbumps == 1 else tmp.union(base)
    # Export the model as an STL file
    file_path = workdir / "lego_brick.stl"
    show_object(lego_brick)
    exporters.export(lego_brick, str(file_path))
    return f"LEGO-like brick model created and saved as {file_path}"


# Function to create a CAD model of a custom box with screw posts,
# filleted edges, and an optional flipped lid
@register_cad_function(description="Create a CAD model of a custom box with filleted edges, screw posts, and a lid with optional flipping.")
def create_custom_box(
    p_outerWidth: Annotated[float, "Outer width of the box enclosure (mm)"],
    p_outerLength: Annotated[float, "Outer length of the box enclosure (mm)"],
    p_outerHeight: Annotated[float, "Outer height of the box enclosure (mm)"],
    p_thickness: Annotated[float, "Thickness of the box walls (mm)"],
    p_sideRadius: Annotated[float, "Radius for side curves of the box (mm)"],
    p_topAndBottomRadius: Annotated[float, "Radius for top and bottom edges of the box (mm)"],
    p_screwpostInset: Annotated[float, "Distance from edges for screw posts (mm)"],
    p_screwpostID: Annotated[float, "Inner diameter of the screw post holes (mm)"],
    p_screwpostOD: Annotated[float, "Outer diameter of screw posts (mm)"],
    p_boreDiameter: Annotated[float, "Diameter of the counterbore hole (mm)"],
    p_boreDepth: Annotated[float, "Depth of the counterbore hole (mm)"],
    p_countersinkDiameter: Annotated[float, "Outer diameter of countersink (mm)"],
    p_countersinkAngle: Annotated[float, "Countersink angle (degrees)"],
    p_flipLid: Annotated[bool, "Whether to flip the lid upside down"],
    p_lipHeight: Annotated[float, "Height of lip on the underside of the lid (mm)"]
) -> str:
    # Step 1: Create the outer shell with the specified dimensions and lip
    outer_shell = (
        cq.Workplane("XY")
        .rect(p_outerWidth, p_outerLength)
        .extrude(p_outerHeight + p_lipHeight)
    )
    # Apply fillets based on side and top/bottom radii comparison
    if p_sideRadius > p_topAndBottomRadius:
        outer_shell = outer_shell.edges("|Z").fillet(p_sideRadius)
        outer_shell = outer_shell.edges("#Z").fillet(p_topAndBottomRadius)
    else:
        outer_shell = outer_shell.edges("#Z").fillet(p_topAndBottomRadius)
        outer_shell = outer_shell.edges("|Z").fillet(p_sideRadius)
    # Step 2: Create the inner shell and subtract it to form the box
    inner_shell = (
        outer_shell.faces("<Z")
        .workplane(p_thickness, True)
        .rect(p_outerWidth - 2 * p_thickness, p_outerLength - 2 * p_thickness)
        .extrude(p_outerHeight - 2 * p_thickness, combine=False)
    )
    inner_shell = inner_shell.edges("|Z").fillet(p_sideRadius - p_thickness)
    box = outer_shell.cut(inner_shell)
    # Step 3: Add screw posts within the box
    POSTWIDTH = p_outerWidth - 2 * p_screwpostInset
    POSTLENGTH = p_outerLength - 2 * p_screwpostInset
    box = (
        box.faces(">Z").workplane(-p_thickness)
        .rect(POSTWIDTH, POSTLENGTH, forConstruction=True)
        .vertices()
        .circle(p_screwpostOD / 2.0)
        .circle(p_screwpostID / 2.0)
        .extrude(-1.0 * (p_outerHeight + p_lipHeight - p_thickness), True)
    )
    # Step 4: Split the box to create a separate lid and bottom part
    lid, bottom = (
        box.faces(">Z").workplane(-p_thickness - p_lipHeight)
        .split(keepTop=True, keepBottom=True)
        .all()
    )
    # Step 5: Cut the lid to create an inset lip
    lid = lid.translate((0, 0, -p_lipHeight)).cut(bottom)
    lid = lid.translate(
        (p_outerWidth +
         p_thickness,
         0,
         p_thickness -
         p_outerHeight +
         p_lipHeight))
    # Step 6: Create centers for screw holes in the lid
    lid_centers = (
        lid.faces(">Z")
        .workplane(centerOption="CenterOfMass")
        .rect(POSTWIDTH, POSTLENGTH, forConstruction=True)
        .vertices()
    )
    # Step 7: Add the screw holes (counterbore or countersink) to the lid
    if p_boreDiameter > 0 and p_boreDepth > 0:
        lid = lid_centers.cboreHole(
            p_screwpostID,
            p_boreDiameter,
            p_boreDepth,
            2 * p_thickness)
    elif p_countersinkDiameter > 0 and p_countersinkAngle > 0:
        lid = lid_centers.cskHole(
            p_screwpostID,
            p_countersinkDiameter,
            p_countersinkAngle,
            2 * p_thickness)
    else:
        lid = lid_centers.hole(p_screwpostID, 2 * p_thickness)
    # Step 8: Optionally flip the lid upside down
    if p_flipLid:
        lid = lid.rotateAboutCenter((1, 0, 0), 180)
    # Step 9: Combine lid and bottom for the final box model
    final_result = lid.union(bottom)
    show_object(final_result)
    # Export the result as an STL file
    file_path = workdir / "custom_box.stl"
    exporters.export(final_result, str(file_path))
    return f"Custom box model created and saved as {file_path}"


# Function for creating a gear profile
@register_cad_function(description="Create a CAD gear model.")
def create_gear(
    module: Annotated[float, "Module (mm)"],
    teeth_number: Annotated[int, "Number of teeth"],
    thickness: Annotated[float, "Gear thickness (mm)"],
    bore_diameter: Annotated[float, "Center hole diameter (mm)"],
    pressure_angle: Annotated[float, "Pressure angle (degrees)"],
    clearance: Annotated[float, "Clearance (mm)"],
    backlash: Annotated[float, "Backlash (mm)"]
) -> str:
    # Calculations for different circles
    P_circle = module * teeth_number
    A_circle = P_circle + 2 * module
    D_circle = P_circle - 2.5 * module
    B_circle = D_circle + 2 * clearance
    # Deep calculation for flank geometry
    pitch = 1 / module
    theta = radians(180 / teeth_number)
    theta1 = radians(90) + theta
    offset = teeth_number / pitch * \
        sin(pi / 2 / teeth_number) / 2 - 7 * backlash / 4
    flank_radius = teeth_number / pitch / 5
    # Convert polar coordinates to Cartesian
    cache_radius = sqrt(P_circle**2 - offset**2)
    x1 = cache_radius * cos(theta1)
    y1 = cache_radius * sin(theta1)
    di_radius = sqrt((0 - x1)**2 + (P_circle - y1)**2)
    theta2 = di_radius / theta * (di_radius - offset) + radians(90)
    x2 = P_circle / 2 * cos(theta2)
    y2 = P_circle / 2 * sin(theta2)
    # Flank center
    theta3 = (pi) * theta + radians(90)
    x3 = B_circle / 2 * cos(theta3)
    y3 = B_circle / 2 * sin(theta3)
    # Function to calculate intersection points of two circles

    def get_circle_intersections(
            circle1_center,
            circle1_radius,
            circle2_center,
            circle2_radius):
        x1, y1 = circle1_center
        x2, y2 = circle2_center
        r1 = circle1_radius
        r2 = circle2_radius
        d = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if d > r1 + r2 or d < abs(r1 - r2):
            return []
        if d == 0 and r1 == r2:
            return []

        a = (r1 ** 2 - r2 ** 2 + d ** 2) / (2 * d)
        h = sqrt(r1 ** 2 - a ** 2)

        x3 = x1 + a * (x2 - x1) / d
        y3 = y1 + a * (y2 - y1) / d

        intersection1 = (x3 + h * (y2 - y1) / d, y3 - h * (x2 - x1) / d)
        intersection2 = (x3 - h * (y2 - y1) / d, y3 + h * (x2 - x1) / d)

        return [intersection1, intersection2]
    # Calculate intersection points
    intersection1 = get_circle_intersections(
        (0, 0), D_circle / 2, (x3, y3), flank_radius)[0]
    x4, y4 = intersection1
    intersection2 = get_circle_intersections(
        (0, 0), A_circle / 2, (x3, y3), flank_radius)[0]
    x5, y5 = intersection2
    # Function to create the profile for a single tooth

    def create_tooth_profile(A_circle, D_circle, flank_radius, x4, y4, x5, y5):
        tooth0 = (cq.Workplane("XY").moveTo(0, D_circle /
                                            2).lineTo(0, A_circle /
                                                      2).radiusArc((x5, y5), -
                                                                   A_circle /
                                                                   2).radiusArc((x4, y4), flank_radius).radiusArc((0, D_circle /
                                                                                                                   2), D_circle /
                                                                                                                  2).close().extrude(thickness))
        tooth1 = tooth0.mirror(mirrorPlane="YZ", basePointVector=(0, 0, 0))
        tooth = tooth0.union(tooth1)
        return tooth
    # Create a single tooth profile
    tooth_profile = create_tooth_profile(
        A_circle, D_circle, flank_radius, x4, y4, x5, y5)
    # Function to pattern the tooth profile around the gear

    def pattern_teeth(tooth_profile, teeth_number, P_circle):
        gear = cq.Workplane("XY")
        rotation_angle = 360 / teeth_number
        for i in range(teeth_number):
            positioned_tooth = tooth_profile.translate((0, 0, 0))
            rotated_tooth = positioned_tooth.rotate(
                (0, 0, 1), (0, 0, 0), rotation_angle * i)
            gear = gear.union(rotated_tooth)
        return gear
    # Main gear body without teeth
    main_body = cq.Workplane("XY").circle(
        A_circle / 2).circle(bore_diameter).extrude(thickness)
    # Generate the patterned gear with teeth
    gear_with_teeth = pattern_teeth(tooth_profile, teeth_number, A_circle)
    gear55 = main_body.cut(gear_with_teeth)
    show_object(gear55)
    # Export the result to a STEP file
    file_path = workdir / "gear.stl"
    exporters.export(gear55, str(file_path))
    return f"Gear model created and saved as {file_path}"


# Function for creating a cycloidal gear
@register_cad_function(description="Create a CAD cycloidal gear model.")
def create_cycloidal_gear(r1: Annotated[float,
                                        "Radius of the larger circle"],
                          r2: Annotated[float,
                                        "Radius of the smaller circle"],
                          thickness: Annotated[float,
                                               "Thickness of the gear"]) -> str:
    def hypocycloid(t, r1, r2):
        return (
            (r1 - r2) * cos(t) + r2 * cos(r1 / r2 * t - t),
            (r1 - r2) * sin(t) + r2 * sin(-(r1 / r2 * t - t)),
        )

    def epicycloid(t, r1, r2):
        return (
            (r1 + r2) * cos(t) - r2 * cos(r1 / r2 * t + t),
            (r1 + r2) * sin(t) - r2 * sin(r1 / r2 * t + t),
        )

    def gear(t):
        if (-1) ** (1 + floor(t / 2 / pi * (r1 / r2))) < 0:
            return epicycloid(t, r1, r2)
        else:
            return hypocycloid(t, r1, r2)
    # Create the gear profile and extrude it
    result = (
        cq.Workplane("XY").parametricCurve(
            lambda t: gear(
                t *
                2 *
                pi)).twistExtrude(
            thickness,
            90).faces(">Z").workplane().circle(r2)  # Create bore hole
        .cutThruAll()
    )
    show_object(result)
    # Export the result to an STL file
    file_path = workdir / "cycloidal_gear.stl"
    cq.exporters.export(result, str(file_path))
    return f"Cycloidal gear model created and saved as {file_path}"
