Welcome to ScraTap! (Scratch Tap) First, run the scratchtap_compile.py file, and enter the path of the JSON file to be parsed (remember, the full name of this JSON file must be main.st.json) Wait for the generation of xxx.s3exe to complete (if there is an error, check whether there is a syntax error in main.st.json (ST (ScraTap) syntax will be explained later), or whether the corresponding path in "assets" does not have that image file or the file is not an image type) Open the scratchtap_execute.py file and enter the path of the xxx (your file name).s3exe file ST Syntax Explanation (AI Generated): ScratchTap (ScraTap) Programming Language Syntax Details ScratchTap is a programming language that combines Scratch's visual logic with JSON structured configuration. By defining characters, events, instructions, and resources, it can eventually be compiled into a .s3exe executable file. Its syntax core revolves around the JSON configuration file, combining structure and readability. Here is the complete syntax explanation: 1. File Structure The core of a ScraTap project is the main.st.json file, which is divided into three main modules: json {"init": {}, // Project initialization configuration "custom-functions": {}, // Custom functions (optional) "script": {} // Character script logic } 2. Initialization Configuration (init) Defines project metadata, resource mapping and global settings. Required fields: Field Type Description file-name String Project name super-speed-mode Boolean Whether to enable high-speed mode (affects frame rate) export-type String Export format, fixed as .s3exe assets Object Character resource mapping, key is character name, value is the path to the resource file (supports PNG/JPG/SVG etc.) Example: json "init": {"file-name": "Cat Interactive Game", "super-speed-mode": false, "export-type": ".s3exe", "assets": {"Character1": "assets/cat.png", "Background": "assets/bg.jpg"} } 3. Custom Functions (custom-functions, optional) Defines reusable sets of instructions that can be called by function name, suitable for repeating logic: Syntax: json
"custom-functions": {{ "FunctionName": [InstructionArray] } Example: json "custom-functions": { "rotate-and-move": [ { "spin-left": { "angle": 5 } }, { "move-steps": { "steps": 10 } } ] } IV. 3. Script Logic (script) Organize interactive logic by roles. Each role contains triggers and instruction sets, which is the core part of ScraTap. 3.1 Role Definition The key of script is the role name (must correspond to the role name in init.assets), and the value is the behavior configuration of the role: json "script": { "Role1": { "triggers": {}, // Event triggers "InstructionSet1": [], // Instructions to execute "InstructionSet2": [] } } 3.2 Triggers (triggers) Define the events that a role can trigger. The key is the event type, and the value is the name of the instruction set to execute: Event Type Description greenflag-clicked Triggered when the green flag is clicked key-pressed Triggered when a key is pressed (requires parameters) stage-clicked Triggered when the stage is clicked role-clicked Triggered when the role is clicked Example: json "triggers": { "greenflag-clicked": "main-flow", "role-clicked": "role-clicked-action" } 3.3 Instruction Sets Instruction sets are specific sequences of operations, composed of multiple instruction objects, with each instruction object containing the instruction type and parameters. 3.3.1 Basic Instruction Types (1) Motion Instructions Instruction Type Parameters Description move-to position: {x, y} Move to specified coordinates (x/y are integers) spin-left angle: degrees Rotate left by the specified angle (0-360) spin-right angle: degrees Rotate right by the specified angle move-steps steps: number of steps Move forward by the specified number of steps Example: json [ { "move-to": { "position": { "x": 50, "y": -20 } } }, { "spin-left": { "angle": 10 } } ] (2) Control Instructions Instruction Type Parameters Description infinite-loop nested instructions array Execute nested instructions in an infinite loop wait seconds: number of seconds Wait for the specified time (float) call-function name: function name Call a custom function Example: json [ { "infinite-loop": [ { "spin-right": { "angle": 2 } }, { "wait": { "seconds": 0.1 } } ] }, { "call-function": { "name": "RotateAndMove" } } ]

(3) Interactive Commands

| Command Type | Parameters | Description |
|--------------|------------|-------------|
| user-input   | prompt: prompt text, var: variable name | Get user input and store it in a variable |
| say          | text: content | Output text (supports variable substitution) |
| set-var      | var: variable name, value: variable value | Set a variable's value |

Example:
json [
  { "user-input": { "prompt": "Please enter your name:", "var": "username" } },
  { "say": { "text": "Hello, ${username}!" } },  // Use ${variableName} for variable substitution
  { "set-var": { "var": "score", "value": "100" } }
]

3.3.2 Nested Commands
Supports command nesting (such as embedding other commands within an infinite-loop) to implement complex logic:
json [
  {
    "infinite-loop": [
      { "move-steps": { "steps": 5 } },
      { "wait": { "seconds": 0.2 } },
      { "if-touching": { // Conditional command (extension)
          "target": "edge",
          "then": [
            { "spin-right": { "angle": 90 } }
          ]
        }
      }
    ]
  }
]

5. Variable System
ScraTap supports variable storage and usage. Core rules:
- Variable Definition: Create variables via user-input or set-var commands;
- Variable Reference: Use ${variableName} in commands such as say;
- Variable Scope: Global, accessible by all characters.

6. Complete Example
json {
  "init": {
    "file-name": "WelcomeProgram",
    "super-speed-mode": false,
    "export-type": ".s3exe",
    "assets": {
      "Robot": "assets/robot.svg"
    }
  },
  "custom-functions": {
    "RotateInCircle": [ { "spin-left": { "angle" } }
  }
}
