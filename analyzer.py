import io
import os
import platform
import urllib.request
import zipfile
import chess
import chess.pgn
from stockfish import Stockfish
from utils import (
    get_opening_name,
    evaluate_position,
    classify_move,
    get_board_image,
    calculate_accuracy,
)

class ChessAnalyzer:
    def __init__(self, uploaded_file, stockfish_path=None):
        pgn_text = uploaded_file.read().decode("utf-8")
        self.pgn_io = io.StringIO(pgn_text)

        if platform.system() == "Windows":
            # Use local Windows path (works locally)
            stockfish_path = r"stockfish/stockfish.exe"
        else:
            # Hugging Face/Linux
            if not os.path.exists("stockfish"):
                print("Downloading Stockfish for Linux...")
                url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_15/stockfish-ubuntu-x86-64.zip"
                urllib.request.urlretrieve(url, "stockfish.zip")
                with zipfile.ZipFile("stockfish.zip", "r") as zip_ref:
                    zip_ref.extractall("stockfish_folder")
                # Locate the binary and make it executable
                for root, dirs, files in os.walk("stockfish_folder"):
                    for file in files:
                        if "stockfish" in file.lower():
                            stockfish_path = os.path.join(root, file)
                            os.system(f"chmod +x {stockfish_path}")

        self.stockfish = Stockfish(path=stockfish_path)
        self.game = chess.pgn.read_game(self.pgn_io)
        self.board = self.game.board()
        self.moves_info = []
        self.white_scores = []
        self.black_scores = []
        self.player_names = {
            "White": self.game.headers.get("White", "White"),
            "Black": self.game.headers.get("Black", "Black"),
        }
        self.opening_name = get_opening_name(self.game)

    def analyze_game(self):
        node = self.game
        move_number = 1

        while node.variations:
            next_node = node.variation(0)
            move = next_node.move
            san = self.board.san(move)

            self.stockfish.set_fen_position(self.board.fen())
            eval_before = evaluate_position(self.stockfish)

            self.board.push(move)

            self.stockfish.set_fen_position(self.board.fen())
            eval_after = evaluate_position(self.stockfish)

            move_color = "White" if self.board.turn == chess.BLACK else "Black"
            cp_loss = abs(eval_before - eval_after)

            move_type = classify_move(cp_loss)
            board_img = get_board_image(self.board)

            self.moves_info.append({
                "move_number": move_number,
                "move": san,
                "color": move_color,
                "eval_before": eval_before,
                "eval_after": eval_after,
                "cp_loss": cp_loss,
                "type": move_type,
                "image": board_img,
            })

            if move_color == "White":
                self.white_scores.append(cp_loss)
            else:
                self.black_scores.append(cp_loss)

            move_number += 1
            node = next_node

    def get_scorecards(self):
        white_acc = calculate_accuracy(self.white_scores)
        black_acc = calculate_accuracy(self.black_scores)
        return {
            "White": {
                "name": self.player_names["White"],
                "accuracy": white_acc,
            },
            "Black": {
                "name": self.player_names["Black"],
                "accuracy": black_acc,
            }
        }
