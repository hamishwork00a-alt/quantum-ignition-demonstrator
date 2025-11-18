"""
半導體光刻系統演示 - 完整單文件示例
展示量子預火光源在實際設備中的應用
"""

import time
import threading
from typing import Dict, List
from quantum_light_controller import *

class SemiconductorLithographySystem:
    """
    半導體光刻系統
    完整的光刻生產線集成示例
    """
    
    def __init__(self):
        # 光源配置
        self.light_source_config = LightSourceConfig(
            wavelength=5.8e-9,
            max_power=5.0e-9,
            stability_target=0.005,
            warmup_time=10.0  # 演示用較短預熱時間
        )
        
        # 初始化控制器
        self.light_source = QuantumLightSourceController(self.light_source_config)
        
        # 設備管理
        self.device_manager = DeviceManager()
        
        # 生產狀態
        self.production_state = "IDLE"
        self.current_recipe = None
        self.wafer_count = 0
        
        # 設置回調
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """設置系統回調"""
        self.light_source.register_callback('state_change', self._on_light_source_state_change)
        self.light_source.register_callback('power_update', self._on_power_update)
        self.light_source.register_callback('error', self._on_error)
    
    def initialize_system(self) -> bool:
        """初始化系統"""
        print("🔄 初始化半導體光刻系統...")
        
        try:
            # 1. 初始化設備
            if not self._initialize_devices():
                return False
            
            # 2. 啟動光源
            if not self.light_source.power_on():
                return False
            
            # 3. 系統校準
            if not self.light_source.calibrate():
                return False
            
            print("✅ 光刻系統初始化完成")
            self.production_state = "READY"
            return True
            
        except Exception as e:
            print(f"❌ 系統初始化失敗: {e}")
            return False
    
    def _initialize_devices(self) -> bool:
        """初始化設備"""
        # 註冊設備
        devices = {
            "stage_controller": EthernetAdapter("192.168.1.10", 8080),
            "mask_aligner": EthernetAdapter("192.168.1.11", 8080),
            "vacuum_system": EthernetAdapter("192.168.1.12", 8080),
        }
        
        for device_id, adapter in devices.items():
            self.device_manager.register_device(device_id, adapter)
        
        # 連接設備
        results = self.device_manager.connect_all()
        
        for device_id, connected in results.items():
            status = "✅" if connected else "❌"
            print(f"{status} {device_id}: {'連接成功' if connected else '連接失敗'}")
        
        return all(results.values())
    
    def load_recipe(self, recipe: Dict) -> bool:
        """加載光刻配方"""
        print(f"📁 加載光刻配方: {recipe.get('name', '未知')}")
        
        if not self._validate_recipe(recipe):
            return False
        
        self.current_recipe = recipe
        print("✅ 配方加載完成")
        return True
    
    def start_exposure(self, wafer_id: str) -> bool:
        """開始晶圓曝光"""
        if self.production_state != "READY":
            print("❌ 系統未就緒")
            return False
        
        if not self.current_recipe:
            print("❌ 未加載配方")
            return False
        
        print(f"🚀 開始晶圓曝光: {wafer_id}")
        self.production_state = "EXPOSING"
        
        try:
            # 1. 移動晶圓
            self._move_wafer_to_position(wafer_id)
            
            # 2. 啟動光源
            exposure_params = self._get_exposure_parameters()
            if not self.light_source.start_emission(exposure_params):
                return False
            
            # 3. 執行曝光
            self._execute_exposure_sequence()
            
            # 4. 完成曝光
            self.light_source.stop_emission()
            self._move_wafer_to_unload()
            
            self.wafer_count += 1
            self.production_state = "READY"
            
            print(f"✅ 晶圓曝光完成: {wafer_id} (總計: {self.wafer_count})")
            return True
            
        except Exception as e:
            print(f"❌ 曝光失敗: {e}")
            self.production_state = "ERROR"
            return False
    
    def batch_process(self, wafer_list: List[str]) -> Dict:
        """批量處理"""
        print(f"🏭 批量處理 {len(wafer_list)} 個晶圓")
        
        results = {
            "total": len(wafer_list),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for i, wafer_id in enumerate(wafer_list, 1):
            print(f"\n--- 進度: {i}/{len(wafer_list)} ---")
            
            start_time = time.time()
            success = self.start_exposure(wafer_id)
            process_time = time.time() - start_time
            
            result = {
                "wafer_id": wafer_id,
                "success": success,
                "process_time": process_time
            }
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append(result)
        
        print(f"\n🎉 批量完成: {results['success']} 成功, {results['failed']} 失敗")
        return results
    
    def emergency_stop(self):
        """緊急停止"""
        print("🛑 緊急停止!")
        self.light_source.stop_emission()
        self.production_state = "EMERGENCY"
    
    def get_system_status(self) -> Dict:
        """獲取系統狀態"""
        light_status = self.light_source.get_status()
        
        return {
            "production_state": self.production_state,
            "wafer_count": self.wafer_count,
            "current_recipe": self.current_recipe,
            "light_source": light_status
        }
    
    def _validate_recipe(self, recipe: Dict) -> bool:
        """驗證配方"""
        required = ["name", "exposure_time", "light_source"]
        for field in required:
            if field not in recipe:
                print(f"❌ 缺少字段: {field}")
                return False
        return True
    
    def _move_wafer_to_position(self, wafer_id: str):
        """移動晶圓"""
        print(f"📦 移動晶圓 {wafer_id} 到曝光位置")
        time.sleep(0.5)
    
    def _get_exposure_parameters(self) -> EmissionParameters:
        """獲取曝光參數"""
        recipe_light = self.current_recipe.get("light_source", {})
        
        return EmissionParameters(
            power=recipe_light.get("power", 3.0e-9),
            duration=self.current_recipe.get("exposure_time", 5.0),
            frequency=recipe_light.get("frequency", 1000),
            duty_cycle=recipe_light.get("duty_cycle", 0.5),
            mode=OutputMode.PULSED
        )
    
    def _execute_exposure_sequence(self):
        """執行曝光序列"""
        exposure_time = self.current_recipe.get("exposure_time", 5.0)
        
        print(f"⏱ 曝光中... 時長: {exposure_time}秒")
        
        start_time = time.time()
        while time.time() - start_time < exposure_time:
            elapsed = time.time() - start_time
            progress = min(elapsed / exposure_time, 1.0)
            
            if progress % 0.2 < 0.01:
                print(f"📊 進度: {progress*100:.1f}%")
            
            time.sleep(0.1)
    
    def _move_wafer_to_unload(self):
        """移動晶圓到卸載"""
        print("📤 移動晶圓到卸載位置")
        time.sleep(0.3)
    
    def _on_light_source_state_change(self, data):
        """光源狀態回調"""
        print(f"💡 光源狀態: {data['old_state']} → {data['new_state']}")
    
    def _on_power_update(self, power):
        """功率回調"""
        print(f"⚡ 功率更新: {power:.3e}W")
    
    def _on_error(self, error_data):
        """錯誤回調"""
        print(f"🚨 系統錯誤: {error_data}")

def demo_lithography_system():
    """演示光刻系統"""
    print("=" * 50)
    print("🏭 半導體光刻系統演示")
    print("=" * 50)
    
    # 創建系統
    litho_system = SemiconductorLithographySystem()
    
    # 初始化
    if not litho_system.initialize_system():
        return
    
    # 加載配方
    recipe = {
        "name": "5nm EUV 工藝",
        "exposure_time": 6.0,
        "light_source": {
            "power": 3.5e-9,
            "frequency": 2000,
            "duty_cycle": 0.6
        }
    }
    
    if not litho_system.load_recipe(recipe):
        return
    
    # 處理晶圓
    wafers = [f"Wafer_{i:03d}" for i in range(1, 4)]
    results = litho_system.batch_process(wafers)
    
    # 顯示結果
    print("\n" + "=" * 50)
    print("📊 生產報告")
    print("=" * 50)
    print(f"總處理: {results['total']}")
    print(f"成功: {results['success']}")
    print(f"失敗: {results['failed']}")
    
    # 系統狀態
    status = litho_system.get_system_status()
    print(f"\n🔧 系統狀態: {status['production_state']}")
    print(f"📦 已處理: {status['wafer_count']}")
    
    # 關閉系統
    litho_system.light_source.power_off()
    print("\n✅ 演示完成")

if __name__ == "__main__":
    demo_lithography_system()
