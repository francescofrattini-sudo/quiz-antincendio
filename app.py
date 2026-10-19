import os
import random
import pandas as pd
import streamlit as st

# --- CONFIGURAZIONE PATH E FILE ---
EXCEL_PATH = "Quiz.xlsx"

st.set_page_config(
    page_title="Quiz Addetto Antincendio",
    page_icon="🔥",
    layout="centered"
)

# --- FUNZIONE PER CARICARE E MESCOLARE IL QUIZ ---
@st.cache_data
def load_and_shuffle_quiz(excel_path):
    if not os.path.exists(excel_path):
        st.error(f"File non trovato nel percorso specificato: {excel_path}")
        return None
    
    df = pd.read_excel(excel_path)
    quiz_list = []
    
    for _, row in df.iterrows():
        orig_answers = {
            'A': str(row['rispostaA']),
            'B': str(row['rispostaB']),
            'C': str(row['rispostaC'])
        }
        ok_letter = str(row['risposta_OK']).strip().upper()
        
        options = [
            {'label': orig_answers['A'], 'is_correct': (ok_letter == 'A')},
            {'label': orig_answers['B'], 'is_correct': (ok_letter == 'B')},
            {'label': orig_answers['C'], 'is_correct': (ok_letter == 'C')}
        ]
        
        # Mescolamento opzioni di risposta
        random.shuffle(options)
        
        quiz_list.append({
            'nr_domanda': row['nr_domanda'],
            'descr_domanda': row['descr_domanda'],
            'options': options
        })
    
    # Mescolamento domande
    random.shuffle(quiz_list)
    return quiz_list

# --- INIZIALIZZAZIONE STATO DELL'APP ---
if "quiz_data" not in st.session_state:
    data = load_and_shuffle_quiz(EXCEL_PATH)
    st.session_state.quiz_data = data
    st.session_state.user_answers = {}

quiz_data = st.session_state.quiz_data

# --- CALCOLO STATISTICHE IN TEMPO REALE ---
total_questions = len(quiz_data) if quiz_data else 0
correct_count = 0
wrong_count = 0

for q_id, chosen_text in st.session_state.user_answers.items():
    # Estraiamo l'indice della domanda dal q_id (es. "q_0" -> 0)
    idx = int(q_id.split("_")[1])
    q = quiz_data[idx]
    for opt in q['options']:
        if opt['label'] == chosen_text:
            if opt['is_correct']:
                correct_count += 1
            else:
                wrong_count += 1

answered_total = correct_count + wrong_count
success_rate = (correct_count / answered_total * 100) if answered_total > 0 else 0.0

# --- SPECCHIETTO RIEPILOGATIVO FISSO IN ALTO A DESTRA ---
st.markdown(f"""
    <style>
        .fixed-summary {{
            position: fixed;
            top: 70px;
            right: 30px;
            width: 240px;
            background-color: #ffffff;
            border: 2px solid #366092;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
            z-index: 999999;
            font-family: sans-serif;
        }}
        .fixed-summary h4 {{
            margin: 0 0 10px 0;
            color: #366092;
            font-size: 15px;
            text-align: center;
        }}
        .summary-item {{
            font-size: 13px;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
        }}
    </style>
    <div class="fixed-summary">
        <h4>📊 Riepilogo Quiz</h4>
        <div class="summary-item"><span>Totale Domande:</span> <b>{total_questions}</b></div>
        <div class="summary-item" style="color: #006100;"><span>✅ Corrette:</span> <b>{correct_count}</b></div>
        <div class="summary-item" style="color: #9C0006;"><span>❌ Sbagliate:</span> <b>{wrong_count}</b></div>
        <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ccc;">
        <div class="summary-item"><span>Risposte date:</span> <b>{answered_total} / {total_questions}</b></div>
        <div class="summary-item"><span>% Successo:</span> <b>{success_rate:.1f}%</b></div>
    </div>
""", unsafe_allow_html=True)

# --- INTERFACCIA UTENTE (STREAMLIT) ---
st.title("🔥 Simulatore Quiz - Addetto Antincendio di Livello 3")
st.markdown("Rispondi alle domande sottostanti. Le domande e le opzioni di risposta sono state mescolate casualmente.")
st.markdown("---")

if quiz_data:
    for idx, q in enumerate(quiz_data):
        q_id = f"q_{idx}"
        st.subheader(f"Domanda {idx + 1} (Orig. {q['nr_domanda']})")
        st.write(f"**{q['descr_domanda']}**")
        
        option_labels = [opt['label'] for opt in q['options']]
        
        selected_option = st.radio(
            label=f"Seleziona la risposta per la domanda {idx + 1}",
            options=option_labels,
            key=q_id,
            index=None if q_id not in st.session_state.user_answers else option_labels.index(st.session_state.user_answers[q_id])
        )
        
        if selected_option:
            # Se la risposta cambia, aggiorniamo lo stato e facciamo il rerun per aggiornare subito lo specchietto
            if st.session_state.user_answers.get(q_id) != selected_option:
                st.session_state.user_answers[q_id] = selected_option
                st.rerun()
        
        # Feedback visivo immediato
        if q_id in st.session_state.user_answers:
            chosen_text = st.session_state.user_answers[q_id]
            
            for opt in q['options']:
                if opt['label'] == chosen_text:
                    if opt['is_correct']:
                        st.markdown(
                            f"<div style='background-color: #C6EFCE; color: #006100; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>"
                            f"<b>Risposta Corretta!</b> {opt['label']}</div>", 
                            unsafe_allow_html=True
                        )
                    else:
                        correct_opt_text = next(o['label'] for o in q['options'] if o['is_correct'])
                        st.markdown(
                            f"<div style='background-color: #FFC7CE; color: #9C0006; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>"
                            f"<b>Risposta Errata.</b> Hai selezionato: {chosen_text}</div>", 
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<div style='background-color: #C6EFCE; color: #006100; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>"
                            f"<b>La risposta corretta era:</b> {correct_opt_text}</div>", 
                            unsafe_allow_html=True
                        )
        
        st.markdown("---")

    # Pulsante per ricaricare / rimescolare il quiz
    if st.button("🔄 Rimescola Domande e Risposte"):
        st.session_state.quiz_data = load_and_shuffle_quiz(EXCEL_PATH)
        st.session_state.user_answers = {}
        st.rerun()
