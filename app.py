import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🎾 Analyse de Match Tennis - Outil de Prédiction")

uploaded_file = st.file_uploader("📂 Importe ton fichier Excel Tennis", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=1)
    df = df.rename(columns={
        'J1': 'Cote_J1', 'J2': 'Cote_J2',
        'Set1 \nJ1': 'Set1_J1', 'Set1\nJ2': 'Set1_J2',
        'Score ': 'Score', 'Type de\ntournoi': 'Type_Tournoi'
    })

    for col in ['Cote_J1', 'Cote_J2', 'Set1_J1', 'Set1_J2']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in ['Type', 'Tournoi', 'Type_Tournoi', 'Surface', 'Rang', 'Joueur 1', 'Joueur 2']:
        df[col] = df[col].astype(str).str.strip()

    def get_unique_with_all(col):
        return ["Tous"] + sorted(df[col].dropna().unique())

    with st.sidebar:
        st.header("🧮 Filtrage Max")
        type_val = st.selectbox("Type", get_unique_with_all('Type'))
        tournoi = st.selectbox("Tournoi", get_unique_with_all('Tournoi'))
        type_tournoi = st.selectbox("Type Tournoi", get_unique_with_all('Type_Tournoi'))
        surface = st.selectbox("Surface", get_unique_with_all('Surface'))
        rang = st.selectbox("Rang", get_unique_with_all('Rang'))
        joueur1 = st.selectbox("Joueur 1", get_unique_with_all('Joueur 1'))
        joueur2 = st.selectbox("Joueur 2", get_unique_with_all('Joueur 2'))
        cote_j1 = st.selectbox("Cote Joueur 1", ["Tous"] + sorted(df['Cote_J1'].dropna().unique()))
        cote_j2 = st.selectbox("Cote Joueur 2", ["Tous"] + sorted(df['Cote_J2'].dropna().unique()))
        set1_j1 = st.selectbox("Cote Set1 J1", ["Tous"] + sorted(df['Set1_J1'].dropna().unique()))
        set1_j2 = st.selectbox("Cote Set1 J2", ["Tous"] + sorted(df['Set1_J2'].dropna().unique()))
        lancer = st.button("🚀 Analyser")

    if lancer:
        def determine_winner(score_str):
            try:
                sets = score_str.strip().split('-')
                return 'J1' if int(sets[0]) > int(sets[1]) else 'J2'
            except:
                return 'Inconnu'

        df['Gagnant'] = df['Score'].apply(determine_winner)

        filtres = {
            'Type': type_val,
            'Tournoi': tournoi,
            'Type_Tournoi': type_tournoi,
            'Surface': surface,
            'Rang': rang,
            'Joueur 1': joueur1,
            'Joueur 2': joueur2
        }

        df_filtered = df.copy()
        for col, val in filtres.items():
            if val != "Tous":
                df_filtered = df_filtered[df_filtered[col].str.lower().str.contains(val.lower(), na=False)]
        if cote_j1 != "Tous":
            df_filtered = df_filtered[df_filtered['Cote_J1'] == float(cote_j1)]
        if cote_j2 != "Tous":
            df_filtered = df_filtered[df_filtered['Cote_J2'] == float(cote_j2)]
        if set1_j1 != "Tous":
            df_filtered = df_filtered[df_filtered['Set1_J1'] == float(set1_j1)]
        if set1_j2 != "Tous":
            df_filtered = df_filtered[df_filtered['Set1_J2'] == float(set1_j2)]

        st.markdown("---")
        st.markdown("## 🔍 Résultats du Filtrage Max")
        st.info(f"**{len(df_filtered)} matchs trouvés**")

        if len(df_filtered) > 0:
            win_j1 = (df_filtered['Gagnant'] == 'J1').sum()
            win_j2 = (df_filtered['Gagnant'] == 'J2').sum()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Victoires Joueur 1", f"{win_j1} ({(win_j1 / len(df_filtered) * 100):.1f}%)")
            with col2:
                st.metric("Victoires Joueur 2", f"{win_j2} ({(win_j2 / len(df_filtered) * 100):.1f}%)")

            fig1, ax1 = plt.subplots()
            ax1.pie([win_j1, win_j2], labels=['Joueur 1', 'Joueur 2'], autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)

            scores = ['2-0', '2-1', '1-2', '0-2']
            score_counts = df_filtered['Score'].value_counts()
            values = [score_counts.get(s, 0) for s in scores]
            if sum(values) > 0:
                st.markdown("### 🎯 Répartition des scores exacts")
                fig2, ax2 = plt.subplots()
                ax2.pie(values, labels=scores, autopct='%1.1f%%', startangle=90)
                ax2.axis('equal')
                st.pyplot(fig2)

        # Appel à la fonction show_entonnoir
        from Synthese_Ia import show_entonnoir, show_stats_dynamiques, show_h2h, show_bo_stats, show_final_analysis
        # À insérer dans le bon ordre après le filtrage :
        show_entonnoir(df, filtres, cote_j1, cote_j2, set1_j1, set1_j2)
        show_stats_dynamiques(df, joueur1, joueur2, cote_j1, cote_j2, surface)
        show_h2h(df, joueur1, joueur2, surface)
        show_bo_stats(df, joueur1, joueur2, surface)
        show_final_analysis(df, joueur1, joueur2, cote_j1, cote_j2, set1_j1, set1_j2)


