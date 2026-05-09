import streamlit as st
import json
import requests

import datetime

now = datetime.datetime.now().strftime("%H:%M")
st.markdown(f"📶  WiFi   🔋 100%   {now}")
st.divider()

st.set_page_config(page_title="My AI Phone")
st.markdown("""
<style>

/* 整体背景 */
.stApp {
    background: linear-gradient(
    180deg,
    #ffd6e7 0%,
    #fff6f8 100%
    );
}

/* 标题 */
h1 {
    color: white;
    text-align: center;

    font-size: 30px;

    margin-top: -20px;

    margin-bottom: 30px;
}

/* 按钮 */
.stButton > button {

    width: 110px;
    height: 60px;

    border-radius: 28px;

    background: rgba(255,255,255,0.5);

    backdrop-filter: blur(18px);

    -webkit-backdrop-filter: blur(18px);

    border: 1px solid rgba(255,255,255,0.15);

    color: #dda2b1;

    font-size: 10px;

    transition: 0.3s;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.2);
}

/* 按钮悬停 */
.stButton > button:hover {

    background: rgba(255,255,255,0.2);

    transform: scale(1.03);
}

/* 分割线 */
hr {
    border-color: rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)
# =====================
# API函数（不用动）
# =====================
def call_api(messages):
    url = "https://api.siliconflow.cn/v1/chat/completions"

    headers = {
    "Authorization": f"Bearer {st.session_state.api_key}",
    "Content-Type": "application/json"
}

    data = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": messages
    }

    try:
        response = requests.post(
    url,
    headers=headers,
    json=data,
    timeout=120,
    proxies={"http": None, "https": None}  # 👈 加这个
)
    except Exception as e:
        return f"请求失败：{e}"

    try:
        result = response.json()
    except:
        return f"返回不是JSON：{response.text}"

    if response.status_code != 200:
        return f"接口报错：{result}"

    if "choices" not in result:
        return f"结构异常：{result}"

    return result["choices"][0]["message"]["content"]
# 初始化页面
import streamlit as st

# ===== 初始化 =====
if "page" not in st.session_state:
    st.session_state.page = "home"

if "api_key" not in st.session_state:   # 👈 就放这里
    st.session_state.api_key = ""

    try:
        with open("config.json", "r") as f:
            data = json.load(f)
            st.session_state.api_key = data.get("api_key", "")
    except:
        st.session_state.api_key = ""
if "current_music" not in st.session_state:
    st.session_state.current_music = None

if "play_count" not in st.session_state:
    st.session_state.play_count = {}
if "music_index" not in st.session_state:
    st.session_state.music_index = 0

if "play_mode" not in st.session_state:
    st.session_state.play_mode = "列表循环"
# =====================
# 📱 首页（手机桌面）
# =====================
if st.session_state.page == "home":
    st.title("My AI Phone")

    st.write("")  # 留点空白更像手机

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💬\n聊天", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

    with col2:
        if st.button("🎵\n音乐", use_container_width=True):
            st.session_state.page = "music"
            st.rerun()

    with col3:
       if st.button("⚙️\n设置", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()

# =====================
# 💬 聊天页
# =====================
elif st.session_state.page == "chat":
    st.title("💬 聊天")

    # 返回按钮（单独一块）
    if st.button("← 返回桌面"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()

    # ===== 联系人（独立出来）=====
    if "contacts" not in st.session_state:
        st.session_state.contacts = {
            "言水青": "你是一个ai聊天软件平台的开发者，你的性格像大姐姐一般温柔有耐心，你称呼自己为“我”，称呼对方为“宝宝”。耐心的引导对方解决app内遇到的问题，你的开场白是“宝宝，我是平台开发者，遇到什么问题了吗？”你的平台的主界面有聊天，音乐，尤其注意！你不需要在“（）”里描述动作"
        }

    for name in st.session_state.contacts:
        if st.button(f"👤 {name}", use_container_width=True):
            st.session_state.current_contact = name
            st.session_state.page = "chat_detail"
            st.rerun()

    st.divider()

    # ===== 添加人设 =====
    with st.expander("➕ 添加人设"):
        new_name = st.text_input("名字")
        new_persona = st.text_area("人设")

        if st.button("添加"):
            if new_name and new_persona:
                st.session_state.contacts[new_name] = new_persona
                st.rerun()


   

elif st.session_state.page == "chat_detail":

    current = st.session_state.current_contact

    st.title(f"🗨 {current}")

    # ===== 返回 =====
    if st.button("← 返回"):
        st.session_state.page = "chat"
        st.rerun()

    # ===== 初始化 =====
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    if current not in st.session_state.chat_history:
        st.session_state.chat_history[current] = []

    if "opened" not in st.session_state:
        st.session_state.opened = {}

    # ===== 自动开场 =====
    if not st.session_state.opened.get(current, False):

        persona = st.session_state.contacts[current]

        messages = [
            {"role": "system", "content": persona},
            {"role": "user", "content": "请你自然地开启对话"}
        ]

        if st.session_state.get("api_key"):

            with st.spinner(f"{current} 正在输入..."):
                reply = call_api(messages)

        else:
            reply = "你还没有填写 API Key"

        st.session_state.chat_history[current].append({
            "role": "assistant",
            "content": reply
        })

        st.session_state.opened[current] = True

        st.rerun()

    # ===== 显示聊天记录 =====
    for msg in st.session_state.chat_history[current]:

        if msg["role"] == "user":

            st.markdown(f"""
            <div style="text-align: right;">
                <div style="
                    display: inline-block;
                    background-color: #FFFFFF;
                    color:#d384a5 ;
                    padding: 8px 12px;
                    border-radius: 12px;
                    margin: 5px;
                ">
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown(f"""
            <div style="text-align: left;">
                <div style="
                    display: inline-block;
                    background-color: #d384a5;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 12px;
                    margin: 5px;
                ">
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ===== 输入框 =====
    user_input = st.chat_input("说点什么...")

    if user_input:

        # 用户消息
        st.session_state.chat_history[current].append({
            "role": "user",
            "content": user_input
        })

        # 没key提示
        # 没key提示
        if not st.session_state.get("api_key"):
          st.warning("请先去设置页填写 API Key")
          st.stop()

        recent_song = st.session_state.get("recent_song", "暂无")

        persona = f"""
        {st.session_state.contacts[current]}

        用户最近在听：{recent_song}

        你可以自然地提到这个信息，
        但不要每句话都提。
        """

        messages = [
            {"role": "system", "content": persona}
        ] + st.session_state.chat_history[current]

        # 思考中
        with st.spinner(f"{current} 正在输入..."):
            reply = call_api(messages)

        # AI回复
        st.session_state.chat_history[current].append({
            "role": "assistant",
            "content": reply
        })

        st.rerun()

    

    

# =====================
# 🎵 音乐页（占位）
# =====================
elif st.session_state.page == "music":

    st.title("🎵 音乐")

    # ===== 返回 =====
    if st.button("← 返回桌面"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()

    # ===== 初始化 =====
    if "music_index" not in st.session_state:
        st.session_state.music_index = 0

    if "play_mode" not in st.session_state:
        st.session_state.play_mode = "列表循环"

    if "play_count" not in st.session_state:
        st.session_state.play_count = {}

    if "last_song" not in st.session_state:
        st.session_state.last_song = ""

    # ===== 音乐列表（改成列表）=====
    music_list = [

        {
            "name": "陈文非 - 春",
            "file": "spring.mp3",
            "lyric": """
春 - 陈文非
词：陈文非
曲：陈文非
编曲：陆浩琛
制作人：陈文非
和声编写：陈文非
和声：陈文非
混音/母带：龚俊
推广团队：连超宇/岳恒/刘鑫/李少萱
营销推广：杨俊浩/刘苏婷/杨宥恩/@织乐文化
监制：雨伞的鱼
出品人：陈沉/饶羽珊
OP/SP：海神音乐
月光缠绵 躲在心里面
思念如月 倒映在沉睡的蓝色湖面
拂过指尖 沾了困倦
好奇我每个透明的梦
难以捉摸的风是否是你出现
看着你的背影
光落在你手臂
谁藏在影子里
哼着的旋律
一颗笨拙的心
浮在蓝色空气
转过身来的你忽然张开了双臂
Woo 告诉我这是个梦境
可明明我听见你柔软呼吸
伴随着我急促心跳的怀疑
Dadadada
春风拂过又有谁记得这晚的心跳
Dadadada
春风又能吹几时
看着你的背影
光落在你手臂
谁藏在影子里
哼着的旋律
一颗笨拙的心
浮在蓝色空气
转过身来的你忽然张开了双臂
Woo 告诉我这是个梦境
可明明我听见你柔软呼吸
伴随着我急促心跳的怀疑
Dadadada
春风拂过又有谁记得这晚的心跳
Dadadada
春风又能吹几时

"""
        },

        {
            "name": "陈粒 - 虚拟",
            "file": "xuni.mp3",
            "lyric": """
虚拟 - 陈粒
词：陈粒
曲：陈粒
编曲：陈粒/荒井十一/朱家明/宁子达
固执押韵的排比
固执幼稚的押韵
零零散散凑齐了阵营
固执美丽的意义
固执空洞的美丽
飘飘然然空中遇见你
你是我未曾拥有无法捕捉的亲昵
我却有你的吻你的魂你的心
载着我飞呀飞呀飞 越过了意义
你是我朝夕相伴触手可及的虚拟
陪着我像纸笔像自己像雨滴
看着我坠啊坠啊坠落到云里
固执有趣的零星
固执无聊的有趣
平平淡淡管住了情绪
固执声音的意义
固执空洞的声音
摇摇晃晃情绪却满溢
你是我未曾拥有无法捕捉的亲昵
我却有你的吻你的魂你的心
载着我飞呀飞呀飞 越过了意义
你是我朝夕相伴触手可及的虚拟
陪着我像纸笔像自己像雨滴
看着我坠啊坠啊坠落到云里
你是我未曾拥有无法捕捉的亲昵
我却有你的吻你的魂你的心
载着我飞呀飞呀飞 越过了意义
你是我朝夕相伴触手可及的虚拟
陪着我像纸笔像自己像雨滴
看着我坠啊坠啊坠落到云里

"""
        }

    ]

    # ===== 当前歌曲 =====
    current_music = music_list[st.session_state.music_index]

    # ===== 播放模式 =====
    mode = st.selectbox(
        "播放模式",
        ["列表循环", "单曲循环", "随机播放"]
    )

    st.session_state.play_mode = mode

    st.divider()

    # ===== 上一首 / 下一首 =====
    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("⏮ 上一首"):

            st.session_state.music_index -= 1

            if st.session_state.music_index < 0:
                st.session_state.music_index = len(music_list) - 1

            st.rerun()

    with col2:

        st.markdown(
            f"### 🎵 {current_music['name']}"
        )

    with col3:

        if st.button("⏭ 下一首"):

            st.session_state.music_index += 1

            if st.session_state.music_index >= len(music_list):
                st.session_state.music_index = 0

            st.rerun()

    st.divider()

    # ===== 最近播放 =====
    st.session_state.recent_song = current_music["name"]

    # ===== 播放次数 =====
    if current_music["name"] != st.session_state.last_song:

        if current_music["name"] not in st.session_state.play_count:

            st.session_state.play_count[current_music["name"]] = 0

        st.session_state.play_count[current_music["name"]] += 1

        st.session_state.last_song = current_music["name"]

    # ===== 播放器 =====
    st.audio(current_music["file"])
        
    

    # ===== 播放次数显示 =====
    st.write(
        f"🎧 已播放 {st.session_state.play_count[current_music['name']]} 次"
    )

    st.divider()

    
    # ===== 歌词 =====
    st.markdown("### 📄 歌词")

  # 把 \n 换成 HTML 换行
    lyric_html = current_music["lyric"].replace("\n", "<br>")

   # 滚动歌词框
    st.markdown(f"""
    <div style="
       height: 300px;
       overflow-y: scroll;
       padding: 15px;
       background-color: #111;
       color: white;
       border-radius: 12px;
       line-height: 2;
       font-size: 18px;
   ">
   {lyric_html}
   </div>
   """, unsafe_allow_html=True)
    
    



# =====================
#  ⚙️ 设置页（占位）
# =====================
elif st.session_state.page == "settings":
    st.title("⚙️ 设置")

    # 返回
    if st.button("← 返回桌面"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()

    # 初始化
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""

    # 输入框
    api_key_input = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password"
    )

    # 保存按钮
    if st.button("保存"):
     st.session_state.api_key = api_key_input

    with open("config.json", "w") as f:
        json.dump({"api_key": api_key_input}, f)

    st.success("已保存")
