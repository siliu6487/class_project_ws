![Overview](Project_Overview.png)

# 1. Instructions for building and launching
check system_commands.md for instructions [https://github.com/siliu6487/class_project_ws/blob/main/system_commands.md]

# 2. Links
1. MoieIt!: src/kinova_manipulation [https://github.com/siliu6487/class_project_ws/tree/main/src/kinova_manipulation]
2. Nav2: src/turtlebot_nav [https://github.com/siliu6487/class_project_ws/tree/main/src/turtlebot_nav]
3. Perception: src/perception_module [https://github.com/siliu6487/class_project_ws/tree/main/src/perception_module]
4. Custom component: src/demo_system.ipynb [https://github.com/siliu6487/class_project_ws/blob/main/src/demo_system.ipynb]
5. hand-writted node: src/perception_module/perception_module/perception_service.py [https://github.com/siliu6487/class_project_ws/blob/main/src/perception_module/perception_module/perception_service.py]


# 3. Project Overview
This project demonstrates an LLM-powered tabletop object fetching and delivery system using a Kinova arm, TurtleBot2, MoveIt2, Nav2, and perception modules:

**User command → LLM plan → MoveIt2 action → audio/image sensing → perception result → decision loop**


The system takes a user command such as:

- “Give me an empty bottle”

- “Fetch me the cup with pens”

An LLM running through Ollama parses the command and generates a simple task plan, such as:

```json

{

  "object": "bottle",

  "property": "empty",

  "action": "shake and listen"

}
```
Based on the object type, the robot chooses an interactive sensing action:

* Bottle → shake and listen (can't see what's inside a bottle)
* Cup → tilt and look (pens will fall of the cup if it's shaken)
s
The Kinova arm uses MoveIt2 and predefined trajectories to reach the object, grasp it, perform the selected interaction, and return to a holding pose. The perception client then processes recorded sensing data to determine whether the object has the requested property.
After the system confirms that the current object is what the user required, the arm drops the object to the TurtleBot to deliver to the user.

### Notes on Implementation Scope

The submitted demo focuses on the main required system behaviors:

* MoveIt2 manipulation with the Kinova arm
* Nav2 navigation with TurtleBot2
* LLM-based high-level decision making using Ollama
* Meaningful perception through audio classification and vision-based color blob detection
* Closed-loop sensing, perception, and action

Some parts are simplified for reliability and safety:

* Object detection (bottle vs. cup) and 3D localization are skipped.
* Grasp poses are preset.
* Objects are manually placed or switched before interactions.
* The real arm-to-TurtleBot drop-off is not included because the arm reach was insufficient and caused unstable motion near the table edge.
