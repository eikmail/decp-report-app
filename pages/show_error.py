import numpy as np
import streamlit as st
import pandas as pd
import streamlit_app
from psycopg2.extensions import register_adapter, AsIs

st.markdown("# Error list")
st.sidebar.markdown("# Error list")

if not streamlit_app.check_password():
    st.stop()

# For session_id conversion
register_adapter(np.int64, AsIs)

query_errors = """
    SELECT 
        (SELECT name FROM decp_report.step s WHERE s.step_id = r.step_id) AS step,
        (SELECT name FROM decp_report."source" s WHERE s.source_id = r.source_id) AS source,
        (SELECT name FROM decp_report.file f WHERE f.file_id = r.file_id) AS file,
        (SELECT name FROM decp_report.exclusion_type et WHERE et.exclusion_type_id = r.exclusion_type_id) AS type,
        r."position", 
        r.exclusion_type_id,
        r.message,
        r.error,
        r."path",
        r.id_content 
    FROM decp_report.report r 
    WHERE r.exclusion_type_id = 1
    AND session_id = :session_id
"""

if "source_id" in st.session_state and st.session_state.get("source_id", None) is not None:
    source_id = int(st.session_state.get("source_id", None))

    conn = st.connection("decp_database")
    df = conn.query("select name from decp_report.source WHERE source_id = :source_id",ttl="10s",params={"source_id":source_id})
    source_name = df['name'][0]
    
    st.sidebar.markdown(source_name)
else:
    # Get sources list
    #conn = st.connection("decp_database")
    #df = conn.query("select NULL as source_id ,'Choisissez' as name UNION select source_id,name from decp_report.source")

    #source_name = st.selectbox("Sélectionnez une source de données",df["name"])
    #source_id = df.loc[df["name"] == source_name, 'source_id'].iloc[0]
    source_id = None

if source_id is None:
    st.write("Affichage de toutes les sources")

    # Get sources list
    conn = st.connection("decp_database")
    df = conn.query("SELECT session_id,CONCAT(session_id,' - ',name,' ',end_date) as full_name FROM decp_report.session ORDER BY end_date DESC")
    df['session_id'].values.astype(int)

    session_name = st.selectbox("Sélectionnez une session",df["full_name"])
    session_id = df.loc[df["full_name"] == session_name, 'session_id'].iloc[0]

    if session_id is not None:
        data = conn.query(query_errors,ttl="10s",params={"session_id": session_id})    
        st.dataframe(data)

else:
    st.header(source_name)

    # Get sources list
    conn = st.connection("decp_database")
    df = conn.query("SELECT session_id,CONCAT(session_id,' - ',name, ' ', end_date) as full_name FROM decp_report.session ORDER BY end_date DESC")
    st.dataframe(df)

    session_name = st.selectbox("Sélectionnez une session",df["full_name"])
    session_id = df.loc[df["full_name"] == session_name, 'session_id'].iloc[0]

    if session_id is not None:
        data = conn.query("SELECT session_date,nb_records from decp_report.v_stats_all WHERE source_id = :source_id and session_id = :session_id",ttl="10s",params={"source_id":source_id,"session_id": session_id})    
        st.line_chart(data,x='session_date')

        query_errors += " source_id = :source_id"
        data = conn.query(query_errors,ttl="10s",params={"source_id":source_id,"session_id": session_id})    
        st.dataframe(data)

