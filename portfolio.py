import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(page_title="Portfolio Tracker", layout="wide", page_icon="📊")

CMC_API_KEY = "3c8b3b52fbd2427ca854b66233e9f1f9"

@st.cache_data(ttl=300)
def get_tasso_cambio():
    try:
        t = yf.Ticker("EURUSD=X")
        h = t.history(period="5d")
        return float(h['Close'].dropna().iloc[-1])
    except:
        return 1.1782

@st.cache_data(ttl=300)
def get_prezzi(tickers):
    risultati = {}
    for tk in tickers:
        try:
            h = yf.Ticker(tk).history(period="2d")
            val = h['Close'].dropna().iloc[-1]
            risultati[tk] = float(val)
        except:
            risultati[tk] = 0.0
    return risultati

@st.cache_data(ttl=300)
def get_storico(ticker, periodo="5y"):
    try:
        h = yf.Ticker(ticker).history(period=periodo)
        return h['Close'].dropna()
    except:
        return None

@st.cache_data(ttl=300)
def get_crypto(symbols):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": ",".join(symbols), "convert": "USD"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        return r.json()
    except:
        return None

IB = {
    "TSLA":  {"q": 5,   "costo": 209.53, "v": "USD"},
    "UBER":  {"q": 31,  "costo": 72.34,  "v": "USD"},
    "MSFT":  {"q": 20,  "costo": 358.00, "v": "USD"},
    "AAPL":  {"q": 14,  "costo": 162.18, "v": "USD"},
    "GOOGL": {"q": 35,  "costo": 123.10, "v": "USD"},
    "NVDA":  {"q": 50,  "costo": 49.10,  "v": "USD"},
    "AXP":   {"q": 6,   "costo": 150.83, "v": "USD"},
    "V":     {"q": 5,   "costo": 209.53, "v": "USD"},
    "SMR":   {"q": 200, "costo": 18.07,  "v": "USD"},
    "SOFI":  {"q": 100, "costo": 19.14,  "v": "USD"},
    "ADBE":  {"q": 7,   "costo": 385.00, "v": "USD"},
    "VST":   {"q": 13,  "costo": 150.62, "v": "USD"},
}
IB_LIQ_USD = 157.44

FINECO = {
    "IB1T-ETFP.MI": {"q": 248, "costo": 6.65,  "v": "EUR"},
    "VUSA.MI":       {"q": 535, "costo": 66.69, "v": "EUR"},
    "VUAA.MI":       {"q": 88,  "costo": 71.51, "v": "EUR"},
}
FINECO_LIQ_EUR = 11124.49

TFR_LIQ_USD = 107363.22
RE_LIQ_USD   = 235963.13

CRYPTO_LIST = [
    {"nome": "Bitcoin",           "sym": "BTC",    "q": 0.15,        "c": 43132.90},
    {"nome": "Ethereum",          "sym": "ETH",    "q": 2.37,        "c": 2269.33},
    {"nome": "Dogecoin",          "sym": "DOGE",   "q": 10081.00,    "c": 0.09191},
    {"nome": "Cronos",            "sym": "CRO",    "q": 13079.87,    "c": 0.1003},
    {"nome": "Sui",               "sym": "SUI",    "q": 715.36,      "c": 1.6423},
    {"nome": "Aerodrome Finance", "sym": "AERO",   "q": 1252.55,     "c": 0.9575},
    {"nome": "Shiba Inu",         "sym": "SHIB",   "q": 60391497.00, "c": 0.00001135},
    {"nome": "Kaspa",             "sym": "KAS",    "q": 10668.00,    "c": 0.1684},
    {"nome": "ASI Alliance",      "sym": "FET",    "q": 1254.28,     "c": 1.3214},
    {"nome": "Nexo",              "sym": "NEXO",   "q": 206.13,      "c": 1.0249},
    {"nome": "Ondo",              "sym": "ONDO",   "q": 633.00,      "c": 1.1388},
    {"nome": "Render",            "sym": "RENDER", "q": 62.21,       "c": 7.2133},
    {"nome": "Ocean Protocol",    "sym": "OCEAN",  "q": 634.29,      "c": 0.761},
    {"nome": "SingularityNET",    "sym": "AGIX",   "q": 647.58,      "c": 0.6598},
    {"nome": "Immutable",         "sym": "IMX",    "q": 342.57,      "c": 2.2824},
    {"nome": "Celestia",          "sym": "TIA",    "q": 83.63,       "c": 5.5378},
    {"nome": "Solama",            "sym": "SLAMA",  "q": 10715.00,    "c": 0.02397},
    {"nome": "Myro",              "sym": "MYRO",   "q": 2631.00,     "c": 0.1572},
    {"nome": "TRUMP",             "sym": "TRUMP",  "q": 1.80,        "c": 67.60},
    {"nome": "XEN Crypto",        "sym": "XEN",    "q": 7473641.00,  "c": 0.0000003966},
]

def d(val_usd, eur, tc):
    return val_usd / tc if eur else val_usd

def f(val_usd, eur, tc):
    v = d(val_usd, eur, tc)
    s = "€" if eur else "$"
    return f"{s}{v:,.2f}"

tc = get_tasso_cambio()

all_tickers = list(IB.keys()) + list(FINECO.keys())
with st.spinner("⏳ Scarico prezzi..."):
    prezzi = get_prezzi(all_tickers)
    cmc = get_crypto([c["sym"] for c in CRYPTO_LIST])

if "eur" not in st.session_state:
    st.session_state.eur = False
eur = st.session_state.eur
sim = "€" if eur else "$"

def calc_ib_usd():
    tot = IB_LIQ_USD
    for tk, info in IB.items():
        tot += prezzi.get(tk, 0) * info["q"]
    return tot

def calc_fineco_usd():
    tot = FINECO_LIQ_EUR * tc
    for tk, info in FINECO.items():
        tot += prezzi.get(tk, 0) * info["q"] * tc
    return tot

ib_usd     = calc_ib_usd()
fineco_usd = calc_fineco_usd()
tfr_usd    = TFR_LIQ_USD
re_usd     = RE_LIQ_USD

crypto_usd = 0
crypto_rows = []
if cmc and "data" in cmc:
    for c in CRYPTO_LIST:
        if c["sym"] in cmc["data"]:
            p = cmc["data"][c["sym"]]["quote"]["USD"]["price"]
            v = p * c["q"]
            crypto_usd += v
            co = c["c"] * c["q"]
            pnl = v - co
            pnl_pct = pnl / co * 100 if co > 0 else 0
            crypto_rows.append({
                "Nome": c["nome"], "Symbol": c["sym"], "Quantità": c["q"],
                "Prezzo ($)": round(p, 6),
                f"Valore ({sim})": round(d(v, eur, tc), 2),
                f"Costo ({sim})": round(d(co, eur, tc), 2),
                f"P&L ({sim})": round(d(pnl, eur, tc), 2),
                "P&L (%)": round(pnl_pct, 2),
            })

tot_usd = ib_usd + fineco_usd + tfr_usd + re_usd + crypto_usd

st.title("📊 Portfolio Tracker — Tommaso")
st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')} · EUR/USD: {tc:.4f}")

if st.button("💱 Mostra in EUR" if not eur else "💱 Mostra in USD"):
    st.session_state.eur = not st.session_state.eur
    st.rerun()

c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("💰 Totale",      f(tot_usd,     eur, tc))
c2.metric("📈 IB",          f(ib_usd,      eur, tc))
c3.metric("📊 Fineco",      f(fineco_usd,  eur, tc))
c4.metric("💼 TFR",         f(tfr_usd,     eur, tc))
c5.metric("🏠 Real Estate", f(re_usd,      eur, tc))
c6.metric("₿ Crypto",       f(crypto_usd,  eur, tc))

st.divider()

tabs = st.tabs(["📈 Tommy IB","📊 Tommy Fineco","💼 Tommy TFR","🏠 Real Estate","₿ Crypto","📋 Riepilogo"])

def render_titoli(titoli, prezzi, liq_usd, colore, nome, tc, eur, con_200w=False):
    sim = "€" if eur else "$"
    rows = []
    tot_titoli_usd = 0
    for tk, info in titoli.items():
        p = prezzi.get(tk, 0)
        if info["v"] == "EUR":
            val_usd = p * info["q"] * tc
            costo_usd = info["costo"] * info["q"] * tc
        else:
            val_usd = p * info["q"]
            costo_usd = info["costo"] * info["q"]
        tot_titoli_usd += val_usd
        pnl_usd = val_usd - costo_usd
        pnl_pct = pnl_usd / costo_usd * 100 if costo_usd > 0 else 0
        rows.append({
            "Ticker": tk,
            "Qtà": info["q"],
            f"Prezzo ({info['v']})": round(p, 4),
            f"Valore ({sim})": round(d(val_usd, eur, tc), 2),
            f"Costo ({sim})": round(d(costo_usd, eur, tc), 2),
            f"P&L ({sim})": round(d(pnl_usd, eur, tc), 2),
            "P&L (%)": round(pnl_pct, 2),
        })

    df = pd.DataFrame(rows)
    tot_usd = tot_titoli_usd + liq_usd

    col1,col2,col3 = st.columns(3)
    col1.metric("Valore totale", f(tot_usd, eur, tc))
    col2.metric("Titoli", f(tot_titoli_usd, eur, tc))
    col3.metric("Liquidità", f(liq_usd, eur, tc))

    if len(df) > 0:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, values=f"Valore ({sim})", names="Ticker",
                        title="Allocazione", color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(df, x="Ticker", y="P&L (%)", title="Performance (%)",
                         color="P&L (%)", color_continuous_scale=["red","yellow","green"])
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df, use_container_width=True, hide_index=True)

        tk_lista = df["Ticker"].tolist()
        t_sel = st.selectbox("📈 Scegli titolo per grafico", tk_lista, key=f"sel_{nome}")
        storico = get_storico(t_sel, "5y" if con_200w else "2y")
        if storico is not None and len(storico) > 0:
            s = storico.reset_index()
            s.columns = ["Data", "Prezzo"]
            if con_200w:
                s["200W MA"] = s["Prezzo"].rolling(window=1000).mean()
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=s["Data"], y=s["Prezzo"],
                                         name="Prezzo", line=dict(color=colore, width=1.5)))
                fig3.add_trace(go.Scatter(x=s["Data"], y=s["200W MA"],
                                         name="200-Week MA", line=dict(color="orange", dash="dash", width=2)))
                fig3.update_layout(title=f"{t_sel} — Prezzo + 200-Week MA", hovermode="x unified")
            else:
                fig3 = px.line(s, x="Data", y="Prezzo", title=f"{t_sel} — ultimi 2 anni")
                fig3.update_traces(line_color=colore)
            st.plotly_chart(fig3, use_container_width=True)

with tabs[0]:
    st.subheader("📈 Tommy IB — Interactive Brokers")
    render_titoli(IB, prezzi, IB_LIQ_USD, "#2196F3", "IB", tc, eur, con_200w=True)

with tabs[1]:
    st.subheader("📊 Tommy Fineco")
    render_titoli(FINECO, prezzi, FINECO_LIQ_EUR * tc, "#4CAF50", "Fineco", tc, eur, con_200w=False)

with tabs[2]:
    st.subheader("💼 Tommy TFR — Fondo Pensione")
    st.metric("Valore totale", f(TFR_LIQ_USD, eur, tc))
    st.info("Portafoglio composto da sola liquidità (FON.TE)")

with tabs[3]:
    st.subheader("🏠 Real Estate")
    st.metric("Valore totale", f(RE_LIQ_USD, eur, tc))
    st.info("Valore immobiliare stimato")

with tabs[4]:
    st.subheader("₿ Portfolio Crypto — CoinMarketCap")
    col1,col2,col3 = st.columns(3)
    col1.metric("Valore totale", f(crypto_usd, eur, tc))

    if crypto_rows:
        df_c = pd.DataFrame(crypto_rows)
        pnl_tot = sum(r[f"P&L ({sim})"] for r in crypto_rows)
        costo_tot = d(sum(c["c"]*c["q"] for c in CRYPTO_LIST), eur, tc)
        col2.metric(f"P&L totale", f"{sim}{pnl_tot:,.2f}")
        col3.metric("P&L %", f"{pnl_tot/costo_tot*100:.2f}%" if costo_tot else "N/A")

        col1, col2 = st.columns(2)
        with col1:
            df_pie = df_c[df_c[f"Valore ({sim})"] > 5]
            fig = px.pie(df_pie, values=f"Valore ({sim})", names="Nome",
                        title="Allocazione crypto", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(df_c.sort_values("P&L (%)"), x="Symbol", y="P&L (%)",
                         title="Performance crypto (%)",
                         color="P&L (%)", color_continuous_scale=["red","yellow","green"])
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.warning("Impossibile caricare prezzi crypto — verifica API key")

with tabs[5]:
    st.subheader("📋 Riepilogo patrimonio totale")
    colori = ["#2196F3","#4CAF50","#FF9800","#9C27B0","#F44336","#795548"]
    valori = {"Tommy IB": ib_usd, "Tommy Fineco": fineco_usd,
              "Tommy TFR": tfr_usd, "Real Estate": re_usd, "Crypto": crypto_usd}

    recap = [{"Portafoglio": n,
              f"Valore ({sim})": round(d(v, eur, tc), 2),
              "Allocazione (%)": round(v/tot_usd*100, 1)}
             for n, v in valori.items()]
    df_r = pd.DataFrame(recap)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df_r, values=f"Valore ({sim})", names="Portafoglio",
                    title=f"Allocazione patrimonio ({sim})", color_discrete_sequence=colori)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(df_r, x="Portafoglio", y=f"Valore ({sim})",
                     title=f"Valore per portafoglio ({sim})",
                     color="Portafoglio", color_discrete_sequence=colori)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📈 Crescita storica portafogli — ultimo anno")
    fig_cr = go.Figure()
    portafogli_storici = {
        "Tommy IB": (IB, IB_LIQ_USD, "#2196F3"),
        "Tommy Fineco": (FINECO, FINECO_LIQ_EUR * tc, "#4CAF50"),
    }
    for nome, (titoli, liq, col) in portafogli_storici.items():
        tks = list(titoli.keys())
        try:
            frames = []
            for tk in tks:
                h = yf.Ticker(tk).history(period="1y")['Close'].dropna()
                info = titoli[tk]
                if info["v"] == "EUR":
                    frames.append((h * info["q"] * tc).rename(tk))
                else:
                    frames.append((h * info["q"]).rename(tk))
            if frames:
                df_h = pd.concat(frames, axis=1).fillna(method='ffill').dropna()
                serie = df_h.sum(axis=1) + liq
                serie_disp = serie / tc if eur else serie
                fig_cr.add_trace(go.Scatter(
                    x=serie_disp.index, y=serie_disp.values,
                    name=nome, line=dict(color=col, width=2)
                ))
        except:
            pass

    fig_cr.update_layout(title=f"Crescita portafogli ({sim})",
                         xaxis_title="Data", yaxis_title=f"Valore ({sim})",
                         hovermode="x unified")
    st.plotly_chart(fig_cr, use_container_width=True)

    st.dataframe(df_r, use_container_width=True, hide_index=True)
    st.metric("💰 PATRIMONIO TOTALE", f(tot_usd, eur, tc))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Aggiorna prezzi"):
            st.cache_data.clear()
            st.rerun()
    st.caption("Prezzi aggiornati automaticamente ogni 5 minuti")