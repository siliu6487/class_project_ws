from setuptools import find_packages, setup

package_name = 'kinova_manipulation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bee-humble',
    maintainer_email='siliu64cs@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'calibrate_camera = kinova_manipulation.calibrate_camera:main',
            'test_click_transform = kinova_manipulation.test_click_transform:main',
            'test_cam_arm_tf = kinova_manipulation.test_cam_arm_tf:main',
            'joy_teleop = kinova_manipulation.joy_teleop:main',
            'add_table_collision = kinova_manipulation.add_table_collision:main',
        ],
    },
)
