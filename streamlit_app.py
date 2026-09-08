import streamlit as st
import os
import requests  
import random    

# --- 1. ABLAK ALAPBEÁLLÍTÁSAI ÉS CSS TRÜKKÖK A GAP ÖSSZENYOMÁSÁRA ---
st.set_page_config(page_title="PPD - Personal Pocket Dictionary", layout="centered")

# Ezzel a kis kóddal kényszerítjük a címet egy sorba, és összenyomjuk a gombok közötti üres teret
st.markdown("""
    <style>
    /* Egy soros, elegáns főcím */
    .egy-soros-cim {
        text-align: center; 
        color: #FFFFFF; 
        font-size: 28px; 
        font-weight: 600;
        margin-bottom: 5px;
        white-space: nowrap;
    }
    /* A választógombok alatti óriási rés (gap) minimalizálása */
    div[data-testid="stRadio"] {
        margin-bottom: -15px !important;
    }
    /* Általános térközcsökkentés az elemek között */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }
    hr {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. KÉRÉS JAVÍTÁSA: Gyönyörű egy soros cím
st.markdown("<div class='egy-soros-cim'>📇 PPD - Personal Pocket Dictionary</div>", unsafe_allow_html=True)

# --- 2. FÁJL ALAPÚ ADATBÁZIS ---
FAJL_NEV = "szavak.txt"

def szotat_betolt():
    alap_szavak = [
        {"idegen": "apple", "magyar": "alma"},
        {"idegen": "train", "magyar": "vonat"},
        {"idegen": "pocket", "magyar": "zseb"},
        {"idegen": "dictionary", "magyar": "szótár"}
    ]
    if not os.path.exists(FAJL_NEV):
        return alap_szavak
    szavak = list(alap_szavak)
    with open(FAJL_NEV, "r", encoding="utf-8") as f:
        for sor in f:
            if ";" in sor:
                reszek = sor.strip().split(";")
                if len(reszek) == 2:
                    szavak.append({"idegen": reszek[0].strip(), "magyar": reszek[1].strip()})
    return szavak

def szotat_ujrair(teljes_lista):
    alap_idegenek = ["apple", "train", "pocket", "dictionary"]
    with open(FAJL_NEV, "w", encoding="utf-8") as f:
        for szo in teljes_lista:
            if szo["idegen"].lower() not in alap_idegenek:
                f.write(f"{szo['idegen']};{szo['magyar']}\n")

def szo_ment(idegen, magyar):
    with open(FAJL_NEV, "a", encoding="utf-8") as f:
        f.write(f"{idegen.strip()};{magyar.strip()}\n")

if "szotarfuzet" not in st.session_state:
    st.session_state.szotarfuzet = szotat_betolt()

if "kerdes_szamlalo" not in st.session_state:
    st.session_state.kerdes_szamlalo = 0
if "kereso_szamlalo" not in st.session_state:
    st.session_state.kereso_szamlalo = 0

# --- 3. Tab elrendezés ---
tab_fuzet, tab_kikerdezo = st.tabs(["📝 Szótárfüzetem", "🧠 Kikérdező Játék"])

# =================================================================
# 1. TAB: SZÓTÁRFÜZET NÉZET (Összenyomott, szűkített résekkel)
# =================================================================
with tab_fuzet:
    # 1. KÉRÉS JAVÍTÁSA: Szuper kompakt üzemmód- és irányválasztó sáv
    fuzet_uzemmod = st.radio(
        "Füzet üzemmódja:",
        ["🔍 Betekintő mód (Olvasás)", "🛠️ Törlő mód (Szerkesztés)"],
        horizontal=True
    )
    
    fuzet_irany = st.radio(
        "Adatbevitel és keresés módja:", 
        ["Angol szó keresése / beírása", "Magyar szó keresése / beírása"], 
        horizontal=True
    )

    if fuzet_irany == "Magyar szó keresése / beírása":
        st.info("💡 Az online szótár funkció csak angol-magyar irányban működik.")

    st.write("") # minimális helyköz a beviteli mező előtt
    sor_hasab1, sor_hasab2 = st.columns(2)
    with sor_hasab1:
        uj_szo = st.text_input(
            "Írd be a szót:", 
            key=f"kereso_{st.session_state.kereso_szamlalo}",
            label_visibility="collapsed"
        )
    with sor_hasab2:
        if st.button("❌ Törlés", use_container_width=True):
            st.session_state.kereso_szamlalo += 1
            st.rerun()

    if uj_szo:
        if fuzet_irany == "Angol szó keresése / beírása":
            talalat = [szo for szo in st.session_state.szotarfuzet if szo["idegen"].lower() == uj_szo.lower().strip()]
        else:
            talalat = [szo for szo in st.session_state.szotarfuzet if szo["magyar"].lower() == uj_szo.lower().strip()]
        
        if talalat:
            parja = talalat[0]["magyar"] if fuzet_irany == "Angol szó keresése / beírása" else talalat[0]["idegen"]
            st.success(f"🎉 Ez a szó már szerepel a füzetedben! Párja: **{parja}**")
        else:
            st.info(f"🔍 '{uj_szo}' még nincs a füzetben.")
            if fuzet_irany == "Angol szó keresése / beírása":
                st.write("🔄 Keresés az online szótárban...")
                url = f"https://dictionaryapi.dev{uj_szo}"
                try:
                    valasz = requests.get(url, timeout=3)
                    if valasz.status_code == 200:
                        adat = valasz.json()
                        angol_def = adat['meanings']['definitions']['definition']
                        st.write(f"📖 **Online angol jelentés:** *{angol_def}*")
                    else:
                        st.warning("⚠️ Nem találtam automatikus definíciót ehhez a szóhoz.")
                except Exception as e:
                    st.error("❌ Az online szótár nem elérhető időtúllépés miatt.")
            
            cimke = "Írd ide a magyar jelentését:" if fuzet_irany == "Angol szó keresése / beírása" else "Írd be az angol megfelelőjét:"
            hianyozo_par = st.text_input(cimke, key="hianyozo_par_input")
            
            if hianyozo_par and st.button("➕ Mentés a PPD-be"):
                if fuzet_irany == "Angol szó keresése / beírása":
                    angol_ment = uj_szo
                    magyar_ment = hianyozo_par
                else:
                    angol_ment = hianyozo_par
                    magyar_ment = uj_szo
                
                st.session_state.szotarfuzet.append({"idegen": angol_ment, "magyar": magyar_ment})
                szo_ment(angol_ment, magyar_ment)
                st.success("Sikeresen elmentve!")
                st.session_state.kereso_szamlalo += 1
                st.rerun()

    st.write("---")
    st.write("### 📝 Szótárfüzetem tartalma")
    
    if fuzet_uzemmod == "🔍 Betekintő mód (Olvasás)":
        hasab1, hasab2 = st.columns(2)
        with hash1 if 'hash1' in locals() else hasab1: st.markdown("**Idegen szó (Angol)**")
        with hasab2: st.markdown("**Magyar jelentés**")
        st.write("---")
        for szo in st.session_state.szotarfuzet:
            sor1, sor2 = st.columns(2)
            with sor1: st.write(szo["idegen"])
            with sor2: st.write(szo["magyar"])
    else:
        # BAKI JAVÍTVA: habit helyett tökéletes hasab2 változó!
        hasab1, hasab2, hasab3 = st.columns(3)
        with hasab1: st.markdown("**Idegen szó (Angol)**")
        with hasab2: st.markdown("**Magyar jelentés**")
        with hasab3: st.markdown("**Művelet**")
        st.write("---")
        
        for idx, szo in enumerate(st.session_state.szotarfuzet):
            sor1, sor2, sor3 = st.columns(3)
            with sor1: st.write(szo["idegen"])
            with sor2: st.write(szo["magyar"])
            with sor3:
                if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                    st.session_state.szotarfuzet.pop(idx)
                    szotat_ujrair(st.session_state.szotarfuzet)
                    st.rerun()
# =================================================================
# 2. TAB: KIKÉRDEZŐ MODUL (Atombiztos, ugrásmentesített verzió)
# =================================================================
with tab_kikerdezo:
    st.subheader("Teszteld a tudásod!")
    
    if len(st.session_state.szotarfuzet) < 4:
        st.warning("A kikérdezéshez least 4 szó kell a füzetbe!")
    else:
        valaszto_hasab1, valaszto_hasab2 = st.columns(2)
        
        with valaszto_hasab1:
            irany = st.radio(
                "Válassz tesztelési irányt:", 
                ["Magyarról ➡️ Angolra", "Angolról ➡️ Magyarra"], 
                horizontal=False, 
                on_change=lambda: st.session_state.pop("aktualis_kerdes", None),
                key="jatek_irany_radio"
            )
            
        with valaszto_hasab2:
            mod = st.radio(
                "Válassz játékmódot:", 
                ["Kvíz (A,B,C,D)", "Bepötyögős teszt"], 
                horizontal=False, 
                key="jatek_mod_radio"
            )

        if "aktualis_kerdes" not in st.session_state:
            st.session_state.aktualis_kerdes = random.choice(st.session_state.szotarfuzet)
            kerdes = st.session_state.aktualis_kerdes
            
            helyes_valasz = kerdes["idegen"] if irany == "Magyarról ➡️ Angolra" else kerdes["magyar"]
            
            if irany == "Magyarról ➡️ Angolra":
                rosszak = [s["idegen"] for s in st.session_state.szotarfuzet if s["idegen"] != helyes_valasz]
            else:
                rosszak = [s["magyar"] for s in st.session_state.szotarfuzet if s["magyar"] != helyes_valasz]

            opciok = [helyes_valasz] + random.sample(rosszak, min(3, len(rosszak)))
            random.shuffle(opciok)
            
            st.session_state.kviz_opciok = opciok
            st.session_state.valaszolt = False
            st.session_state.visszajelzes = ""

        kerdes = st.session_state.aktualis_kerdes
        st.write("---")
        
        # Keskeny felső információs sáv
        sor_info1, sor_info2 = st.columns(2)
        with sor_info1:
            if irany == "Magyarról ➡️ Angolra":
                helyes_vegso = kerdes["idegen"]
                st.write("📖 **Hogyan mondod angolul ezt a szót?**")
            else:
                helyes_vegso = kerdes["magyar"]
                st.write("📖 **Mit jelent magyarul ez a szó?**")
                
        with sor_info2:
            # Letisztult, dobozmentes szöveges visszajelzés felül, ami nem ugrik
            if st.session_state.valaszolt:
                if st.session_state.visszajelzes == "helyes":
                    st.markdown("<span style='color: #00FF7F; font-weight: bold;'>🎉 Helyes!</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: #FF4500; font-weight: bold;'>❌ Rossz! 👉 {helyes_vegso}</span>", unsafe_allow_html=True)

        st.markdown(f"<h1 style='text-align: center; color: #1E90FF; font-size: 40px; margin-top: 5px; margin-bottom: 5px;'>{kerdes['magyar'] if irany == 'Magyarról ➡️ Angolra' else kerdes['idegen']}</h1>", unsafe_allow_html=True)
        st.write("") 

        # --- FIX HELYFOGLALÓ MECHANIZMUS ---
        # A gomb fixen ott van a képernyőn, ha nem válaszoltál, láthatatlan de tartja a helyet!
        if not st.session_state.valaszolt:
            # Egy teljesen inaktív, szürke gomb, ami pontosan akkora helyet foglal el, mint a piros gomb
            st.button("Következő szó ➡️", key="kov_placeholder", disabled=True, use_container_width=True)
        else:
            # Amikor válaszoltál, ez a gomb azonnal aktívvá és pirossá (primary) válik, a helye megegyezik!
            if st.button("Következő szó ➡️", key="kov_aktiv", type="primary", use_container_width=True):
                del st.session_state.aktualis_kerdes
                st.session_state.kerdes_szamlalo += 1  
                st.rerun()

        st.write("") 

        if mod == "Kvíz (A,B,C,D)":
            st.write("Válaszd ki a helyes megoldást:")
            for opcio in st.session_state.kviz_opciok:
                if st.button(f"🔹 {opcio}", key=f"btn_{opcio}", use_container_width=True):
                    if not st.session_state.valaszolt:
                        st.session_state.valaszolt = True
                        if opcio == helyes_vegso:
                            st.session_state.visszajelzes = "helyes"
                        else:
                            st.session_state.visszajelzes = "hibas"
                        st.rerun()
        else:
            tipp = st.text_input(
                "Írd be a megfelelőt:", 
                key=f"bepotyogos_tipp_{st.session_state.kerdes_szamlalo}"
            )
            if tipp and not st.session_state.valaszolt:
                st.session_state.valaszolt = True
                if tipp.lower().strip() == helyes_vegso.lower().strip():
                    st.session_state.visszajelzes = "helyes"
                else:
                    st.session_state.visszajelzes = "hibas"
                st.rerun()
