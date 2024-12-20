import geopandas as gpd
from shapely.geometry import LineString, Point, MultiPoint
from pyproj import Geod
import matplotlib.pyplot as plt

def parse_coordinates_from_file(filepath):
    """Parse coordinates from a file into a list of tuples."""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None  # Or raise an exception, depending on desired behavior
    
    coords = []
    for line in lines[1:]:  # Skip the header
        try:
            lon, lat = map(float, line.split(","))
            coords.append((lon, lat))
        except ValueError:  # Handle potential errors in data format
            print(f"Skipping invalid line: {line.strip()}") # Alert user to bad lines
            continue # Keep going in case of bad lines
    return coords

def find_close_segments_and_intersections(powerline_coords, pipeline_coords, threshold=300):
    """Find pipeline segments near the powerline and intersection points."""

    geod = Geod(ellps="WGS84")

    powerline = LineString(powerline_coords)
    pipeline = LineString(pipeline_coords)

    intersections = []
    intersection = powerline.intersection(pipeline) # Get the intersection (can be complex)
    if intersection.is_empty:
        pass # No intersection, do nothing
    elif intersection.geom_type == "Point":
        intersections.append((intersection.x, intersection.y))
    elif intersection.geom_type == "MultiPoint": # Handle multiple intersections
        intersections.extend([(point.x, point.y) for point in intersection])
    else: # Handle GeometryCollection (lines or more complex intersections)
        for geom in intersection:
            if geom.geom_type == "Point":
                intersections.append((geom.x, geom.y))

    close_segments = []
    for i in range(len(pipeline_coords) - 1):
        segment_start = pipeline_coords[i]
        segment_end = pipeline_coords[i + 1]
        segment = LineString([segment_start, segment_end])

        for j in range(len(powerline_coords) - 1):
            powerline_segment = LineString([powerline_coords[j], powerline_coords[j+1]])
            min_dist = float('inf') # Start with a very large distance
            for k in range(10): # Check multiple points along the segment
                frac = k/10.0
                point = segment.interpolate(frac, normalized=True)
                dist = powerline_segment.distance(point)
                min_dist = min(min_dist, dist)

            if min_dist * 100000 <= threshold: # Convert to meters
                close_segments.append((segment_start, segment_end))
                break


    return close_segments, intersections


# --- Visualization ---
def visualize_results(powerline_coords, pipeline_coords, close_segments, intersections):
    """Visualizes the powerline, pipeline, close segments, and intersections."""

    # Create GeoDataFrames for plotting
    powerline_gdf = gpd.GeoDataFrame({'geometry': [LineString(powerline_coords)]})
    pipeline_gdf = gpd.GeoDataFrame({'geometry': [LineString(pipeline_coords)]})

    # Create a GeoDataFrame for close segments
    close_segments_gdf = gpd.GeoDataFrame({'geometry': [LineString(segment) for segment in close_segments]})

    # Create a GeoDataFrame for intersection points
    intersection_points_gdf = gpd.GeoDataFrame({'geometry': [Point(point) for point in intersections]})


    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8))

    powerline_gdf.plot(ax=ax, color='red', label='Powerline')
    pipeline_gdf.plot(ax=ax, color='blue', label='Pipeline')
    close_segments_gdf.plot(ax=ax, color='green', linewidth=2, label='Close Segments')
    intersection_points_gdf.plot(ax=ax, color='black', markersize=50, marker='x', label='Intersections')


    plt.title("Powerline and Pipeline Analysis")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.show()




# --- Example usage with files (including visualization) ---
powerline_filepath = "powerline.csv"  # Or use your larger test case files
pipeline_filepath = "pipeline.csv"

powerline_coords = parse_coordinates_from_file(powerline_filepath)
pipeline_coords = parse_coordinates_from_file(pipeline_filepath)

if powerline_coords and pipeline_coords:
    close_segments, intersections = find_close_segments_and_intersections(powerline_coords, pipeline_coords)
    print("Close Segments:", close_segments)
    print("Intersection Points:", intersections)

    visualize_results(powerline_coords, pipeline_coords, close_segments, intersections) # Call visualization function

else:
    print("Error: Could not read coordinate data from one or both files.")
