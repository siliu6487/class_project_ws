from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'ros2_class_project'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),

    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Launch files
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.py')),

        # Config files
        (os.path.join('share', package_name, 'config'),
         glob('config/*.yaml')),

        # RIVZ setting
        (os.path.join('share', package_name, 'config'),
         glob('config/*.rviz')),

        # Map files
        (os.path.join('share', package_name, 'maps'),
         glob('maps/*')),
    ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bee-humble',
    maintainer_email='bee-humble@todo.todo',
    description='ROS2 class project',
    license='TODO: License declaration',

    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'test_node = ros2_class_project.test_node:main',
            'test_nav_sequence = ros2_class_project.test_nav_sequence:main',
        ],
    },
)