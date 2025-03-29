import pcl
import pye57
from pathlib import Path
import numpy as np
import pye57.e57

# Function to convert e57 to ply
def convert_e57_to_ply(input_e57_file:Path, output_ply_file:Path) -> None:
    """ Converts e57 file format to ply

    Args:
        input_e57_file (_type_): file path to e57 file 
        output_ply_file (_type_): output path to ply file 
    """
    # Read .e57 file
    reader = pye57.E57(input_e57_file)
    point_cloud_data = reader.get_points()  # get points from e57
    
    # Convert to numpy array (x, y, z)
    points = np.array([(point[0], point[1], point[2]) for point in point_cloud_data])

    # Create pcl point cloud object
    cloud = pcl.PointCloud()
    cloud.from_array(points.astype(np.float32))

    # Save the cloud as a .ply file
    pcl.save(cloud, output_ply_file)