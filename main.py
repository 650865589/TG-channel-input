import os
import re
import time
try:
    import pyautogui
except ImportError:
    print("❌ 缺少必要的依赖库，请先运行: pip install pyautogui")
    exit(1)

# ==========================================
# ⚙️ 配置区域
# ==========================================
# 包含链接的txt文件路径
LINKS_FILE = 'links.txt'

# 📍 每次加入后停留等待的时间(秒)。建议保持3-5秒以上，等待TG界面响应
DELAY_UI_LOAD = 3
DELAY_BETWEEN_JOINS = 5

# PyAutoGUI 的自动安全保护机制，鼠标移动到屏幕四角将中止程序
pyautogui.FAILSAFE = True
# ==========================================

def parse_links(content):
    # 正则提取，支持标准链接、@username、以及纯文本的username
    # 由于纯文本可能会匹配到其他非目标字符串，我们稍微放宽匹配，并结合后续过滤
    pattern = r'(?:https?://)?(?:t\.me/|telegram\.me/)?@?([a-zA-Z0-9_\+\-]+)(?:/\d+)?'
    raw_targets = re.findall(pattern, content)
    
    targets = []
    for t in raw_targets:
        t = t.strip('/')
        if t and '?' not in t:
            if t.startswith('joinchat/'):
                hash_str = t.split('/', 1)[1]
                targets.append(('private', hash_str))
            elif t.startswith('+'):
                hash_str = t[1:]
                targets.append(('private', hash_str))
            else:
                targets.append(('public', t))
                
    # 去重
    seen = set()
    unique_targets = []
    for t in targets:
        if t not in seen:
            unique_targets.append(t)
            seen.add(t)
            
    return unique_targets

def get_coordinate(prompt_text):
    print("--------------------------------------------------")
    print(prompt_text)
    print("👉 准备好后，按回车键开始 5 秒倒计时...")
    input()
    for i in range(5, 0, -1):
        print(f"⏳ {i} 秒...")
        time.sleep(1)
    
    x, y = pyautogui.position()
    print(f"🎯 记录成功！坐标为: X={x}, Y={y}")
    print("--------------------------------------------------\n")
    return x, y

def main():
    print("=== Telegram Windows本地化自动加群工具 ===")
    if not os.path.exists(LINKS_FILE):
        print(f"❌ 找不到 {LINKS_FILE}。请创建并将链接粘贴到里面。")
        return
        
    with open(LINKS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    targets = parse_links(content)
    if not targets:
        print("⚠️ 未从文件中提取到任何有效链接，请检查格式。")
        return
        
    print(f"✅ 解析出 {len(targets)} 个有效链接。")
    
    has_public = any(t == 'public' for t, _ in targets)
    has_private = any(t == 'private' for t, _ in targets)
    
    pub_x, pub_y = 0, 0
    priv_x, priv_y = 0, 0
    mute_x, mute_y = 0, 0
    
    if has_public:
        msg = (
            "【录制：公开频道/群组的加入按钮】\n"
            "1. 随便进入一个你还没加入的【公开】Telegram频道。\n"
            "2. Telegram界面底部会显示【加入频道】或【Join Channel】按钮。\n"
            "3. 请将鼠标悬停在那个按钮上，不要动！\n"
            "4. 倒计时结束后会自动记录该位置。"
        )
        pub_x, pub_y = get_coordinate(msg)
        
    if has_private:
        msg = (
            "【录制：私密群组的弹窗加入按钮】\n"
            "1. 随便点击一个你想加入的【私密邀请链接】（带+号或joinchat的链接）。\n"
            "2. Telegram会在屏幕正中间弹出一个确认弹窗，包含【加入群组】按钮。\n"
            "3. 请将鼠标悬停在那个【加入】按钮上，不要动！\n"
            "4. 倒计时结束后会自动记录该位置。\n"
            "注意：录制完后你可以先手动把这个弹窗关掉。"
        )
        priv_x, priv_y = get_coordinate(msg)
        
    msg_mute = (
        "【录制：群组/频道的静音(Mute)按钮】\n"
        "1. 这个按钮通常在聊天界面的底部或右侧（取决于你是否全屏以及你使用的语言版本，比如「Mute」或「静音」）。\n"
        "2. 请将鼠标悬停在那个【静音(Mute)】按钮上，不要动！\n"
        "3. 倒计时结束后会自动记录该位置。"
    )
    mute_x, mute_y = get_coordinate(msg_mute)
        
    print("\n🚀 准备就绪，开始自动执行！")
    print("💡 警告：执行期间请不要动鼠标！如需强行停止，请将鼠标用力滑动到【屏幕任意一个角】！")
    time.sleep(3)
    
    for idx, (link_type, target) in enumerate(targets, 1):
        print(f"\n👉 [{idx}/{len(targets)}] 正在处理: {target} ({link_type})")
        
        if link_type == 'public':
            tg_url = f"tg://resolve?domain={target}"
            target_x, target_y = pub_x, pub_y
        else:
            tg_url = f"tg://join?invite={target}"
            target_x, target_y = priv_x, priv_y
            
        # 调用 Windows 底层协议拉起 Telegram
        os.startfile(tg_url)
        
        # 等待 Telegram 界面响应并加载内容
        time.sleep(DELAY_UI_LOAD)
        
        # 移动鼠标并点击！
        pyautogui.moveTo(target_x, target_y, duration=0.2)
        pyautogui.click()
        
        print(f"  ✅ 已点击加入，等待 {DELAY_UI_LOAD} 秒后点击静音...")
        
        # 等待加入完成，然后点击静音
        time.sleep(DELAY_UI_LOAD)
        pyautogui.moveTo(mute_x, mute_y, duration=0.2)
        pyautogui.click()
        
        print(f"  ✅ 已点击静音，等待 {DELAY_BETWEEN_JOINS} 秒后处理下一个...")
        time.sleep(DELAY_BETWEEN_JOINS)

    print("\n🎉 所有链接处理完毕！")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ 已手动终止。")
    except pyautogui.FailSafeException:
        print("\n⏹️ 触发屏幕角落防误触安全机制，已强行终止自动化！")
