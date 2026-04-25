import streamlit as st
from textblob import TextBlob
import pandas as pd
import sqlite3
from datetime import datetime

# --- DATABASE CONFIGURATION ---
def connect_db():
    # This creates or connects to the local database file
    return sqlite3.connect('sentiment_history.db')

def create_table():
    conn = connect_db()
    c = conn.cursor()
    # Ensure the table exists with the correct columns
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (date TEXT, text_content TEXT, polarity REAL, result TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(text, polarity, result):
    conn = connect_db()
    c = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history (date, text_content, polarity, result) VALUES (?, ?, ?, ?)", 
              (current_date, text, polarity, result))
    conn.commit()
    conn.close()

# --- APP INTERFACE ---
st.set_page_config(page_title="SentimAI Lite", layout="centered", page_icon="🧠")
create_table()

st.title("🧠 SentimAI: Text Sentiment Analyzer")
st.markdown("Enter any text in English to analyze its emotional tone and save it to the database.")

# Layout with two main tabs
tab1, tab2 = st.tabs(["🔍 New Analysis", "📜 History Logs"])

with tab1:
    st.subheader("Analyze Text")
    user_text = st.text_area("Write or paste your text here:", height=150, placeholder="Example: I am having a wonderful day!")
    
    if st.button("Run Analysis"):
        if user_text.strip():
            # NLP Processing
            blob = TextBlob(user_text)
            polarity_score = round(blob.sentiment.polarity, 2)
            
            # Logic to determine result
            if polarity_score > 0.1:
                sentiment_res = "Positive 😊"
            elif polarity_score < -0.1:
                sentiment_res = "Negative 😡"
            else:
                sentiment_res = "Neutral 😐"
            
            # Display results
            st.divider()
            st.metric("Sentiment Score", f"{polarity_score}", delta=sentiment_res)
            st.write(f"**Result:** This text feels {sentiment_res.split()[0].lower()}.")
            
            # Back-end: Save to SQLite
            save_to_db(user_text, polarity_score, sentiment_res)
            st.success("Analysis saved to history!")
        else:
            st.warning("The text area cannot be empty.")

with tab2:
    st.subheader("Past Analyses")
    conn = connect_db()
    # Load data from SQL to a Pandas DataFrame
    try:
        df = pd.read_sql_query("SELECT date, text_content, polarity, result FROM history ORDER BY date DESC", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Option to delete history
            if st.button("Delete All Records"):
                conn.execute("DELETE FROM history")
                conn.commit()
                st.rerun()
        else:
            st.info("No records found yet. Try analyzing some text first!")
    except Exception as e:
        st.error(f"Error loading history: {e}")
    finally:
        conn.close()

st.sidebar.info("Engineering Note: This app uses TextBlob for NLP and SQLite3 for local persistence.")