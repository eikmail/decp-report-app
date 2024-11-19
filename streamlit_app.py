import hmac
import numpy as np
import pandas as pd
import streamlit as st
import time

st.markdown("# DECP statistiques flux")

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        conn = st.connection("decp_database")
        data = conn.query("select account_id,source_id from decp_report.account where user_name=:user_name and passwd = :passwd",ttl="10s",params={"user_name":st.session_state["username"],"passwd":st.session_state["password"]})
        if 'account_id' in data and len(data['account_id'])>0 and data['account_id'][0]>0:
            st.session_state["password_correct"] = True
            st.session_state["source_id"] = data['source_id'][0]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()

    if "password_correct" in st.session_state:
        st.error("User not known or password incorrect")
    return False


if not check_password():
    st.stop()


# Main Streamlit app starts here

if "source_id" in st.session_state and st.session_state.get("source_id", None) is not None:
    source_id = int(st.session_state.get("source_id", None))

    conn = st.connection("decp_database")
    df = conn.query("select name from decp_report.source WHERE source_id = :source_id",ttl="10s",params={"source_id":source_id})
    source_name = df['name'][0]
else:
    # Get sources list
    #conn = st.connection("decp_database")
    #df = conn.query("select NULL as source_id ,'Choisissez' as name UNION select source_id,name from decp_report.source")

    #source_name = st.selectbox("Sélectionnez une source de données",df["name"])
    #source_id = df.loc[df["name"] == source_name, 'source_id'].iloc[0]
    source_id = None

if source_id is None:
    st.write("Affichage de toutes les sources")

    # Request for all source query
    conn = st.connection("decp_database")
    data = conn.query("SELECT decp_report.get_query_stats_global()", ttl="10s")

    if 'get_query_stats_global' in data and len(data['get_query_stats_global'])>0:
        query = data['get_query_stats_global'][0]
        
        data = conn.query(query, ttl="10s")
        
        st.line_chart(data,x='session_date')
        st.dataframe(data)
else:
    st.header(source_name)
    
    conn = st.connection("decp_database")
    data = conn.query("SELECT session_date,nb_records,nb_errors,per_errors from decp_report.v_stats_all WHERE source_id = :source_id",ttl="10s",params={"source_id":source_id})    
    st.line_chart(data,x='session_date')
    st.dataframe(data)
