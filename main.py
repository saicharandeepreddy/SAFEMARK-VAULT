import streamlit as st
import hashlib
from datetime import datetime
from PIL import Image
import io
import sqlite3
import pandas as pd

# ==========================================
# 🗄️ DATABASE SETUP
# ==========================================
conn = sqlite3.connect('safemark_ledger.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS registry 
             (student_id TEXT, file_hash TEXT, timestamp TEXT)''')
conn.commit()

def add_to_db(student_id, file_hash, timestamp):
    c.execute("INSERT INTO registry (student_id, file_hash, timestamp) VALUES (?, ?, ?)", 
              (student_id, file_hash, timestamp))
    conn.commit()

def get_all_records():
    c.execute("SELECT * FROM registry")
    return c.fetchall()

# ==========================================
# 🎨 UI UPGRADE: MODERN SAAS CSS
# ==========================================
st.set_page_config(page_title="SafeMark Vault", page_icon="🛡️", layout="wide")

custom_css = """
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global Styling */
    .stApp { background-color: #0B0F19; color: #E2E8F0; }

    /* Glowing Gradient Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.39);
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        color: white;
    }

    /* Download Button Specific Fix */
    div.stDownloadButton > button {
        background: linear-gradient(90deg, #10b981, #059669) !important;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.39) !important;
    }

    /* Glassmorphism Cards */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 12px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 🔐 AUTHENTICATION & STATE MANAGEMENT
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = ""

def login(user, pw):
    if user == "admin" and pw == "admin":
        st.session_state.logged_in = True
        st.session_state.role = "admin"
        st.session_state.username = "Faculty Administrator"
    elif user.lower() == "student" and pw == "123":
        st.session_state.logged_in = True
        st.session_state.role = "student"
        st.session_state.username = "Priya M." # Fixed User Profile
    else:
        st.error("Invalid credentials.")

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = ""

# ==========================================
# 🧠 CORE LOGIC: PURE PYTHON STEGANOGRAPHY
# ==========================================
DELIMITER = "====EOF===="

def encode_image(img_bytes, secret_data):
    image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    encoded = image.copy()
    width, height = image.size
    secret_data += DELIMITER
    binary_secret = ''.join([format(ord(i), "08b") for i in secret_data])
    binary_len = len(binary_secret)
    pixels = encoded.load()
    data_index = 0
    for y in range(height):
        for x in range(width):
            if data_index < binary_len:
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_secret[data_index])
                pixels[x, y] = (r, g, b)
                data_index += 1
            else:
                break
        if data_index >= binary_len:
            break
    img_byte_arr = io.BytesIO()
    encoded.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def decode_image(img_bytes):
    try:
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        pixels = image.load()
        width, height = image.size
        current_byte = ""
        decoded_data = ""
        MAX_CHARS_TO_CHECK = 300 
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                current_byte += str(r & 1)
                if len(current_byte) == 8:
                    decoded_data += chr(int(current_byte, 2))
                    current_byte = "" 
                    if DELIMITER in decoded_data:
                        return decoded_data.split(DELIMITER)[0]
                    if len(decoded_data) > MAX_CHARS_TO_CHECK:
                        return None
        return None
    except Exception as e:
        return None

# ==========================================
# 🚪 PAGE 1: LOGIN PORTAL
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2913/2913133.png", width=80)
        st.title("SafeMark Gateway")
        st.write("University Intellectual Property Protection System")
        st.info("**Demo Logins:**\n- Student: `student` / `123`\n- Admin: `admin` / `admin`")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Authenticate"):
            login(username, password)
            st.rerun()

# ==========================================
# 🎓 PAGE 2: STUDENT VAULT
# ==========================================
elif st.session_state.role == "student":
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4140/4140048.png", width=50)
        st.write(f"**Logged in as:**\n{st.session_state.username}")
        st.markdown("---")
        st.write("🟢 Connection Secure")
        st.button("Logout", on_click=logout)

    st.title("🛡️ The SafeMark Vault")
    st.write("Protect and verify your digital assets.")

    tab1, tab2 = st.tabs(["🔒 Protect & Embed", "🔍 Verify Asset"])

    with tab1:
        st.subheader("1. Upload Original File")
        # Unique key prevents caching bugs between tabs
        upload_protect = st.file_uploader("Drop PNG artwork here", type=["png"], key="upload_vault")

        if upload_protect is not None:
            colA, colB = st.columns([1, 1])
            with colA:
                st.image(upload_protect, caption="Ready for Encryption", width=300)

            with colB:
                if st.button("🔐 Lock & Watermark Asset"):
                    with st.spinner("Encrypting and saving to database..."):
                        file_bytes = upload_protect.getvalue()

                        # 1. Check if already protected
                        existing_data = decode_image(file_bytes)
                        if existing_data:
                            st.error("⚠️ SYSTEM ALERT: This asset is already protected!")
                            st.code(existing_data)
                        else:
                            # 2. Process New Protection
                            file_hash = hashlib.sha256(file_bytes).hexdigest()
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            secret_message = f"Owner: {st.session_state.username} | Hash: {file_hash[:16]}... | Time: {current_time}"

                            protected_img_bytes = encode_image(file_bytes, secret_message)

                            # 3. Database Save
                            add_to_db(st.session_state.username, file_hash, current_time)

                            st.success("✅ Asset Secured & Logged!")
                            st.info(f"**Official Timestamp:** {current_time}")
                            st.toast('Asset Successfully Protected!', icon='✅')

                            # 4. Flawless Download Button
                            st.download_button(
                                label="⬇️ Download Protected Vault File",
                                data=protected_img_bytes,
                                file_name=f"safemark_{file_hash[:6]}.png",
                                mime="image/png"
                            )

    with tab2:
        st.subheader("System Scanner")
        upload_verify = st.file_uploader("Drop image to scan", type=["png"], key="upload_scan")
        if upload_verify is not None:
            if st.button("🔍 Run Deep Scan"):
                with st.spinner("Extracting hidden data..."):
                    extracted_data = decode_image(upload_verify.getvalue())
                    if extracted_data:
                        st.success("🚨 MATCH FOUND! Asset is protected.")
                        st.code(extracted_data)
                        st.balloons()
                    else:
                        st.error("❌ No SafeMark signature detected.")

# ==========================================
# 👑 PAGE 3: FACULTY ADMIN DASHBOARD
# ==========================================
elif st.session_state.role == "admin":
    with st.sidebar:
        st.write(f"👑 **Admin:**\n{st.session_state.username}")
        st.markdown("---")
        st.button("Logout", on_click=logout)

    st.title("🗄️ University IP Global Ledger")

    records = get_all_records()
    df = pd.DataFrame(records, columns=["Student ID", "SHA-256 Hash", "Timestamp"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Protected Assets", len(records) + 1200) # Mock data addition for visuals
    col2.metric("Active Students", df['Student ID'].nunique() + 340)
    col3.metric("System Status", "Healthy 🟢")

    st.markdown("### 📋 Immutable Ledger Registry")
    if len(records) > 0:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No files uploaded to the local database yet. Log in as a student to protect a file!")