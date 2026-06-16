import math

class CandidateHeuristics:
    """
    Class Responsible for applying heuristics in the selection of candidate points to avoid spatial clustering.
    Currently implements an angular heuristic that ensures candidate points are separated by a minimum angle relative to the origin. Based on the Poisson Disk Sampling algorithm, but adapted for a geographic context.
    """

    def __init__(self, origin_lat: float, origin_lon: float, min_angle_degrees: float):
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        lat_rad = math.radians(self.origin_lat)
        self.lon_scale = math.cos(lat_rad)
        self.min_angle_rad = math.radians(min_angle_degrees)
        self.accepted_angles = []

    def _calculate_angle(self, lat: float, lon: float) -> float:
        """
        Calculates the angle (in radians) from the origin to a candidate point, accounting for longitude scaling.
        Args:
            lat (float): Latitude of the candidate point.
            lon (float): Longitude of the candidate point.
        Returns:
            float: The angle in radians from the origin to the candidate point.
        """
        delta_y = lat - self.origin_lat
        delta_x = (lon - self.origin_lon) * self.lon_scale
        return math.atan2(delta_y, delta_x)

    def _angular_distance(self, theta1: float, theta2: float) -> float:
        """
        Calculates the smallest angular distance between two angles, accounting for wrap-around at 360 degrees (2pi radians).
        Args:
            theta1 (float): First angle in radians.
            theta2 (float): Second angle in radians.
        Returns:
            float: The smallest angular distance in radians.
        """
        diff = abs(theta1 - theta2)
        return min(diff, 2 * math.pi - diff)

    def is_valid_candidate(self, lat: float, lon: float) -> bool:
        """
        Evaluates if a new candidate point respects the minimum angular distance
        with respect to all already accepted points.
        Args:
            lat (float): Latitude from the candidate point.
            lon (float): Longitude from the candidate point.
        Returns:
            bool: True if the candidate is valid (i.e., sufficiently separated from existing points), False otherwise.
        """
        new_angle = self._calculate_angle(lat, lon)

        if not self.accepted_angles:
            self.accepted_angles.append(new_angle)
            return True

        for accepted_angle in self.accepted_angles:
            if self._angular_distance(new_angle, accepted_angle) < self.min_angle_rad:
                return False
        
        self.accepted_angles.append(new_angle)
        return True
