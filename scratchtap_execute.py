import struct
import pygame
import os
from pathlib import Path

class ScraTapRuntime:
    def __init__(self, s3exe_path):
        self.s3exe_path = Path(s3exe_path).resolve()
        self.assets = {}
        self.bytecode = b''
        self.roles = {}
        self.variables = {}
        self.running = False

        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((480, 360))
        pygame.display.set_caption("ScraTap Runtime")
        self.clock = pygame.time.Clock()

    def load_s3exe(self):
        """加载并解析.s3exe文件"""
        if not self.s3exe_path.exists():
            raise FileNotFoundError(f"文件不存在：{self.s3exe_path}")

        with open(self.s3exe_path, "rb") as f:
            # 验证文件头
            header = f.read(8)
            if header != b'SCRATAP\x02':
                raise ValueError("不支持的文件格式或版本！")
            
            # 读取素材
            asset_count = struct.unpack('!I', f.read(4))[0]
            for _ in range(asset_count):
                role_len = struct.unpack('!H', f.read(2))[0]
                role_name = f.read(role_len).decode("utf-8")
                path_len = struct.unpack('!H', f.read(2))[0]
                path = f.read(path_len).decode("utf-8")
                data_len = struct.unpack('!I', f.read(4))[0]
                data = f.read(data_len)

                # 加载素材
                self.assets[role_name] = self._load_asset(data, path)
                # 初始化角色状态
                self.roles[role_name] = {
                    "x": 0, "y": 0, "angle": 0, "visible": True,
                    "costume": self.assets[role_name]
                }
            
            # 读取字节码
            bytecode_len = struct.unpack('!I', f.read(4))[0]
            self.bytecode = f.read(bytecode_len)

        print(f"✅ 成功加载：{self.s3exe_path}")
        print(f"🎭 角色数量：{len(self.roles)}")
        print(f"📜 字节码长度：{len(self.bytecode)} bytes")

    def _load_asset(self, data, path):
        """加载素材（支持PNG/JPG/SVG占位）"""
        from io import BytesIO
        try:
            return pygame.image.load(BytesIO(data)).convert_alpha()
        except:
            # SVG或其他格式：返回占位图
            surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 0, 0), (25, 25), 25)
            return surf

    def execute(self):
        """执行字节码逻辑"""
        self.running = True
        ptr = 0
        while ptr < len(self.bytecode) and self.running:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # 读取触发器
            trigger_op = self.bytecode[ptr]
            ptr += 1

            # 绿旗点击触发器（默认触发）
            if trigger_op == 0x01:
                ptr = self._execute_instructions(ptr)

            # 渲染画面
            self._render()
            self.clock.tick(30)

    def _execute_instructions(self, ptr):
        """递归执行指令"""
        while ptr < len(self.bytecode) and self.running:
            inst_op = self.bytecode[ptr]
            ptr += 1

            # 运动指令
            if inst_op == 0x10:  # move-to
                x = struct.unpack('!h', self.bytecode[ptr:ptr+2])[0]
                y = struct.unpack('!h', self.bytecode[ptr+2:ptr+4])[0]
                ptr += 4
                self.roles["角色1"]["x"] = x
                self.roles["角色1"]["y"] = y
                print(f"[角色1] 移动到 ({x}, {y})")

            elif inst_op == 0x11:  # spin-left
                angle = struct.unpack('!B', self.bytecode[ptr:ptr+1])[0]
                ptr += 1
                self.roles["角色1"]["angle"] += angle
                print(f"[角色1] 左转 {angle}°（当前：{self.roles['角色1']['angle']}°）")

            elif inst_op == 0x12:  # spin-right
                angle = struct.unpack('!B', self.bytecode[ptr:ptr+1])[0]
                ptr += 1
                self.roles["角色1"]["angle"] -= angle
                print(f"[角色1] 右转 {angle}°（当前：{self.roles['角色1']['angle']}°）")

            # 控制指令
            elif inst_op == 0x20:  # infinite-loop
                loop_ptr = ptr
                while self.running:
                    ptr = self._execute_instructions(loop_ptr)

            elif inst_op == 0x21:  # wait
                seconds = struct.unpack('!f', self.bytecode[ptr:ptr+4])[0]
                ptr += 4
                pygame.time.wait(int(seconds * 1000))

            # 交互指令
            elif inst_op == 0x30:  # user-input
                prompt_len = struct.unpack('!H', self.bytecode[ptr:ptr+2])[0]
                ptr += 2
                prompt = self.bytecode[ptr:ptr+prompt_len].decode("utf-8")
                ptr += prompt_len

                var_len = struct.unpack('!H', self.bytecode[ptr:ptr+2])[0]
                ptr += 2
                var_name = self.bytecode[ptr:ptr+var_len].decode("utf-8")
                ptr += var_len

                # 获取用户输入
                user_input = input(f"\n📝 {prompt} ")
                self.variables[var_name] = user_input
                print(f"💾 变量 {var_name} = {user_input}")

            elif inst_op == 0x31:  # say
                text_len = struct.unpack('!H', self.bytecode[ptr:ptr+2])[0]
                ptr += 2
                text = self.bytecode[ptr:ptr+text_len].decode("utf-8")
                ptr += text_len

                # 变量替换（${var}）
                for var_name, value in self.variables.items():
                    text = text.replace(f"${{{var_name}}}", value)
                print(f"🗣️  {text}")

            # 变量指令
            elif inst_op == 0x40:  # set-var
                var_len = struct.unpack('!H', self.bytecode[ptr:ptr+2])[0]
                ptr += 2
                var_name = self.bytecode[ptr:ptr+var_len].decode("utf-8")
                ptr += var_len

                val_len = struct.unpack('!H', self.bytecode[ptr:ptr+2])[0]
                ptr += 2
                value = self.bytecode[ptr:ptr+val_len].decode("utf-8")
                ptr += val_len

                self.variables[var_name] = value
                print(f"🔧 设置变量 {var_name} = {value}")

            # 未知指令
            else:
                break

        return ptr

    def _render(self):
        """渲染游戏画面"""
        self.screen.fill((255, 255, 255))

        # 绘制所有角色
        for role in self.roles.values():
            if role["visible"]:
                # 旋转角色
                rotated = pygame.transform.rotate(role["costume"], role["angle"])
                rect = rotated.get_rect(
                    center=(role["x"] + 240, role["y"] + 180)  # 中心偏移
                )
                self.screen.blit(rotated, rect)

        pygame.display.flip()

    def run(self):
        """启动运行时"""
        try:
            self.load_s3exe()
            print("\n▶️  启动ScraTap运行时（按窗口关闭按钮退出）...\n")
            self.execute()
        except Exception as e:
            print(f"\n❌ 运行失败：{e}")
        finally:
            pygame.quit()

# 交互式运行时
if __name__ == "__main__":
    print("=== ScraTap 运行时 v2 ===")
    while True:
        s3exe_path = input("请输入要运行的.s3exe文件路径：").strip()
        if not os.path.exists(s3exe_path):
            print("错误：文件不存在！")
        else:
            break

    runtime = ScraTapRuntime(s3exe_path)
    runtime.run()