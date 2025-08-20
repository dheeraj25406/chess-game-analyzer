import io
import matplotlib.pyplot as plt
import chess.svg
import cairosvg
import pandas as pd
from PIL import Image, ImageDraw

def get_opening_name(game):
    try:
        df = pd.read_csv("eco.csv")
        df.dropna(subset=["moves", "name"], inplace=True)
        df["moves"] = df["moves"].str.strip()
        df["name"] = df["name"].str.strip()
        df["eco"] = df["eco"].str.strip()

        board = game.board()
        moves = []
        for move in game.mainline_moves():
            moves.append(board.san(move))
            board.push(move)

        # Reconstruct PGN-style numbered move string (e.g., 1.e4 e5 2.Nf3 Nc6 ...)
        move_str = ""
        for i in range(len(moves)):
            if i % 2 == 0:
                move_str += f"{(i // 2) + 1}.{moves[i]} "
            else:
                move_str += f"{moves[i]} "
        move_str = move_str.strip()

        best_match = "Unknown Opening"
        best_length = 0

        for _, row in df.iterrows():
            opening_moves = row["moves"]
            if move_str.startswith(opening_moves) and len(opening_moves) > best_length:
                best_match = f"{row['eco']} - {row['name']}"
                best_length = len(opening_moves)

        return best_match
    except Exception as e:
        return f"Error: {e}"

def evaluate_position(stockfish):
    eval_info = stockfish.get_evaluation()
    if eval_info["type"] == "cp":
        return eval_info["value"]
    elif eval_info["type"] == "mate":
        return 10000 if eval_info["value"] > 0 else -10000
    return 0

def classify_move(cp_loss):
    if cp_loss < 15:
        return "Best"
    elif cp_loss < 50:
        return "Excellent"
    elif cp_loss < 100:
        return "Good"
    elif cp_loss < 200:
        return "Inaccuracy"
    elif cp_loss < 500:
        return "Mistake"
    else:
        return "Blunder"

def get_board_image(board):
    svg = chess.svg.board(board, size=350)
    png_data = cairosvg.svg2png(bytestring=svg)
    return png_data

def calculate_accuracy(cp_losses):
    if not cp_losses:
        return 100.0
    avg_loss = sum(cp_losses) / len(cp_losses)
    acc = max(0, 100 - avg_loss / 10)
    return round(acc, 2)

def get_eval_bar_image(cp_score):
    height = 350
    img = Image.new("RGB", (40, height), "gray")
    draw = ImageDraw.Draw(img)

    cp_score = max(min(cp_score, 1000), -1000)
    norm = cp_score / 2000 + 0.5
    white_height = int(norm * height)

    draw.rectangle([0, 0, 40, height - white_height], fill="black")
    draw.rectangle([0, height - white_height, 40, height], fill="white")

    return img

