1. setting goal pose: use it to get inital pose
rame:map, Position(-0.459849, 1.35869, 0), Orientation(0, 0, 0.321688, 0.946846) = Angle: 0.655023

ros2 topic pub --once /initialpose geometry_msgs/PoseWithCovarianceStamped \
"{header: {stamp: {sec: 0, nanosec: 0}, frame_id: 'map'}, pose: {pose: {position: {x: -0.459849, y: 1.35869, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.321688, w: 0.946846}}, covariance: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5]}}"

local cost map is way off