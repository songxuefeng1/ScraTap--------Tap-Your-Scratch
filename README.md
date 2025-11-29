欢迎来到ScraTap!（Scratch Tap）
先运行scratchtap_compile.py文件，在内输入要解析的json文件路径（记住，这个json文件的全名一定要是main.st.json）
等待生成完成 xxx.s3exe（如果有错误，看一下main.st.josn是否出现语法错误（后续讲解ST（ScraTap）语法），或者其中"assests"的里面相对应的路径没有那个图片文件或文件不是图片类型）打开scratchtap_execute.py文件输入 xxx（这里是你的文件名）.s3exe 文件的路径

ST语法讲解（AI生成）：

ScratchTap（ScraTap）编程语言语法详解
ScratchTap 是一款结合 Scratch 可视化逻辑与 JSON 结构化配置的编程语言，通过定义角色、事件、指令和素材，最终编译为.s3exe可执行文件。其语法核心围绕JSON 配置文件展开，兼具结构化与易读性，以下是完整语法讲解：
一、文件结构
ScraTap 项目的核心是main.st.json文件，整体结构分为三大模块：
json
{
  "init": {},       // 项目初始化配置
  "custom-functions": {},  // 自定义函数（可选）
  "script": {}      // 角色脚本逻辑
}
二、1. 初始化配置（init）
定义项目元信息、素材映射和全局设置，必填字段：
字段	类型	说明
file-name	字符串	项目名称
super-speed-mode	布尔值	是否启用高速模式（影响运行帧率）
export-type	字符串	导出格式，固定为.s3exe
assets	对象	角色素材映射，键为角色名，值为素材文件路径（支持 PNG/JPG/SVG 等）
示例：
json
"init": {
  "file-name": "猫咪互动游戏",
  "super-speed-mode": false,
  "export-type": ".s3exe",
  "assets": {
    "角色1": "assets/cat.png",
    "背景": "assets/bg.jpg"
  }
}
三、2. 自定义函数（custom-functions，可选）
定义可复用的指令集合，通过函数名调用，适用于重复逻辑：
语法：
json
"custom-functions": {
  "函数名": [指令数组]
}
示例：
json
"custom-functions": {
  "旋转并移动": [
    { "spin-left": { "angle": 5 } },
    { "move-steps": { "steps": 10 } }
  ]
}
四、3. 脚本逻辑（script）
按角色组织交互逻辑，每个角色包含触发器和指令集，是 ScraTap 的核心部分。
3.1 角色定义
script的键为角色名（需与init.assets中的角色名对应），值为角色的行为配置：
json
"script": {
  "角色1": {
    "triggers": {},    // 事件触发器
    "指令集1": [],     // 具体执行的指令
    "指令集2": []
  }
}
3.2 触发器（triggers）
定义角色的触发事件，键为事件类型，值为要执行的指令集名称：
事件类型	说明
greenflag-clicked	绿旗被点击时触发
key-pressed	按键被按下时触发（需配合参数）
stage-clicked	舞台被点击时触发
role-clicked	角色被点击时触发
示例：
json
"triggers": {
  "greenflag-clicked": "主流程",
  "role-clicked": "角色被点击"
}
3.3 指令集
指令集是具体的操作序列，由多个指令对象组成，每个指令对象包含指令类型和参数。
3.3.1 基础指令类型
（1）运动指令
指令类型	参数	说明
move-to	position: {x, y}	移动到指定坐标（x/y 为整数）
spin-left	angle: 角度	向左旋转指定角度（0-360）
spin-right	angle: 角度	向右旋转指定角度
move-steps	steps: 步数	向前移动指定步数
示例：
json
[
  { "move-to": { "position": { "x": 50, "y": -20 } } },
  { "spin-left": { "angle": 10 } }
]
（2）控制指令
指令类型	参数	说明
infinite-loop	嵌套指令数组	无限循环执行嵌套指令
wait	seconds: 秒数	等待指定时间（浮点型）
call-function	name: 函数名	调用自定义函数
示例：
json
[
  { "infinite-loop": [
      { "spin-right": { "angle": 2 } },
      { "wait": { "seconds": 0.1 } }
    ]
  },
  { "call-function": { "name": "旋转并移动" } }
]
（3）交互指令
指令类型	参数	说明
user-input	prompt: 提示文本, var: 变量名	获取用户输入并存储到变量
say	text: 文本内容	输出文本（支持变量替换）
set-var	var: 变量名, value: 变量值	设置变量值
示例：
json
[
  { "user-input": { "prompt": "请输入你的名字：", "var": "username" } },
  { "say": { "text": "你好，${username}！" } },  // 变量替换用${变量名}
  { "set-var": { "var": "score", "value": "100" } }
]
3.3.2 指令嵌套
支持指令嵌套（如infinite-loop内嵌套其他指令），实现复杂逻辑：
json
[
  { "infinite-loop": [
      { "move-steps": { "steps": 5 } },
      { "wait": { "seconds": 0.2 } },
      { "if-touching": {       // 条件指令（扩展）
          "target": "边缘",
          "then": [ { "spin-right": { "angle": 90 } } ]
        }
      }
    ]
  }
]
五、变量系统
ScraTap 支持变量存储与使用，核心规则：
变量定义：通过user-input或set-var指令创建变量；
变量引用：在say等指令中用${变量名}引用；
变量作用域：全局生效，所有角色可访问。
六、完整示例
json
{
  "init": {
    "file-name": "欢迎程序",
    "super-speed-mode": false,
    "export-type": ".s3exe",
    "assets": { "机器人": "assets/robot.svg" }
  },
  "custom-functions": {
    "转圈": [
      { "spin-left": { "angle": 30 } },
      { "wait": { "seconds": 0.5 } }
    ]
  },
  "script": {
    "机器人": {
      "triggers": { "greenflag-clicked": "主流程" },
      "主流程": [
        { "user-input": { "prompt": "请输入你的名字：", "var": "name" } },
        { "say": { "text": "欢迎，${name}！我给你表演个转圈～" } },
        { "call-function": { "name": "转圈" } },
        { "infinite-loop": [
            { "move-steps": { "steps": 3 } },
            { "spin-right": { "angle": 1 } }
          ]
        }
      ]
    }
  }
}
七、语法规范
JSON 格式严格：需符合 JSON 语法，键名用双引号，逗号分隔，避免语法错误；
角色名一致：script中的角色名需与init.assets中的键完全匹配；
指令参数合法：如角度为 0-360 的整数，坐标范围通常为 - 240~240（对应舞台中心 ±240 像素）；
嵌套层级：指令嵌套建议不超过 5 层，避免逻辑混乱。
ScraTap 语法设计兼顾 Scratch 的易用性和 JSON 的结构化，适合可视化编程入门，同时支持扩展复杂逻辑，通过解析器编译为可执行文件后可跨平台运行。

