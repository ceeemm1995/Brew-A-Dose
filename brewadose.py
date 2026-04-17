import streamlit as st
import pandas as pd
import hashlib
import os
from datetime import date
from pydantic import BaseModel
from typing import Optional


USER_DB = "users.csv"
BEAN_DB = "bean_library.csv"
SESSION_DB = "session_history.csv"

try:
    df = pd.read_csv("users.csv") 
except FileNotFoundError:

    df = pd.DataFrame(columns=["username", "password", "role"])

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def save_to_db(data, file_path):
    df = pd.DataFrame([data])
    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)

if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'user' not in st.session_state:
    st.session_state['user'] = None

if not st.session_state.get('logged_in', False):
    st.title("☕ Brew A Dose")
    st.info("Hey Brewer! Please log in to continue.")

    choice = st.sidebar.selectbox("Access", ["Login", "Sign Up"])

    if choice == "Login":
        user = st.sidebar.text_input("Username")
        passwd = st.sidebar.text_input("Password", type='password')
       
        if st.sidebar.button("Enter Vault"):
           
           user_match = df[df['username'] == user]
    
           if not user_match.empty:
        
                actual_role = user_match.iloc[0]['role']

                st.session_state['logged_in'] = True
    
                st.session_state['username'] = user  
                st.session_state['role'] = actual_role
                st.session_state['user'] = user      
    
                st.rerun()

    if choice == "Sign Up":
       with st.form ("signup_form"):

        role = st.selectbox("I am a:", ["Barista", "Roaster"])
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type='password')

        submit = st.form_submit_button("Create Account")
 
        if submit:
            if new_user and new_pass:
             hashed_password = make_hashes(new_pass)

             user_data = {"username": new_user, "password": hashed_password, "role": role}
             save_to_db(user_data, "users.csv")
             st.success(f"Account created as a {role}!")
        else:
             st.error("Please fill in both fields!")

if not st.session_state['logged_in']:
    st.stop()

st.title("☕ Brew A Dose")

if st.session_state.get('logged_in', False):
    with st.sidebar:

        st.write(f"👤 **Logged in as:** {st.session_state.get('username', 'None')}")
        st.write(f"🏷️ **Role:** {st.session_state.get('role', 'None')}")

        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.session_state['role'] = None
            st.rerun()

def save_to_db(data, file_path):
    """Saves a dictionary of data to a CSV file."""
    df = pd.DataFrame([data])
    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)

class Bean(BaseModel):
    name: str
    origin: str
    process: str
    roast_date: date
    ideal_temp: float
    notes: str

st.set_page_config(page_title="Brew A Dose", layout="centered")

st.markdown("""
    <style>
    /* Deep Black Background for OLED/Mobile battery saving */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Coffee Brown Buttons */
    .stButton>button {
        background-color: #795548;
        color: white;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([" BEAN STUDY ", " CUPPING LOG ", " BREWING LOG ", " HISTORY ", " ROASTER INTELLIGENCE ", " FLAVOR WHEEL "])

with tab1:
    st.subheader("Roasted Beans")
    with st.form(key="study_form"):
        name = st.text_input("Bean Name")
        origin = st.text_input("Origin")
        process = st.selectbox("Process", ["Washed", "Natural", "Anaerobic", "Honey"])
        r_date = st.date_input("Roast Date", value=date.today())
        temp = st.slider("Ideal Temp (°C)", 88.0, 98.0, 93.5, step=0.1)
        profile_notes = st.text_area("Notes")
        remarks = st.text_area("Insights")

        
        if st.form_submit_button(" SAVE DATA "):
            
            new_bean_dict = {
                "date": date.today(),
                "name": name,
                "origin": origin,
                "process": process,
                "roast_date": r_date,
                "temp": temp,
                "p_notes": profile_notes,
                "remarks": remarks

            }
            save_to_db(new_bean_dict, BEAN_DB)
            st.success(f"Locked in: {name}")
            st.json(new_bean_dict)

with tab2:
    st.subheader("Performance")
    with st.form(key="cupping_form"):
        has_defect = st.toggle("Flag Defects?")
        d_type = st.selectbox("Type", ["None", "Quaker", "Phenolic", "Mouldy"])
        taste_notes = st.text_area("Notes")
        remarks = st.text_area("Insights")
        
        if st.form_submit_button("SAVE CUPPING SESSION"):
            cupping_data = {
                "date": date.today(),
                "type": "Cupping",
                "defects": d_type if has_defect else "None",
                "taste notes": taste_notes,
                "remarks": remarks
            }
            save_to_db(cupping_data, SESSION_DB)
            st.success("Cupping data synchronized.")

with tab3:
    st.subheader("Brewing Log")
    with st.form(key="brewing_form"):
        b_name = st.text_input("Bean Name (Session)")
        method = st.text_input("Brew Method (e.g., V60)")
        b_notes = st.text_area("Brewing Notes")
        
        if st.form_submit_button("LOG BREW"):
            brew_data = {
                "date": date.today(),
                "type": "Brew",
                "bean": b_name,
                "method": method,
                "notes": b_notes
            }
            save_to_db(brew_data, SESSION_DB)
            st.success("Brew session logged to vault.")

with tab4:
    st.subheader("Digital Vault")
    view_type = st.radio("View History For:", ["Beans Library", "Session History"], horizontal=True)
    target_file = BEAN_DB if view_type == "Beans Library" else SESSION_DB
    
    if os.path.exists(target_file):
        history_df = pd.read_csv(target_file)

        row_to_edit = st.selectbox("Select entry to edit (by Index):", history_df.index)

        with st.expander("📝 Edit Selected Entry"):
            
            new_name = st.text_input("Edit Name", value=df.at[row_to_edit, 'name'])
            new_notes = st.text_area("Edit Notes", value=df.at[row_to_edit, 'notes'])
            
            if st.button("Update Vault"):
                
                history_df.at[row_to_edit, 'name'] = new_name
                history_df.at[row_to_edit, 'notes'] = new_notes
                
                history_df.to_csv(target_file, index=False)
                st.success("Entry updated successfully!")
        
        st.dataframe(history_df.iloc[::-1], use_container_width=True)
    else:
        st.info("Vault is currently empty.")

with tab5: 
    st.subheader("Roaster Intelligence")
    with st.form(key="roaster_form"):
        r_name = st.text_input("Roaster Name")
        charge_temp = st.number_input("Charge Temp (°C)", 150.0, 250.0, 200.0)
        dtr = st.slider("DTR (%)", 10.0, 30.0, 20.0)
        total_time = st.number_input("Total Roast Time (min)", 8.0, 15.0, 11.0)
        
        if st.form_submit_button("LOG ROAST PROFILE"):
            roast_data = {
                "date": date.today(),
                "roaster": r_name,
                "charge_temp": charge_temp,
                "dtr": dtr,
                "total_time": total_time
            }
            save_to_db(roast_data, "roast_history.csv")
            st.success("Roast Profile Synchronized.")

with tab6:
    st.header("Coffee Taster's Wheel")
    
    st.image("wheel.png", caption="Sensory Reference", use_container_width=True)