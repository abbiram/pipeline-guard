import geopandas as gpd
from shapely.geometry import LineString, Point
from pyproj import Geod

def parse_coordinates(data):
    """
    Parse coordinates from the given data format into a list of tuples.
    """
    lines = data.strip().split("\n")
    coords = []
    for line in lines[1:]:  # Skip the header
        lon, lat = map(float, line.split(","))
        coords.append((lon, lat))
    return coords

def find_close_segments_and_intersections(powerline_coords, pipeline_coords, threshold=300):
    """
    Find pipeline segments near the powerline and intersection points, if any.
    
    Args:
        powerline_coords: List of (lon, lat) for the powerline.
        pipeline_coords: List of (lon, lat) for the pipeline.
        threshold: Distance threshold in meters.
    
    Returns:
        close_segments: List of pipeline segments within the threshold distance.
        intersections: List of intersection points between the pipeline and powerline.
    """
    geod = Geod(ellps="WGS84")  # Use WGS84 ellipsoid for geodesic calculations

    # Create GeoDataFrames
    powerline = LineString(powerline_coords)
    pipeline = LineString(pipeline_coords)

    # Intersection detection
    intersections = []
    if powerline.intersects(pipeline):
        intersection = powerline.intersection(pipeline)
        if intersection.geom_type == "Point":
            intersections.append((intersection.x, intersection.y))
        elif intersection.geom_type == "MultiPoint":
            intersections.extend([(point.x, point.y) for point in intersection])

    # Proximity detection
    close_segments = []
    for i in range(len(pipeline_coords) - 1):
        segment_start = pipeline_coords[i]
        segment_end = pipeline_coords[i + 1]

        # Compute midpoint and geodesic distance to powerline
        midpoint = ((segment_start[0] + segment_end[0]) / 2, (segment_start[1] + segment_end[1]) / 2)
        for j in range(len(powerline_coords) - 1):
            powerline_segment = LineString([powerline_coords[j], powerline_coords[j + 1]])
            dist = geod.geometry_length(LineString([midpoint, powerline_segment.centroid.coords[0]]))
            if dist <= threshold:
                close_segments.append((segment_start, segment_end))
                break  # Avoid duplicate checks for the same segment

    return close_segments, intersections

# Input data
powerline_data = """
Powerline
11.85432335293859,45.41057949009443
11.84814177213557,45.40345132008886
11.84533769593917,45.39998597542721
11.84268934929547,45.39598173417209
11.83976842989955,45.39155846670078
"""

pipeline_data = """
Pipeline
11.85932670013174,45.4093996339592
11.84433305811558,45.38861665858131
11.83680301015034,45.37862990508097
"""

# Parse coordinates
powerline_coords = parse_coordinates(powerline_data)
pipeline_coords = parse_coordinates(pipeline_data)

# Find close segments and intersections
threshold = 300  # Distance in meters
close_segments, intersections = find_close_segments_and_intersections(powerline_coords, pipeline_coords, threshold)

# Output results
print("Close Segments:", close_segments)
print("Intersection Points:", intersections)
