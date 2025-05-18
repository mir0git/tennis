import streamlit as st

def show_entonnoir(df, filtres, cote_j1, cote_j2, set1_j1, set1_j2):
    st.markdown("---")
    st.markdown("## 📊 Analyse Entonnoir Complémentaire")

    entonnoir_combinations = [
        ['Type', 'Tournoi', 'Cote_J1'],
        ['Type', 'Tournoi', 'Cote_J2'],
        ['Type', 'Tournoi', 'Cote_J1', 'Set1_J1'],
        ['Type', 'Tournoi', 'Cote_J2', 'Set1_J2'],
        ['Joueur 1', 'Cote_J1'],
        ['Joueur 2', 'Cote_J2'],
        ['Surface', 'Cote_J1'],
        ['Type_Tournoi', 'Rang', 'Joueur 1'],
        ['Joueur 1', 'Joueur 2'],
        ['Type_Tournoi', 'Surface', 'Rang', 'Cote_J1', 'Cote_J2', 'Set1_J1', 'Set1_J2'],
        ['Type_Tournoi', 'Surface', 'Cote_J1', 'Cote_J2', 'Set1_J1', 'Set1_J2'],
        ['Joueur 1', 'Cote_J1', 'Surface'],
        ['Joueur 2', 'Cote_J2', 'Surface'],
        ['Type_Tournoi', 'Joueur 1', 'Cote_J1', 'Surface'],
        ['Type_Tournoi', 'Joueur 2', 'Cote_J2', 'Surface'],
        ['Tournoi', 'Cote_J1'],
        ['Tournoi', 'Cote_J2'],
        ['Tournoi', 'Joueur 1'],
        ['Tournoi', 'Joueur 2'],
        ['Tournoi', 'Rang', 'Cote_J1'],
        ['Tournoi', 'Rang', 'Cote_J2'],
        ['Tournoi', 'Rang', 'Joueur 1'],
        ['Tournoi', 'Rang', 'Joueur 2']
    ]

    n_cols = 3
    rows = [entonnoir_combinations[i:i+n_cols] for i in range(0, len(entonnoir_combinations), n_cols)]

    for row_combos in rows:
        cols = st.columns(len(row_combos))
        for col, combo in zip(cols, row_combos):
            df_main = df.copy()
            for col_filter in combo:
                if col_filter in filtres and filtres[col_filter] != "Tous":
                    df_main = df_main[df_main[col_filter].str.lower().str.contains(filtres[col_filter].lower(), na=False)]

            if 'Cote_J1' in combo and cote_j1 != "Tous":
                df_main = df_main[df_main['Cote_J1'] == float(cote_j1)]
            if 'Cote_J2' in combo and cote_j2 != "Tous":
                df_main = df_main[df_main['Cote_J2'] == float(cote_j2)]
            if 'Set1_J1' in combo and set1_j1 != "Tous":
                df_main = df_main[df_main['Set1_J1'] == float(set1_j1)]
            if 'Set1_J2' in combo and set1_j2 != "Tous":
                df_main = df_main[df_main['Set1_J2'] == float(set1_j2)]

            if len(df_main) > 0:
                with col.expander(f"📌 Combo: {', '.join(combo)}"):
                    win1 = (df_main['Gagnant'] == 'J1').sum()
                    win2 = (df_main['Gagnant'] == 'J2').sum()
                    st.markdown(f"- **{len(df_main)} matchs**")
                    st.markdown(f"- J1: {win1} ({win1 / len(df_main) * 100:.2f}%)")
                    st.markdown(f"- J2: {win2} ({win2 / len(df_main) * 100:.2f}%)")

                    # Ajout des sets gagnés
                    set_j1 = df_main['Score'].str.contains("2-1|2-0|1-0|1-2|0-1", na=False).sum()
                    set_j2 = df_main['Score'].str.contains("2-1|0-2|0-1|1-0|1-2", na=False).sum()
                    st.markdown(f"- Set gagné J1: {set_j1} ({(set_j1 / len(df_main)) * 100:.2f}%)")
                    st.markdown(f"- Set gagné J2: {set_j2} ({(set_j2 / len(df_main)) * 100:.2f}%)")



def show_stats_dynamiques(df, joueur1, joueur2, cote_j1, cote_j2, surface):
    st.markdown("---")
    st.markdown("## 📈 Statistiques Dynamiques des Joueurs")

    def show_player_stats(nom_joueur, cote, surface_select):
        df_joueur = df[((df['Joueur 1'].str.lower() == nom_joueur.lower()) & (df['Cote_J1'] == float(cote))) |
                       ((df['Joueur 2'].str.lower() == nom_joueur.lower()) & (df['Cote_J2'] == float(cote)))].copy()
        df_joueur['Est_J1'] = df_joueur['Joueur 1'].str.lower() == nom_joueur.lower()
        total = len(df_joueur)
        wins = ((df_joueur['Gagnant'] == 'J1') & (df_joueur['Est_J1'])) | \
               ((df_joueur['Gagnant'] == 'J2') & (~df_joueur['Est_J1']))
        wins = wins.sum()
        txt = f"{nom_joueur} avec sa cote ({cote}) → {total} matchs, {wins} victoires ({(wins/total*100 if total > 0 else 0):.2f}%)"
        st.markdown(f"- 🎾 {txt}")

        set_won = 0
        for score, estj1 in zip(df_joueur['Score'], df_joueur['Est_J1']):
            if isinstance(score, str):
                try:
                    s1, s2 = map(int, score.strip().split('-'))
                    if (estj1 and s1 >= 1) or (not estj1 and s2 >= 1):
                        set_won += 1
                except:
                    continue
        st.markdown(f"  - 🟩 A gagné au moins 1 set dans {set_won}/{total} matchs ({(set_won/total*100 if total > 0 else 0):.2f}%)")

        if surface_select:
            df_surface = df_joueur[df_joueur['Surface'].str.lower() == surface_select.lower()]
            total_surface = len(df_surface)
            wins_surface = ((df_surface['Gagnant'] == 'J1') & (df_surface['Est_J1'])) | \
                           ((df_surface['Gagnant'] == 'J2') & (~df_surface['Est_J1']))
            wins_surface = wins_surface.sum()
            txt2 = f"{nom_joueur} sur {surface_select} ({cote}) → {total_surface} matchs, {wins_surface} victoires ({(wins_surface/total_surface*100 if total_surface > 0 else 0):.2f}%)"
            st.markdown(f"- 🌍 {txt2}")

            set_won_surface = 0
            for score, estj1 in zip(df_surface['Score'], df_surface['Est_J1']):
                if isinstance(score, str):
                    try:
                        s1, s2 = map(int, score.strip().split('-'))
                        if (estj1 and s1 > 0) or (not estj1 and s2 > 0):
                            set_won_surface += 1
                    except:
                        continue
            st.markdown(f"  - 🟩 A gagné au moins 1 set sur {surface_select} dans {set_won_surface}/{total_surface} matchs ({(set_won_surface/total_surface*100 if total_surface > 0 else 0):.2f}%)")

    if joueur1 != "Tous" and cote_j1 != "Tous":
        show_player_stats(joueur1, cote_j1, surface if surface != "Tous" else None)
    if joueur2 != "Tous" and cote_j2 != "Tous":
        show_player_stats(joueur2, cote_j2, surface if surface != "Tous" else None)


def show_h2h(df, joueur1, joueur2, surface):
    st.markdown("---")
    st.markdown("## 💾 Historique Direct (H2H)")

    if joueur1 != "Tous" and joueur2 != "Tous":
        h2h = df[((df['Joueur 1'].str.lower() == joueur1.lower()) & (df['Joueur 2'].str.lower() == joueur2.lower())) |
                 ((df['Joueur 1'].str.lower() == joueur2.lower()) & (df['Joueur 2'].str.lower() == joueur1.lower()))]

        total_h2h = len(h2h)
        if total_h2h > 0:
            win_j1, win_j2 = 0, 0
            for _, row in h2h.iterrows():
                tournoi_h2h = row['Tournoi']
                surface_h2h = row['Surface']
                j1 = row['Joueur 1']
                j2 = row['Joueur 2']
                score = row['Score']
                gagnant = row['Gagnant']

                format_match = 'BO5' if 'grand chelem' in row['Type_Tournoi'].lower() else 'BO3'
                est_surface = surface.lower() == surface_h2h.lower() if surface != "Tous" else False

                annotation = []
                if est_surface:
                    annotation.append("🎾 Surface identique")
                annotation.append(format_match)

                extra_info = []
                if row['Rang']:
                    extra_info.append(f"Rang : {row['Rang']}")
                if row['Type_Tournoi']:
                    extra_info.append(f"Type : {row['Type_Tournoi']}")
                extra = f" ({', '.join(annotation + extra_info)})" if annotation or extra_info else ""
                st.markdown(f"- {tournoi_h2h} ({surface_h2h}) → {j1} vs {j2} : {score}{extra}")

                if gagnant == 'J1' and j1.lower() == joueur1.lower():
                    win_j1 += 1
                elif gagnant == 'J2' and j2.lower() == joueur1.lower():
                    win_j1 += 1
                elif gagnant == 'J1' and j1.lower() == joueur2.lower():
                    win_j2 += 1
                elif gagnant == 'J2' and j2.lower() == joueur2.lower():
                    win_j2 += 1

            st.markdown(f"### 📊 Bilan : {joueur1} {win_j1} - {win_j2} {joueur2}")
        else:
            st.info("Aucune confrontation directe trouvée.")

def show_bo_stats(df, joueur1, joueur2, surface):
    st.markdown("---")
    st.markdown("## 🔎 Analyse BO3 / BO5 sur la Surface du Match")

    h2h = df[((df['Joueur 1'].str.lower() == joueur1.lower()) & (df['Joueur 2'].str.lower() == joueur2.lower())) |
             ((df['Joueur 1'].str.lower() == joueur2.lower()) & (df['Joueur 2'].str.lower() == joueur1.lower()))]

    bo3_sets = bo3_over2sets = bo5_total = bo5_clean = 0
    for _, row in h2h.iterrows():
        score = row['Score']
        try:
            sets = list(map(int, score.strip().split("-")))
            total_sets = sum(sets)
            is_bo5 = 'grand chelem' in row['Type_Tournoi'].lower()
            if is_bo5:
                bo5_total += 1
                if total_sets == 3:
                    bo5_clean += 1
            else:
                bo3_sets += 1
                if total_sets > 2:
                    bo3_over2sets += 1
        except:
            continue

    if bo3_sets > 0:
        ratio = (bo3_over2sets / bo3_sets) * 100
        st.markdown(f"🔍 En BO3, {ratio:.1f}% des matchs sont allés au-delà de 2 sets ({bo3_over2sets}/{bo3_sets}).")
    if bo5_total > 0:
        clean = (bo5_clean / bo5_total) * 100
        st.markdown(f"🏆 En BO5, {clean:.1f}% des matchs se sont finis en 3-0 ({bo5_clean}/{bo5_total}).")

    if surface != "Tous":
        surface_h2h = h2h[h2h['Surface'].str.lower() == surface.lower()]
        surf_bo3 = surf_bo3_3sets = surf_bo5 = surf_bo5_3_0 = 0
        for _, row in surface_h2h.iterrows():
            try:
                sets = list(map(int, row['Score'].strip().split("-")))
                total_sets = sum(sets)
                is_bo5 = 'grand chelem' in row['Type_Tournoi'].lower()
                if is_bo5:
                    surf_bo5 += 1
                    if total_sets == 3:
                        surf_bo5_3_0 += 1
                else:
                    surf_bo3 += 1
                    if total_sets > 2:
                        surf_bo3_3sets += 1
            except:
                continue

        if surf_bo3 > 0:
            pct = surf_bo3_3sets / surf_bo3 * 100
            st.markdown(f"🎾 Sur {surface}, {pct:.1f}% des BO3 ont dépassé 2 sets ({surf_bo3_3sets}/{surf_bo3}).")
        if surf_bo5 > 0:
            pct = surf_bo5_3_0 / surf_bo5 * 100
            st.markdown(f"🎾 Sur {surface}, {pct:.1f}% des BO5 se sont finis en 3-0 ({surf_bo5_3_0}/{surf_bo5}).")

def show_final_analysis(df, joueur1, joueur2, cote_j1, cote_j2, set1_j1, set1_j2):
    st.markdown("---")
    st.markdown("## 🏆 Analyse Finale Pondérée")

    def analyse_combo(combinaison):
        subset = df.copy()
        for col in combinaison:
            if col == 'Cote_J1' and cote_j1 != "Tous":
                subset = subset[subset['Cote_J1'] == float(cote_j1)]
            elif col == 'Cote_J2' and cote_j2 != "Tous":
                subset = subset[subset['Cote_J2'] == float(cote_j2)]
            elif col == 'Set1_J1' and set1_j1 != "Tous":
                subset = subset[subset['Set1_J1'] == float(set1_j1)]
            elif col == 'Set1_J2' and set1_j2 != "Tous":
                subset = subset[subset['Set1_J2'] == float(set1_j2)]
            elif col in ['Type_Tournoi', 'Surface', 'Rang']:
                if col in df.columns:
                    subset = subset[subset[col] == df[col].iloc[-1]]
        return subset

    combos_j1 = [
        ['Type_Tournoi', 'Surface', 'Rang', 'Cote_J1'],
        ['Type_Tournoi', 'Surface', 'Rang', 'Cote_J1', 'Set1_J1'],
        ['Type_Tournoi', 'Cote_J1', 'Set1_J1'],
        ['Joueur 1', 'Cote_J1', 'Set1_J1']
    ]

    combos_j2 = [
        ['Type_Tournoi', 'Surface', 'Rang', 'Cote_J2'],
        ['Type_Tournoi', 'Surface', 'Rang', 'Cote_J2', 'Set1_J2'],
        ['Type_Tournoi', 'Cote_J2', 'Set1_J2'],
        ['Joueur 2', 'Cote_J2', 'Set1_J2']
    ]

    def calcul_stats(combos, label):
        score_match = 0
        score_set = 0
        for combo in combos:
            subset = analyse_combo(combo)
            n = len(subset)
            if n > 0:
                win = (subset['Gagnant'] == ('J1' if 'Joueur 1' in combo else 'J2')).sum()
                score_match += (win / n) * 25
                set_gagne = subset['Score'].str.contains("2-0|2-1|1-2|1-0|0-1").sum()
                score_set += (set_gagne / n) * 25
        st.markdown(f"### 🏆 Analyse pondérée pour {label}")
        st.markdown(f"Chance de gagner le match : {score_match:.1f}%")
        st.markdown(f"Chance de gagner au moins 1 set : {score_set:.1f}%")

    calcul_stats(combos_j1, joueur1)
    calcul_stats(combos_j2, joueur2)
