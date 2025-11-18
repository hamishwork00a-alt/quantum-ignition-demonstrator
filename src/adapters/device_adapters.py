"""
設備通信適配器
支持多種工業設備接口協議
"""

import abc
import serial
import socket
from typing import Dict, Any
import json

class DeviceAdapter(abc.ABC):
    """設備適配器抽象基類"""
    
    @abc.abstractmethod
    def connect(self) -> bool:
        pass
    
    @abc.abstractmethod
    def disconnect(self):
        pass
    
    @abc.abstractmethod
    def send_command(self, command: str, parameters: Dict) -> Dict:
        pass
    
    @abc.abstractmethod
    def read_status(self) -> Dict:
        pass

class EthernetAdapter(DeviceAdapter):
    """以太網設備適配器"""
    
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"以太網連接失敗: {e}")
            return False
    
    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.connected = False
    
    def send_command(self, command: str, parameters: Dict) -> Dict:
        if not self.connected:
            return {"error": "設備未連接"}
        
        try:
            # 構造命令消息
            message = {
                "command": command,
                "parameters": parameters,
                "timestamp": time.time()
            }
            
            # 發送JSON格式命令
            message_str = json.dumps(message) + "\n"
            self.socket.send(message_str.encode())
            
            # 接收響應
            response = self.socket.recv(1024).decode().strip()
            return json.loads(response)
            
        except Exception as e:
            return {"error": f"命令發送失敗: {e}"}
    
    def read_status(self) -> Dict:
        return self.send_command("read_status", {})

class SerialAdapter(DeviceAdapter):
    """串口設備適配器"""
    
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.connected = False
    
    def connect(self) -> bool:
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"串口連接失敗: {e}")
            return False
    
    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected = False
    
    def send_command(self, command: str, parameters: Dict) -> Dict:
        if not self.connected:
            return {"error": "設備未連接"}
        
        try:
            # 簡單的命令協議
            command_str = f"{command}:{json.dumps(parameters)}\r\n"
            self.serial.write(command_str.encode())
            
            # 讀取響應
            response = self.serial.readline().decode().strip()
            return json.loads(response)
            
        except Exception as e:
            return {"error": f"命令發送失敗: {e}"}
    
    def read_status(self) -> Dict:
        return self.send_command("STATUS", {})

class ModbusTCPAdapter(DeviceAdapter):
    """Modbus TCP適配器 (工業標準協議)"""
    
    def __init__(self, host: str, port: int = 502):
        self.host = host
        self.port = port
        self.connected = False
    
    def connect(self) -> bool:
        # 實際實現會使用pymodbus等庫
        self.connected = True
        return True
    
    def disconnect(self):
        self.connected = False
    
    def send_command(self, command: str, parameters: Dict) -> Dict:
        if not self.connected:
            return {"error": "設備未連接"}
        
        # Modbus協議實現
        return {"status": "success", "protocol": "modbus_tcp"}
    
    def read_status(self) -> Dict:
        # 讀取保持寄存器等
        return {"voltage": 220, "current": 1.5, "temperature": 25.5}

class DeviceManager:
    """設備管理器 - 統一管理多種設備接口"""
    
    def __init__(self):
        self.adapters = {}
        self.device_configs = {}
    
    def register_device(self, device_id: str, adapter: DeviceAdapter, config: Dict):
        """註冊設備"""
        self.adapters[device_id] = adapter
        self.device_configs[device_id] = config
    
    def connect_all(self) -> Dict[str, bool]:
        """連接所有設備"""
        results = {}
        for device_id, adapter in self.adapters.items():
            results[device_id] = adapter.connect()
        return results
    
    def send_to_device(self, device_id: str, command: str, params: Dict) -> Dict:
        """向指定設備發送命令"""
        if device_id not in self.adapters:
            return {"error": f"設備未註冊: {device_id}"}
        
        adapter = self.adapters[device_id]
        return adapter.send_command(command, params)
    
    def broadcast_command(self, command: str, params: Dict) -> Dict[str, Dict]:
        """廣播命令到所有設備"""
        results = {}
        for device_id in self.adapters:
            results[device_id] = self.send_to_device(device_id, command, params)
        return results
    
    def get_system_status(self) -> Dict:
        """獲取系統所有設備狀態"""
        status = {}
        for device_id, adapter in self.adapters.items():
            status[device_id] = {
                "connected": adapter.connected,
                "status": adapter.read_status(),
                "config": self.device_configs[device_id]
            }
        return status
