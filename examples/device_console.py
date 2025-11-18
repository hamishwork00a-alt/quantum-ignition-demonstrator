"""
設備控制台 - 交互式控制界面
"""

import cmd
from quantum_light_controller import *

class LightSourceConsole(cmd.Cmd):
    """光源控制台"""
    
    intro = "🎛️ 量子預火光源控制台 (輸入 help 查看命令)"
    prompt = "光源> "
    
    def __init__(self):
        super().__init__()
        self.light_source = None
        self._initialize_system()
    
    def _initialize_system(self):
        """初始化系統"""
        config = LightSourceConfig()
        self.light_source = QuantumLightSourceController(config)
        
        # 設置回調
        self.light_source.register_callback('state_change', self._on_state_change)
        self.light_source.register_callback('power_update', self._on_power_update)
    
    def _on_state_change(self, data):
        """狀態變化回調"""
        print(f"\n[系統] 狀態變化: {data['old_state']} → {data['new_state']}")
    
    def _on_power_update(self, power):
        """功率更新回調"""
        print(f"\n[系統] 功率更新: {power:.3e}W")
    
    def do_power_on(self, arg):
        """開啟光源: power_on"""
        if self.light_source.power_on():
            print("✅ 光源已開啟")
        else:
            print("❌ 開啟失敗")
    
    def do_power_off(self, arg):
        """關閉光源: power_off"""
        self.light_source.power_off()
        print("✅ 光源已關閉")
    
    def do_calibrate(self, arg):
        """執行校準: calibrate"""
        if self.light_source.calibrate():
            print("✅ 校準完成")
        else:
            print("❌ 校準失敗")
    
    def do_start(self, arg):
        """開始發射: start <功率> <時長>
        示例: start 2.5e-9 5.0"""
        try:
            args = arg.split()
            if len(args) < 2:
                print("❌ 用法: start <功率> <時長>")
                return
            
            power = float(args[0])
            duration = float(args[1])
            
            params = EmissionParameters(power=power, duration=duration)
            
            if self.light_source.start_emission(params):
                print(f"✅ 開始發射: {power:.3e}W, {duration}秒")
            else:
                print("❌ 發射失敗")
                
        except ValueError:
            print("❌ 參數格式錯誤")
    
    def do_stop(self, arg):
        """停止發射: stop"""
        self.light_source.stop_emission()
        print("✅ 發射已停止")
    
    def do_set_power(self, arg):
        """設置功率: set_power <功率>
        示例: set_power 3.0e-9"""
        try:
            power = float(arg)
            if self.light_source.set_power(power):
                print(f"✅ 功率設置為: {power:.3e}W")
            else:
                print("❌ 功率設置失敗")
        except ValueError:
            print("❌ 功率格式錯誤")
    
    def do_status(self, arg):
        """查看狀態: status"""
        status = self.light_source.get_status()
        print("\n📊 系統狀態:")
        print(f"  狀態: {status['state']}")
        print(f"  功率: {status['current_power']:.3e}W")
        print(f"  波長: {status['wavelength']*1e9:.1f}nm")
        print(f"  運行時間: {status['operating_time']:.1f}s")
        
        print("\n🔧 子系統狀態:")
        for subsystem, substatus in status['subsystem_status'].items():
            print(f"  {subsystem}: {substatus}")
    
    def do_exit(self, arg):
        """退出控制台: exit"""
        print("👋 再見!")
        return True

if __name__ == "__main__":
    LightSourceConsole().cmdloop()
