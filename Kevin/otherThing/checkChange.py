import Rhino
import scriptcontext as sc

# Ensure we're using the Rhino document, not Grasshopper's
sc.doc = Rhino.RhinoDoc.ActiveDoc

# Lists to store points and curves
points = []
curves = []

for obj in objInput:  # Assuming 'x' is your input parameter
    # Find the Rhino object corresponding to the GUID
    rh_obj = sc.doc.Objects.Find(obj)
    if rh_obj:
        # Check if the object is a point
        if isinstance(rh_obj.Geometry, Rhino.Geometry.Point):
            points.append(obj)
        # Check if the object is a curve
        elif isinstance(rh_obj.Geometry, Rhino.Geometry.Curve):
            curves.append(obj)


# Function to store initial locations
def store_initial_point_data(objs):
    for obj in objs:
        # Get the object's Rhino document object
        rh_obj = sc.doc.Objects.Find(obj)
        if rh_obj and rh_obj.Geometry:
            # Store the initial location (for point objects, use the Location property)
            print(rh_obj.Geometry.Location)
            initial_point_data[obj] = (rh_obj.Geometry.Location, False)

# Function to store initial curve data
def store_initial_curve_data(curve_guids):
    print("curve work")
    for guid in curve_guids:
        curve_obj = sc.doc.Objects.Find(guid)
        if curve_obj and isinstance(curve_obj.Geometry, Rhino.Geometry.Curve):
            # Extract and store the curve's control points or vertices
            curve = curve_obj.Geometry
            control_points = [pt.Location for pt in curve.ToNurbsCurve().Points]
            initial_curve_data[guid] = (control_points, False, curve)


# Function to check if objects have moved
def have_points_moved(objs):
    moved_objects = []
    for obj in objs:
        rh_obj = sc.doc.Objects.Find(obj)
        if rh_obj and rh_obj.Geometry:
            current_data = rh_obj.Geometry.Location
            initial_data = initial_point_data.get(obj)[0]
            
            if current_data != initial_data:
                moved_objects.append(current_data)
                initial_point_data[obj] = (current_data, True)
            else:
                initial_point_data[obj] = (initial_data, False)

    return moved_objects

# Function to determine if curves have moved
def have_curves_moved(curve_guids):
    moved_curves = []
    for guid in curve_guids:
        curve_obj = sc.doc.Objects.Find(guid)
        if curve_obj and isinstance(curve_obj.Geometry, Rhino.Geometry.Curve):
            current_curve = curve_obj.Geometry
            current_control_points = [pt.Location for pt in current_curve.ToNurbsCurve().Points]
            initial_control_points = initial_curve_data.get(guid)[0]

            # Check if the set of control points has changed
            if any(pt1 != pt2 for pt1, pt2 in zip(current_control_points, initial_control_points)):
                moved_curves.append(guid)
                initial_curve_data[guid] = (current_control_points, True, current_curve)
            else:
                initial_curve_data[guid] = (initial_control_points, False, current_curve)

    return moved_curves

def show(input, type):
    show_pt = []
    show_pt_bool = []
    show_crv = []
    show_crv_bool = []
    if type == "point":
        for guid in input:
            pt, ptBool = initial_point_data[guid]
            show_pt.append(pt)
            show_pt_bool.append(ptBool)
        return (show_pt, show_pt_bool)
    elif type == "curve":
        for guid in input:
            crvPt, crvBool, crv = initial_curve_data[guid]
            show_crv.append(crv)
            show_crv_bool.append(crvBool)
        return (show_crv, show_crv_bool)
    
    else:
        return "none"


if init:
    initial_point_data = {}
    initial_curve_data = {}


try:
    # Call this function to check for moved objects
    moved_guids_points = have_points_moved(points)
    moved_guids_curves = have_curves_moved(curves)
    a = moved_guids_points
    b = moved_guids_curves
    
except:
    initial_point_data = {}
    initial_curve_data = {}
    store_initial_point_data(points)
    store_initial_curve_data(curves)
    moved_guids_points = have_points_moved(points)
    moved_guids_curves = have_curves_moved(curves)
    a = moved_guids_points
    b = moved_guids_curves
    
outPt, outPtBool = show(initial_point_data, "point")
outCrv, outCrvBool = show(initial_curve_data, "curve")
    