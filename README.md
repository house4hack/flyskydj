# Code and presentation for talk at PyConZa 2019
[![Talk Teaser](http://img.youtube.com/vi/QT3D1Bvv6F4/0.jpg)](http://www.youtube.com/watch?v=QT3D1Bvv6F4 "Edge Computing at the Edge of the World")

## Summary
Well, to be more accurate, running a context-aware machine learning based music recommendation system using Python on an embedded processor integrated into a RC remote control on mountains around South Africa. The context is generated by sensors on a 1.2 m home-built slope glider, processed on the plane using Python, running on an even smaller embedded board built into the plane (was also thinking about 'Snakes on a plane' as a title) and being transmitted down to the music player while flying.

The music recommendation uses reinforcement learning to map the current flying-style features (e.g. fast-and-reckless vs slow-and-relaxed) at time of recommendation to songs on an SD card. Songs are processed offline into mel-spectograms, features extracted using a convolutional neural network (VGG16) via Keras and then clustered into folders of similar songs. The mapping of flying style to folders are discovered through reinforcement from skips or listens.

The purpose of the talk is to introduce the audience to CircuitPython (a flavour of Python for microcontrollers), song feature extraction using convnets and reinforcement learning based context aware realtime music recommendation. The audience for this would be Python enthusiasts, data scientist, tinkerers, those interested in edge computing and anyone frustrated with the lack of context aware music players (especially when flying their RC slope gliders). The entire project with code, Jupyter notebook and videos with the system in action will be made available on Github.
