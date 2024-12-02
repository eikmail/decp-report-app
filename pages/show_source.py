import streamlit as st
import pandas as pd
import streamlit_app

st.markdown("# Error list")
st.sidebar.markdown("# Error list")

if not streamlit_app.check_password():
    st.stop()

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
else:
    st.header(source_name)

    # Get sources list
    conn = st.connection("decp_database")
    df = conn.query("SELECT session_id,CONCAT(name, ' ', end_date) as full_name FROM decp_report.session ORDER BY end_date DESC")

    source_name = st.selectbox("Sélectionnez une session",df["full_name"])
    source_id = df.loc[df["full_name"] == source_name, 'source_id'].iloc[0]
