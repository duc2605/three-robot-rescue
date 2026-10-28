from setuptools import find_packages, setup

package_name = 'social_navigation_planner'

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
    maintainer='long',
    maintainer_email='long@todo.todo',
    description='Three-robot D* Lite/MPC formation navigation and comparative paper backends',
    license='LicenseRef-Not-Specified',
    extras_require={
        'test': [
            'pytest',
        ],
    },
   entry_points={
    'console_scripts': [
        'paper1_controller = social_navigation_planner.paper1_gwo_woa_node:main',
        'paper2_controller = social_navigation_planner.paper2_apf_mpc_node:main',
        'three_robot_dstar_mpc = social_navigation_planner.dstar_mpc_controller:main',
        'robot_distributed_mpc = social_navigation_planner.dstar_mpc_controller:robot_mpc_main',
    ],
},
)
