# What's Barbell

You may have heard of [Gym](https://gym.openai.com/), the toolkit for developing and comparing reinforcement learning algorithms. Gym provides a set of episodic scenarios, called _environments_, with which the reinforcement learning agent must interact. As reinforcement learning algorithms evolve, however, the scenarios on which they are applied must evolve too. Gym provides a set of tools to develop scenarios, but the documentation on these tools is poor and, should physics engines be used in the scenario, they must be included and controlled manually. This is the gap that Barbell tries to fill. It provides a framework to generate Gym scenarios in a quick and simple way. It provides a language to describe objects, that can later be rendered/represented in one of the available game/physics engines provided by Barbell.  


# Getting started

To install Barbell, execute
```
pip install barbell
```

then run 
```
barbell init
```
follow the instructions to create an environment under the form of a Python package. Then, objects in the scenario can be created by either using a high-level descriptive language to define them or the APIs of the different game/physics engines provided by Barbell can be called directly.   

# License
[GPL](https://github.com/oprometeumoderno/barbell/blob/master/LICENSE)

