your_project/
├── scenes/
│   └── pick_place_scene.ttt                # 🏗️ Your CoppeliaSim scene
│
├── robot/
│   └── zmq_client.py                       # 🔌 Interface to CoppeliaSim (ZeroMQ)
│   └── robot_interface.py                  # 🦾 High-level robot API: pick, place, etc.
│
├── state/
│   └── scene_state.py                      # 🌍 SceneState class (current state abstraction)
│   └── slot_config.py                      # 📍 Hardcoded coordinates for shop & goal slots
│
├── behaviors/
│   └── pick.py                             # 🧠 BT node: Pick object
│   └── place.py                            # 🧠 BT node: Place object
│   └── detect_objects.py                   # 🧠 BT node: update SceneState
│   └── explore.py                          # 🧠 BT node: Do random action
│   └── check_goal.py                       # ✅ BT condition: goal complete?
│   └── chance_node.py                      # 🎲 BT decorator: epsilon-greedy selector
│
├── rl/
│   └── transition_logger.py                # 📘 Logs (state, action, reward, next_state)
│   └── reward_function.py                  # 💰 Reward logic (customizable)
│   └── action_space.py                     # 🧭 Discrete/parametric action representations
│   └── dataset/                            # 📂 Where transitions get stored (pickle/json/etc)
│       └── episode_00001.json
│
├── trees/
│   └── pick_place_tree.py                  # 🌳 Full behavior tree composition
│
├── utils/
│   └── geometry.py                         # 📐 Vector math, distance, etc
│   └── timer.py                            # ⏱️ For tick timing, optional
│
├── main.py                                 # 🚀 Main entry point (run BT loop)
├── requirements.txt                        # 📦 Python dependencies
└── README.md                               # 📄 Project summary
