import base64
from pathlib import Path
import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="Volkswagen Parts Tracker", page_icon="assets/vw_logo.png", layout="wide", initial_sidebar_state="collapsed")
BASE = Path(__file__).parent
ASSETS = BASE / "assets"
DEMO_EMAIL = "customer@demo.co.za"
DEMO_PASSWORD = "Track123"

ORDER = {
    "number": "VWP-2026-001258", "date": "12 Oct 2026", "eta": "18 Oct 2026, 14:00",
    "dealer": "Volkswagen Gqeberha", "part": "Brake Disc (Front)", "part_no": "5Q0 615 301 F",
    "quantity": 2, "status": "In Transit", "location": "Near Harrismith, Free State",
    "updated": "14 Oct 2026, 10:30"
}
ROUTE = pd.DataFrame([
    {"name":"Parts Warehouse, Johannesburg", "lat":-26.2041, "lon":28.0473, "kind":"Origin"},
    {"name":"Harrismith, Free State", "lat":-28.2728, "lon":29.1295, "kind":"Current location"},
    {"name":"Volkswagen Gqeberha", "lat":-33.9608, "lon":25.6022, "kind":"Destination"},
])

st.markdown("""
<style>
:root{--navy:#001e50;--blue:#0068d8;--ink:#14213d;--muted:#667085;--line:#e4eaf2;--bg:#f5f7fb}
.stApp{background:var(--bg);color:var(--ink)}
.block-container{max-width:1500px;padding-top:1rem;padding-bottom:2rem}
header[data-testid="stHeader"]{background:transparent} #MainMenu,footer{visibility:hidden}
[data-testid="stForm"]{border:0;padding:0}
.brand{display:flex;align-items:center;gap:12px;font-weight:850;font-size:22px;color:var(--navy);height:44px}
.brand img{width:42px;height:42px;object-fit:contain}
div[data-testid="stButton"] button{border-radius:10px;font-weight:700;border:1px solid transparent;background:transparent;color:var(--navy)}
div[data-testid="stButton"] button:hover{background:#eaf3ff;border-color:#bdd7f7;color:#0056b3}
div[data-testid="stFormSubmitButton"] button{background:linear-gradient(90deg,#002b63,#001e50);color:white;border:0;border-radius:10px;font-weight:800}
.navline{border-bottom:1px solid var(--line);margin:4px 0 18px}
.hero{position:relative;min-height:660px;border-radius:24px;overflow:hidden;background:#ddd;box-shadow:0 18px 48px rgba(0,30,80,.12)}
.hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.overlay{position:absolute;inset:0;background:linear-gradient(90deg,rgba(255,255,255,.97),rgba(255,255,255,.72) 43%,rgba(255,255,255,.03) 78%)}
.hero-copy{position:absolute;left:6%;top:9%;width:52%;color:var(--navy)}.eyebrow{font-size:13px;letter-spacing:.15em;font-weight:800}.hero-copy h1{font-size:58px;line-height:1.02;margin:15px 0}.lead{font-size:21px;color:#40536f}.copy{font-size:16px;color:#344054;line-height:1.55}
.card{background:white;border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 6px 20px rgba(15,35,65,.055);height:auto;color:var(--ink)}.page-title{font-size:34px;font-weight:900;color:var(--navy);margin:10px 0 4px}.sub{color:var(--muted);font-size:14px}.section{font-size:20px;font-weight:850;color:var(--navy);margin-bottom:10px}.tiny{font-size:12px;color:var(--muted)}.big{font-size:20px;font-weight:850;color:var(--navy);overflow-wrap:anywhere}
.feature-title{font-weight:850;color:var(--navy);margin:7px 0}.feature-copy{font-size:13px;color:var(--muted);line-height:1.55}.feature-icon{font-size:28px}
.status{display:inline-flex;padding:8px 13px;border-radius:12px;background:#e7f7ec;color:#087b36;font-weight:750}.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:18px 0}.kpi{border-right:1px solid var(--line)}
.partrow{display:grid;grid-template-columns:65px 1fr 140px;align-items:center;border-top:1px solid var(--line);padding-top:17px}.disc{width:55px;height:55px;border-radius:50%;background:radial-gradient(circle,#f1f2f3 0 18%,#8e949b 19% 25%,#d6d9dc 26% 57%,#7d838b 58% 64%,#d8dadd 65%)}
.timeline{margin:18px 0 4px 13px;padding-left:26px;overflow:hidden}.step{position:relative;padding:0 0 22px 8px;border-left:2px solid #d8dee8;min-width:0}.timeline>.step:last-child{border-left:2px solid transparent;padding-bottom:2px}.timeline>.step:last-child::before{content:"";position:absolute;left:-2px;top:0;width:2px;height:15px;background:#d8dee8}.dot{position:absolute;left:-15px;top:-1px;width:24px;height:24px;border-radius:50%;background:#aeb5c0;border:4px solid white;flex-shrink:0;box-sizing:border-box}.done .dot{background:#11a04b}.active .dot{background:#0667d9}.label{font-weight:760;color:var(--ink);overflow-wrap:anywhere;word-break:break-word;line-height:1.35}.meta{font-size:12px;color:#7b8698;overflow-wrap:anywhere}.note{padding:13px 0;border-bottom:1px solid var(--line)}.footer{background:linear-gradient(90deg,#002c61,#001638);color:white;padding:19px 25px;border-radius:16px;margin-top:20px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
 [data-testid="stColumn"]{min-width:0;overflow:hidden}.card{min-width:0;overflow:hidden;overflow-wrap:anywhere}
@media(max-width:900px){.hero{min-height:610px}.hero-copy{width:87%}.hero-copy h1{font-size:40px}.kpis{grid-template-columns:1fr}.partrow{grid-template-columns:60px 1fr}}
</style>
""", unsafe_allow_html=True)

def data_uri(path):
    mime = "image/png" if str(path).lower().endswith(".png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()

def go(page):
    st.session_state.page = page

def logout():
    st.session_state.logged_in = False
    st.session_state.page = "home"

def navbar():
    cols = st.columns([3.5,1,1.25,1,0.8,1.2], gap="small")
    logo = data_uri(ASSETS / "vw_logo.png")
    with cols[0]: st.markdown(f'<div class="brand"><img src="{logo}">Volkswagen</div>', unsafe_allow_html=True)
    with cols[1]: st.button("Home", key="nav_home", use_container_width=True, on_click=go, args=("home",))
    with cols[2]: st.button("How It Works", key="nav_how", use_container_width=True, on_click=go, args=("how",))
    with cols[3]: st.button("Support", key="nav_support", use_container_width=True, on_click=go, args=("support",))
    with cols[4]: st.button("FAQ", key="nav_faq", use_container_width=True, on_click=go, args=("faq",))
    with cols[5]:
        if st.session_state.logged_in:
            st.button("Sign Out", key="nav_logout", type="primary", use_container_width=True, on_click=logout)
        else:
            st.markdown('<div style="padding:10px 0;text-align:right;color:#001e50;font-weight:800">Move Forward.</div>', unsafe_allow_html=True)
    st.markdown('<div class="navline"></div>', unsafe_allow_html=True)

def render_home():
    car = data_uri(ASSETS / "polo_gti.jpg")
    left, right = st.columns([1.55, .72], gap="large")
    with left:
        st.markdown(f'''<div class="hero"><img src="{car}"><div class="overlay"></div><div class="hero-copy"><div class="eyebrow">GENUINE PARTS. GREATER JOURNEYS.</div><h1>Volkswagen<br>Parts Tracker</h1><div class="lead">Stay informed, wherever your part is.</div><p class="copy">Track your Volkswagen genuine parts order using a simple, transparent customer experience.</p></div></div>''', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card"><div class="page-title" style="font-size:32px">Welcome Back</div><div class="sub">Track your parts order</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email address", value=DEMO_EMAIL)
            password = st.text_input("Password", value=DEMO_PASSWORD, type="password")
            st.checkbox("Remember me")
            submit = st.form_submit_button("Sign In →", use_container_width=True)
        if submit:
            if email.strip().lower() == DEMO_EMAIL and password == DEMO_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Incorrect demo details. Use the credentials shown below.")
        st.markdown('<div style="text-align:center;color:#667085;padding:8px 0">or</div>', unsafe_allow_html=True)
        if st.button("📦 Track Order Without Login", key="guest", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.page = "dashboard"
            st.rerun()
        st.caption("Demo: customer@demo.co.za / Track123")
        st.markdown('<div class="card" style="margin-top:18px;box-shadow:none"><div class="feature-title">🛡 Your information is safe with us.</div><div class="feature-copy">This prototype uses synthetic customer and order data.</div></div></div>', unsafe_allow_html=True)
    st.write("")
    items=[("⌕","Real-Time Tracking","See the current demo milestone."),("🔔","Instant Notifications","Review simulated order updates."),("🛡","Genuine Parts","A customer-focused experience."),("◉","Better Together","Keeping customers informed.")]
    for col,item in zip(st.columns(4,gap="medium"),items):
        with col: st.markdown(f'<div class="card"><div class="feature-icon">{item[0]}</div><div class="feature-title">{item[1]}</div><div class="feature-copy">{item[2]}</div></div>',unsafe_allow_html=True)

def render_info(page):
    pages={
      "how":("How It Works","Track a customer parts order in three simple steps",[("1","Sign in","Use the demo customer account or guest tracking."),("2","Open the order","View the part, dealer, ETA and status."),("3","Follow the journey","Review milestones, notifications and the interactive map.")]),
      "support":("Support","Help for the customer tracking experience",[("☎","Dealer support","Contact the dealer about the order or collection."),("✉","Customer support","Request help with the tracking experience."),("⌕","Order help","Have the order number available when requesting help.")]),
      "faq":("Frequently Asked Questions","Quick answers about this demonstration",[("?","Is the tracking live?","No. Locations and movement are synthetic demonstration data."),("?","Can I enter without login?","Yes. Select Track Order Without Login on Home."),("?","Is it connected to production?","No. This prototype has no production integration.")])}
    title,sub,cards=pages[page]
    st.markdown(f'<div class="page-title">{title}</div><div class="sub">{sub}</div>',unsafe_allow_html=True)
    st.write("")
    for col,item in zip(st.columns(3,gap="large"),cards):
        with col: st.markdown(f'<div class="card"><div class="feature-icon">{item[0]}</div><div class="feature-title">{item[1]}</div><div class="feature-copy">{item[2]}</div></div>',unsafe_allow_html=True)
    st.write("")
    st.button("← Back to Home", key=f"back_{page}", on_click=go, args=("home",))

def render_dashboard():
    if not st.session_state.logged_in:
        go("home"); st.rerun()
    st.markdown('<div class="page-title">Welcome back, Customer</div><div class="sub">Track the latest simulated journey update.</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown(f'''<div class="card"><div style="display:flex;justify-content:space-between"><div><div class="tiny">Order number</div><div class="big">{ORDER['number']}</div></div><div class="status">🚚 {ORDER['status']}</div></div><div class="kpis"><div class="kpi"><div class="tiny">Order date</div><b>{ORDER['date']}</b></div><div class="kpi"><div class="tiny">Expected arrival</div><b>{ORDER['eta']}</b></div><div><div class="tiny">Dealer</div><b>{ORDER['dealer']}</b></div></div><div class="partrow"><div class="disc"></div><div><div class="big">{ORDER['part']}</div><div class="tiny">{ORDER['part_no']}<br>Quantity: {ORDER['quantity']}</div></div><b>Genuine Parts</b></div></div>''',unsafe_allow_html=True)
    st.write("")
    left,mid,right=st.columns([1,1.45,1],gap="large")
    steps=[('done','Order Received','12 Oct 2026, 09:14'),('done','Order Approved','12 Oct 2026, 11:20'),('done','Picked from Warehouse','13 Oct 2026, 08:45'),('active','In Transit','14 Oct 2026, 10:30'),('','Arrived at Dealer','Estimated 18 Oct 2026'),('','Ready for Collection','Pending dealer confirmation')]
    timeline='<div class="card"><div class="section">Tracking Journey</div><div class="timeline">'+''.join(f'<div class="step {c}"><span class="dot"></span><div class="label">{l}</div><div class="meta">{m}</div></div>' for c,l,m in steps)+'</div></div>'
    left.markdown(timeline,unsafe_allow_html=True)
    with mid:
        with st.container(border=True):
            st.markdown('<div class="section">Interactive Map</div><div class="tiny">Synthetic route for demonstration only.</div>',unsafe_allow_html=True)
            path=[{"path":ROUTE[["lon","lat"]].values.tolist()}]
            layers=[pdk.Layer("PathLayer",path,get_path="path",get_color=[0,104,216],width_min_pixels=5),pdk.Layer("ScatterplotLayer",ROUTE,get_position="[lon,lat]",get_fill_color=[0,30,80],get_radius=25000,pickable=True)]
            deck=pdk.Deck(map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",initial_view_state=pdk.ViewState(latitude=-30,longitude=27.1,zoom=4.4),layers=layers,tooltip={"text":"{kind}\n{name}"})
            st.pydeck_chart(deck,use_container_width=True,height=390)
            st.markdown(f'<div class="tiny">Current location</div><b>{ORDER["location"]}</b><div class="tiny">Updated {ORDER["updated"]}</div>',unsafe_allow_html=True)
    right.markdown('''<div class="card"><div class="section">Notifications</div><div class="note"><b>🚚 Your part is on the way</b><div class="tiny">Currently in transit to the dealer.</div></div><div class="note"><b>📦 Picked from warehouse</b><div class="tiny">Prepared for dispatch.</div></div><div class="note"><b>✓ Order approved</b><div class="tiny">The part was confirmed and reserved.</div></div><div class="section" style="margin-top:22px">Need help?</div><div class="tiny">Use Support in the navigation.</div></div>''',unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page="home"
if "logged_in" not in st.session_state: st.session_state.logged_in=False
navbar()
page=st.session_state.page
if page=="home": render_home()
elif page in ("how","support","faq"): render_info(page)
elif page=="dashboard": render_dashboard()
else: go("home"); st.rerun()
st.markdown('<div class="footer"><b>Volkswagen Parts Tracker Demo</b></div>',unsafe_allow_html=True)
