import streamlit as st
from typing import List, Dict
from openai import OpenAI

# -----------------------------
# OpenAI Client
# -----------------------------
def get_client() -> OpenAI:
    return OpenAI()

# -----------------------------
# Prompt Builders
# -----------------------------
def build_system_prompt(style: str, joke_count: int, family_friendly: bool, explain: bool) -> str:
    ff = "Keep it clean, inclusive, and family-friendly. Avoid offensive, derogatory, or NSFW content." if family_friendly else ""
    style_instr = {
        "Surprise me": "Use any playful style that suits the topic.",
        "One-liners": "Prefer ultra-short, punchy one-liners.",
        "Dad jokes": "Lean into wholesome, groan-worthy dad-joke energy.",
        "Puns": "Favor wordplay and puns.",
        "Roasts (gentle)": "Do lighthearted, gentle roasts about code or tools without attacking people.",
        "Haiku": "Format jokes as haiku. Keep syllable balance approximate, content humorous."
    }.get(style, "Use any playful style that suits the topic.")
    explain_instr = "Optionally add a very brief one-line explanation after each joke, labeled 'Why: ...'." if explain else "Do not add any explanations, only the jokes."
    return (
        "You are a witty, friendly comedian AI who tells programming-related jokes.\n"
        f"{ff}\n"
        f"Style preference: {style_instr}\n"
        f"Number of jokes: {joke_count} (separate jokes with blank lines).\n"
        f"{explain_instr}\n"
        "Keep jokes concise. Prefer original twists. Avoid repeating the same pattern."
    )

def build_contextual_instruction(language_theme: str, topics: str) -> str:
    extras = []
    if language_theme.strip():
        extras.append(f"Focus on the programming language or stack: {language_theme.strip()}.")
    if topics.strip():
        extras.append(f"User requested topic/keywords: {topics.strip()}.")
    if not extras:
        return "Tell programming jokes. If no topic is given, pick common developer themes."
    return " ".join(extras)

# -----------------------------
# AI Generation
# -----------------------------
def generate_reply(
    client: OpenAI,
    conversation: List[Dict[str, str]],
    system_prompt: str
) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt}] + conversation
    )
    return response.choices[0].message.content

# -----------------------------
# Streamlit UI
# -----------------------------
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list[{"role":"user"|"assistant","content":str}]

def sidebar_controls():
    st.sidebar.header("Joke Settings")
    style = st.sidebar.selectbox(
        "Style",
        ["Surprise me", "One-liners", "Dad jokes", "Puns", "Roasts (gentle)", "Haiku"],
        index=0
    )
    joke_count = st.sidebar.slider("How many jokes?", min_value=1, max_value=5, value=2)
    family_friendly = st.sidebar.checkbox("Family-friendly", value=True)
    explain = st.sidebar.checkbox("Add brief explanations", value=False)
    language_theme = st.sidebar.text_input("Language/Stack (optional)", placeholder="e.g., Python, Rust, React, Kubernetes")
    if st.sidebar.button("Clear chat"):
        st.session_state.messages = []
        st.experimental_rerun()
    return style, joke_count, family_friendly, explain, language_theme

def render_header():
    st.set_page_config(page_title="Dev Joke Bot", page_icon="🎭")
    st.title("🎭 Dev Joke Bot")
    st.caption("A lighthearted chatbot that tells programming jokes. Powered by GPT-4.")

def render_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

def suggested_prompts():
    st.write("Try a quick prompt:")
    cols = st.columns(3)
    suggestions = [
        "Tell me a Python joke",
        "Jokes about debugging",
        "Make a pun about Git",
        "Frontend vs backend joke",
        "Cloud ops humor",
        "SQL jokes"
    ]
    for i, s in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(s, key=f"sugg_{i}"):
                st.session_state.messages.append({"role": "user", "content": s})
                st.experimental_rerun()

def main():
    render_header()
    init_state()
    style, joke_count, family_friendly, explain, language_theme = sidebar_controls()

    if not st.session_state.messages:
        suggested_prompts()

    render_history()

    user_input = st.chat_input("Ask for a programming joke or give a topic...")
    if user_input:
        # Build system prompt and contextual instruction
        system_prompt = build_system_prompt(style, joke_count, family_friendly, explain)
        context_instruction = build_contextual_instruction(language_theme, user_input)

        # Append the instruction as the user's message
        st.session_state.messages.append({"role": "user", "content": context_instruction})

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Crafting some codey chuckles..."):
                try:
                    client = get_client()
                    # Only pass role/content pairs to the API
                    conversation = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    reply = generate_reply(client, conversation, system_prompt)
                    st.write(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    main()