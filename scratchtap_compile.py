import json
import os
import struct
from pathlib import Path

class ScraTapParser:
    def __init__(self, project_path):
        self.project_path = Path(project_path).resolve()
        self.json_data = self._load_json()
        self.assets = {}
        self.bytecode = b''

    def _load_json(self):
        """加载并验证ScraTap项目文件"""
        json_path = self.project_path / "main.st.json"
        if not json_path.exists():
            raise FileNotFoundError(f"项目文件不存在：{json_path}")
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 必要字段校验
        required = ["init", "script"]
        for field in required:
            if field not in data:
                raise ValueError(f"项目文件缺少必要字段：{field}")
        return data

    def _pack_assets(self):
        """打包素材为二进制"""
        assets_config = self.json_data["init"].get("assets", {})
        for role_name, asset_path in assets_config.items():
            full_path = self.project_path / asset_path
            if not full_path.exists():
                raise FileNotFoundError(f"素材文件不存在：{full_path}")
            
            with open(full_path, "rb") as f:
                self.assets[role_name] = {
                    "path": asset_path,
                    "data": f.read()
                }

    def _compile_script(self):
        """编译角色脚本为字节码"""
        script_data = self.json_data["script"]
        for role_name, role_script in script_data.items():
            # 处理触发器绑定
            triggers = role_script.get("triggers", {})
            for trigger, process_name in triggers.items():
                self.bytecode += self._encode_trigger(trigger)
                # 编译进程逻辑
                process_logic = role_script.get(process_name, [])
                self.bytecode += self._compile_instructions(process_logic)

    def _encode_trigger(self, trigger):
        """触发器编码"""
        trigger_map = {
            "greenflag-clicked": b'\x01',
            "key-pressed": b'\x02',
            "stage-clicked": b'\x03'
        }
        return trigger_map.get(trigger, b'\x00')

    def _compile_instructions(self, instructions):
        """递归编译指令（支持嵌套）"""
        inst_bytecode = b''
        for inst in instructions:
            for inst_type, params in inst.items():
                # 指令操作码
                inst_bytecode += self._get_inst_opcode(inst_type)
                # 参数编码
                inst_bytecode += self._encode_params(inst_type, params)
                # 处理嵌套指令（如循环内的指令）
                if isinstance(params, list):
                    inst_bytecode += self._compile_instructions(params)
        return inst_bytecode

    def _get_inst_opcode(self, inst_type):
        """指令操作码映射"""
        opcode_map = {
            # 运动指令
            "move-to": b'\x10',
            "spin-left": b'\x11',
            "spin-right": b'\x12',
            # 控制指令
            "infinite-loop": b'\x20',
            "wait": b'\x21',
            # 交互指令
            "user-input": b'\x30',
            "say": b'\x31',
            # 变量指令
            "set-var": b'\x40'
        }
        return opcode_map.get(inst_type, b'\x00')

    def _encode_params(self, inst_type, params):
        """参数编码"""
        param_bytes = b''
        if inst_type == "move-to":
            x = params["position"]["x"]
            y = params["position"]["y"]
            param_bytes += struct.pack('!h', x) + struct.pack('!h', y)
        elif inst_type == "spin-left" or inst_type == "spin-right":
            angle = params["angle"]
            param_bytes += struct.pack('!B', angle)
        elif inst_type == "wait":
            seconds = params["seconds"]
            param_bytes += struct.pack('!f', seconds)
        elif inst_type == "user-input":
            prompt = params["prompt"].encode("utf-8")
            var_name = params["var"].encode("utf-8")
            param_bytes += struct.pack('!H', len(prompt)) + prompt
            param_bytes += struct.pack('!H', len(var_name)) + var_name
        elif inst_type == "say":
            text = params["text"].encode("utf-8")
            param_bytes += struct.pack('!H', len(text)) + text
        elif inst_type == "set-var":
            var_name = params["var"].encode("utf-8")
            value = params["value"].encode("utf-8")
            param_bytes += struct.pack('!H', len(var_name)) + var_name
            param_bytes += struct.pack('!H', len(value)) + value
        return param_bytes

    def generate_s3exe(self, output_path=None):
        """生成.s3exe文件（支持用户输入路径）"""
        # 获取输出路径
        if not output_path:
            while True:
                output_path = input("请输入目标.s3exe文件路径（如：./output.s3exe）：").strip()
                if not output_path.endswith(".s3exe"):
                    print("错误：文件必须以.s3exe为后缀！")
                elif os.path.exists(output_path):
                    if input(f"文件 {output_path} 已存在，是否覆盖？(y/n)").lower() != "y":
                        output_path = None
                    else:
                        break
                else:
                    break

        output_path = Path(output_path).resolve()

        # 打包素材+编译脚本
        self._pack_assets()
        self._compile_script()

        # 写入.s3exe文件
        with open(output_path, "wb") as f:
            # 文件头（版本2）
            f.write(b'SCRATAP\x02')
            # 素材数据
            f.write(struct.pack('!I', len(self.assets)))
            for role_name, asset in self.assets.items():
                # 角色名
                role_bytes = role_name.encode("utf-8")
                f.write(struct.pack('!H', len(role_bytes)) + role_bytes)
                # 素材路径
                path_bytes = asset["path"].encode("utf-8")
                f.write(struct.pack('!H', len(path_bytes)) + path_bytes)
                # 素材数据
                f.write(struct.pack('!I', len(asset["data"])) + asset["data"])
            # 脚本字节码
            f.write(struct.pack('!I', len(self.bytecode)) + self.bytecode)

        print(f"\n✅ 成功生成.s3exe文件：{output_path}")
        return output_path

# 交互式运行解析器
if __name__ == "__main__":
    print("=== ScraTap 解析器 v2 ===")
    # 用户输入项目路径
    while True:
        project_path = input("请输入ScraTap项目路径（存放main.st.json的文件夹）：").strip()
        if not os.path.exists(project_path):
            print("错误：项目路径不存在！")
        else:
            break

    try:
        parser = ScraTapParser(project_path)
        parser.generate_s3exe()
    except Exception as e:
        print(f"\n❌ 编译失败：{e}")