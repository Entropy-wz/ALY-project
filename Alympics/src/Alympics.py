
import json
import os
import time
import openai

class PlayGround:
    def __init__(self) -> None:
        self.players = []
        self.game_setting = ""
        self.history = [] # Historical Records
        self.game_setting = []# Game Setting

    def add_player(self, new_player):
        self.players.append(new_player)

class Player:
    def __init__(self, name, if_persona, persona):
        self.name = name
        self.if_persona = if_persona # Persona Setting
        self.persona = persona
        self.llm = None
        self.player_status = {} # Player Status
        self.history = [] # Memory Cache
        self.reasoning = None # Reasoning Plugin
        self.other_components = None # Other Components

    def append_message(self, role, content):
        self.history.append({"role": role, "content": content})

class LLM:
    def __init__(self, engine=None, temperature=0.7, sleep_time=2) -> None:
        # ==================== 配置区域 ====================
        
        openai.api_base = "https://api.chatanywhere.tech/v1"
        
        openai.api_key = "sk-CAD4iMgGyj1cJi8ts6Zz1Essy6H6Ctwl5pIsM3mzPwJvtc1X" 

        # 如果外部没有指定模型，就默认使用 gpt-4o-mini
        self.engine = "gpt-4o-mini" if not engine else engine

        # 清理旧的 Azure 设置 (防止报错)
        openai.api_type = "open_ai"
        openai.api_version = None
        
        # ================================================

        self.temperature = temperature
        self.sleep_time = sleep_time
    
    def call(self, message):
        status = 0
        retries = 0
        while status != 1:
            try:
                # 调用接口
                response = openai.ChatCompletion.create(
                        model=self.engine,  # 关键修改：Azure用engine，这里改成标准model
                        messages=message,
                        temperature=self.temperature,
                        max_tokens=800,
                        top_p=0.95,
                        frequency_penalty=0,
                        presence_penalty=0,
                        stop=None)
                
                RESPONSE = response['choices'][0]['message']['content']
                status = 1
                time.sleep(self.sleep_time) # 避免请求太快
            except Exception as e:
                retries += 1
                print(f"请求失败 (重试 {retries}): {e}")
                time.sleep(5)
                
                # 如果重试超过5次还在报错，可以选择跳出（防止死循环）
                if retries > 5:
                    print("重试次数过多，停止尝试。")
                    return "Error: API call failed"
                    
        return RESPONSE
    

