from setuptools import find_packages, setup

package_name = 'behaviour_trees'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools','py-trees','py-trees-ros','py-trees-ros-interfaces','rclpy'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='saleeqmohammed7@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['main_planner = behaviour_trees.main_planner:main'
        ],
    },
)
