import streamlit as st
from analyzer import ChessAnalyzer
from PIL import Image
import io
import pandas as pd
from utils import get_eval_bar_image  # NEW import

st.set_page_config(layout="wide")
st.title("♟️ Chess Game Analyzer")

uploaded_file = st.file_uploader("Upload a PGN file", type=["pgn"])

if uploaded_file:
    analyzer = ChessAnalyzer(uploaded_file)
    analyzer.analyze_game()

    scorecards = analyzer.get_scorecards()
    moves = analyzer.moves_info
    opening = analyzer.opening_name

    st.subheader(f"📖 Opening: {opening}")
    col1, col2 = st.columns(2)
    col1.metric(f"{scorecards['White']['name']} (White)", f"{scorecards['White']['accuracy']}% Accuracy")
    col2.metric(f"{scorecards['Black']['name']} (Black)", f"{scorecards['Black']['accuracy']}% Accuracy")

    st.markdown("---")
    st.subheader("🧠 Move-by-Move Analysis")

    selected_index = st.slider("Select Move Number", 1, len(moves), 1)
    selected_move = moves[selected_index - 1]

    # Evaluation bar and board side-by-side
    from PIL import Image as PILImage

    img_col, bar_col = st.columns([5, 1], gap="small")

    with img_col:
        st.image(
            PILImage.open(io.BytesIO(selected_move["image"])),
            caption=f"{selected_move['color']} plays {selected_move['move']}"
        )

    with bar_col:
        bar_image = get_eval_bar_image(selected_move["eval_before"])
        st.image(
            bar_image,
            use_container_width=False,
            width=40
        )



    st.write(f"**Move Type:** `{selected_move['type']}`")
    st.write(f"**Centipawn Loss:** `{int(selected_move['cp_loss'])}`")
    st.write(f"**Evaluation Before:** `{selected_move['eval_before']}`")
    st.write(f"**Evaluation After:** `{selected_move['eval_after']}`")

    st.markdown("---")
    st.subheader("📋 All Moves Table")

    table_data = [
        {
            "Move #": move["move_number"],
            "Color": move["color"],
            "Move": move["move"],
            "Type": move["type"],
            "CP Loss": int(move["cp_loss"])
        }
        for move in moves
    ]
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
