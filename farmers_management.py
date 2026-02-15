st.title("Farmers Management")
farmers = load_farmers()
st.dataframe(farmers)

import sqlite3
import hashlib
from farmer_db import get_db_connection

st.title("Farmer Profile & Management")

def get_farmer_by_id(fid):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, contact, location, crops_grown, notes FROM farmers WHERE id=?", (fid,))
    row = c.fetchone()
    conn.close()
    return row

if "farmer_id" in st.session_state and st.session_state["farmer_id"]:
    farmer = get_farmer_by_id(st.session_state["farmer_id"])
    if farmer:
        st.subheader(f"👤 Farmer: {farmer[1]}")
        st.write(f"**Contact:** {farmer[2]}")
        st.write(f"**Location:** {farmer[3]}")
        st.write(f"**Crops Grown:** {farmer[4]}")
        st.write(f"**Notes:** {farmer[5]}")
        st.markdown("---")
        st.info("Your recommended crops and fertilisers will appear in the respective dashboard sections after you use the recommendation tools.")
    else:
        st.error("Farmer profile not found.")
else:
    st.warning("Please sign in to view your profile.")
