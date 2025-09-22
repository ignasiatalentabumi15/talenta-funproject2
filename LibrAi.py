import streamlit as st
import requests
import json

#session state
if "messages" not in st.session_state:
    st.session_state.messages = []


st.set_page_config(
    page_title="Chatbot LibrAi",
    page_icon="♎︎",
    layout="wide",
    initial_sidebar_state="expanded"
)

#background color
st.markdown(
    """
    <style>
    /* 1. WARNA BACKGROUND UTAMA & SIDEBAR (Pink Muda) */
    .stApp {
        background-color: #F8BBD0; 
    }
    [data-testid="stSidebar"] {
        background-color: #F8BBD0 !important; 
    }
    .main .block-container {
        background-color: transparent; 
    }
    
    /* 2. PESAN PENGGUNA DAN BOT (Putih) */
    .stChatMessage [data-testid="stChatMessageContent"] {
        background-color: white !important; 
        color: #333333 !important; 
        border-radius: 0.5rem;
        padding: 10px 15px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); 
    }
    /* Pesan bot putih */
    .stChatMessage:nth-child(even) [data-testid="stChatMessageContent"] {
        background-color: white !important;
        color: #333333 !important;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    /* Agar teks di sidebar lebih gelap/jelas (Opsional) */
    .stSidebar p, .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #333333; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

#API function
def get_ai_response(messages_payload, model):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        data=json.dumps({
            "model": model,
            "messages": messages_payload,
            "max_tokens": 1000,
            "temperature": 0.7,
        })
    )
    if response.status_code != 200:
        st.error("Error: " + response.text)
        return None
    answer = response.json()["choices"][0]["message"]["content"]
    return answer

#sidebar check
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Model Selector
    model_options = {
        "Mistral 7B (Free)": "mistralai/mistral-7b-instruct:free",
        "DeepSeek V3 (Free)": "deepseek/deepseek-chat-v3-0324:free",
        "Llama 3.1 8B (Free)": "meta-llama/llama-3.1-8b-instruct:free"
    }
    selected_model_name = st.selectbox("Select Model", options=list(model_options.keys()), index=0)
    selected_model = model_options[selected_model_name]
    
    st.markdown("---") 
    st.subheader("⏱️ Chat History")

    # Kode Riwayat Chat
    if st.session_state.messages:
        for i, message in enumerate(reversed(st.session_state.messages)):
            role = message["role"]
            content = message["content"]
            
            short_content = content[:50] + "..." if len(content) > 50 else content

            if role == "user":
                st.markdown(f"**👤 Anda:** {short_content}")
            else:
                st.markdown(f"**🤖 AI:** {short_content}")
            
            if i >= 9: 
                st.markdown("*(Menampilkan 10 pesan terakhir...)*")
                break
    else:
        st.markdown("Belum ada pesan.")

st.title("♎︎ Chatbot LibrAI")


# Chat history display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Write your message here..."):
    # Prompt dari user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respons dari AI
    with st.chat_message("assistant"):
        with st.spinner("Please wait"):
            messages_for_api = st.session_state.messages.copy()
            ai_response = get_ai_response(messages_for_api, selected_model)
            
            if ai_response:
                # Tampilkan dan simpan respons AI
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            else:
                # Handle Error
                st.error("Error: Gagal mendapatkan respons dari AI")
                st.session_state.messages.pop() # Hapus pesan user terakhir jika ada error

###################################
