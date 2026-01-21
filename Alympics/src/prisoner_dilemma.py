import time
import json
import itertools 

from Alympics import LLM, Player 

# ==================== 1. 定义囚徒玩家类 ====================
class PDPersonaPlayer(Player):
    def __init__(self, name, persona, engine):
        # 初始化父类 (对应 Alympics.py 中的 Player.__init__)
        # 参数顺序: name, if_persona, persona
        super().__init__(name, False, persona) 
        self.engine = engine
        self.hp = 10 # 初始血量
        
        # 定义系统提示词
        self.SYSTEM_PROMPT = f"""
You are {name}, a resident in a drought-stricken town.
{persona}

[Game Rules - The Water Truce]
You are playing a game against another resident. Every day, you must choose one of two actions:
1. 'Cooperate': Try to share water resources peacefully.
2. 'Defect': Try to steal all the water for yourself.

[Payoff Matrix (HP Changes)]
- If BOTH Cooperate: Both gain +2 HP (Water shared).
- If YOU Defect and THEY Cooperate: You gain +4 HP (You steal it all), They lose 2 HP.
- If YOU Cooperate and THEY Defect: You lose 2 HP (They steal it all), They gain +4 HP.
- If BOTH Defect: Both lose 1 HP (Conflict wastes water).

Your Goal: Maximize your own HP survival.
"""

    def make_choice(self, round_num, opponent_name, history_str):
        # 构建这一轮的提示词
        prompt = f"""
{self.SYSTEM_PROMPT}

[Current Status]
Round: {round_num}
Your HP: {self.hp}
Opponent: {opponent_name}
History of previous rounds:
{history_str}

[Decision]
Based on your personality and the history, choose your action for today.
You must strictly output ONLY one word: "Cooperate" or "Defect".
Do not output anything else.
"""
        messages = [{"role": "system", "content": prompt}]
        
        try:
            llm_client = LLM(engine=self.engine)
            response = llm_client.call(messages)
            
            # 清洗结果
            action = response.strip().replace(".", "").replace('"', "").replace("'", "")
            
            if "defect" in action.lower():
                return "Defect"
            elif "cooperate" in action.lower():
                return "Cooperate"
            else:
                return "Cooperate"
        except Exception as e:
            print(f"Error in LLM call for {self.name}: {e}")
            return "Cooperate"

# ==================== 2. 定义锦标赛逻辑 ====================
def run_tournament():
    print(">>> 🏆 W镇生存大乱斗循环赛开始！<<<")
    print(">>> 规则：所有选手两两对决，每场打 5 轮。")
    
    engine_name = "gpt-4o-mini" 

    # --- 选手介绍 ---
    # 1. Alex: 普通好人
    alex = PDPersonaPlayer(
        name="Alex", 
        persona="You are kind, naive, and believe in the goodness of humanity. You prefer to work together.", 
        engine=engine_name
    )
    # 2. Bob: 自私鬼
    bob = PDPersonaPlayer(
        name="Bob", 
        persona="You are selfish, cunning, and ruthless. You only care about your own survival and will exploit others if profitable.", 
        engine=engine_name
    )
    # 3. Charlie: 记仇者
    charlie = PDPersonaPlayer(
        name="Charlie",
        persona="You are principled. You start with Cooperate. However, if anyone betrays you (Defect) even ONCE, you will hold a grudge forever and will NEVER cooperate with them again.",
        engine=engine_name
    )
    # 4. David: 疯帽子
    david = PDPersonaPlayer(
        name="David",
        persona="You are chaotic and unpredictable. You don't care about logic. You flip a coin in your mind every time. Sometimes you cooperate, sometimes you defect, randomly.",
        engine=engine_name
    )
    # 5. Eric: 精算师
    eric = PDPersonaPlayer(
        name="Eric",
        persona="You are a cunning strategist. You test your opponent. If they are weak, you Defect. If they are strong/retaliatory, you Cooperate to cut losses.",
        engine=engine_name
    )
    # 6. Fiona: 圣母
    fiona = PDPersonaPlayer(
        name="Fiona",
        persona="You are a saint. You believe love conquers all. Even if others hurt you, you ALWAYS choose Cooperate.",
        engine=engine_name
    )

    all_contestants = [alex, bob, charlie, david, eric, fiona]
    matchups = list(itertools.combinations(all_contestants, 2))
    
    total_matches = len(matchups)
    print(f">>> 共计 {total_matches} 场对决即将上演...\n")

    # === 循环赛开始 ===
    for index, (p1, p2) in enumerate(matchups):
        print(f"==============================================")
        print(f"⚔️  MATCH {index+1}/{total_matches}: {p1.name} VS {p2.name}")
        print(f"   ({p1.name}的人设) vs ({p2.name}的人设)")
        print(f"==============================================")
        
        p1.hp = 10
        p2.hp = 10
        history_log = []
        
        ROUNDS_PER_MATCH = 5
        
        for r in range(1, ROUNDS_PER_MATCH + 1):
            history_text = "\n".join(history_log) if history_log else "None (Game Start)"
            
            print(f"   Round {r} 思考中...", end="", flush=True)
            action1 = p1.make_choice(r, p2.name, history_text)
            action2 = p2.make_choice(r, p1.name, history_text)
            print(" 完成!")

            delta1, delta2 = 0, 0
            res_desc = ""
            
            if action1 == "Cooperate" and action2 == "Cooperate":
                delta1, delta2 = 2, 2
                res_desc = "🤝 双赢"
            elif action1 == "Defect" and action2 == "Cooperate":
                delta1, delta2 = 4, -2
                res_desc = f"🔪 {p1.name}背刺成功"
            elif action1 == "Cooperate" and action2 == "Defect":
                delta1, delta2 = -2, 4
                res_desc = f"🔪 {p2.name}背刺成功"
            elif action1 == "Defect" and action2 == "Defect":
                delta1, delta2 = -1, -1
                res_desc = "💥 双输冲突"
            
            p1.hp += delta1
            p2.hp += delta2
            
            log_str = f"Round {r}: {p1.name} chose {action1}, {p2.name} chose {action2}"
            history_log.append(log_str)
            
            print(f"   -> 结果: {p1.name}({action1}) vs {p2.name}({action2}) | {res_desc}")
            print(f"   -> 血量: {p1.name}: {p1.hp} | {p2.name}: {p2.hp}")
            
            time.sleep(1) 

        print(f"\n   🏁 本场结束!")
        print(f"   最终得分: {p1.name} [{p1.hp}] - {p2.name} [{p2.hp}]")
        if p1.hp > p2.hp:
            print(f"   🏆 胜者: {p1.name}")
        elif p2.hp > p1.hp:
            print(f"   🏆 胜者: {p2.name}")
        else:
            print(f"   🤝 平局")
        print("\n")
        time.sleep(2)

    print(">>> 所有比赛结束！<<<")

if __name__ == "__main__":
    run_tournament()