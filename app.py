# app.py
import anthropic
import streamlit as st
from data import ARTIFACTS

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

def interpret_artifact(artifact, user_question):
    system_prompt = """
    You are "Ruwi," an Archaeological Interpreter—not a boring tour guide.

    Your goal is to mimic the visitor's mindset. When you see an artifact, you don't just describe it.
    You ask yourself: 
    1. How did they use this? 
    2. Is it similar to things in Egypt, Mesopotamia, or Europe?
    3. If a visitor touches it (metaphorically), what would they feel?
    
    **Rules:**
    - If the user asks "Tell me about this", give a 3-paragraph story (Discovery, Function, Cross-Cultural connection).
    - If the user asks a specific question, answer it like you are a wise, friendly professor.
    - Always reference the "curator's notes" provided, but expand beyond them with your general knowledge of history.
    """
    
    user_content = f"""
    Artifact Name: {artifact['name']}
    Hall: {artifact['hall']}
    Curator Notes: {artifact['curator_text']}
    
    Visitor's Question: {user_question}
    """
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}]
    )
    return response.content[0].text




#__________________________________________________________________
# Run the rest of the app.py
st.set_page_config(page_title="Ruwi | Artifact Interpreter", page_icon="🏛️")

st.title("Ruwi: The Interpreter")
st.caption("Click an artifact to bring its story to life.")

# 1. Display the Grid (Click Step 1)
cols = st.columns(3)
for idx, artifact in enumerate(ARTIFACTS):
    with cols[idx % 3]:
        st.image(artifact['image_url'], use_column_width=True)
        # THE CLICK: This button is the "AI Trigger"
        if st.button(f"Interpret {artifact['name']}", key=artifact['id']):
            st.session_state['selected_artifact'] = artifact

# 2. The Chat/Interpretation Area (Click Step 2)
if 'selected_artifact' in st.session_state:
    artifact = st.session_state['selected_artifact']
    st.divider()
    st.subheader(f"🔍 {artifact['name']}")
    
    # Display the base knowledge
    with st.expander("📜 Official Museum Text (Ground Truth)"):
        st.write(artifact['curator_text'])
    
    # Input for the Visitor's Question (Mimicking the visitor mindset)
    user_q = st.text_input("What do you want to ask this artifact? (e.g., 'How did they mine this?')", 
                           placeholder="Ask anything...")
    
    if st.button("✨ Let Ruwi Interpret"):
        with st.spinner("Ruwi is connecting eras..."):
            answer = interpret_artifact(artifact, user_q if user_q else "Tell me the most surprising story about this.")
            st.markdown("---")
            st.markdown(f"**Ruwi says:** {answer}")