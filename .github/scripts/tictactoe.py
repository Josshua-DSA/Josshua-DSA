#!/usr/bin/env python3
"""
Tic-Tac-Toe Game Engine for GitHub Profile README
Secure, zero-dependency script designed to run in GitHub Actions.
"""

import json
import os
import re
import sys
import random

REPO_NAME = "Josshua-DSA/Josshua-DSA"
STATE_FILE = ".github/game-state.json"
README_FILE = "README.md"


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
        "turn": "X",
        "winner": null,
        "last_player": "None",
        "scores": {"visitor": 0, "bot": 0, "draws": 0}
    }


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def check_winner(board):
    # Check rows
    for r in range(3):
        if board[r][0] != " " and board[r][0] == board[r][1] == board[r][2]:
            return board[r][0]

    # Check cols
    for c in range(3):
        if board[0][c] != " " and board[0][c] == board[1][c] == board[2][c]:
            return board[0][c]

    # Check diagonals
    if board[0][0] != " " and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] != " " and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    # Check draw or ongoing
    for r in range(3):
        for c in range(3):
            if board[r][c] == " ":
                return None  # Ongoing

    return "Draw"


def get_bot_move(board):
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] == " "]
    if not empty:
        return None

    # 1. Check if Bot (O) can win in next move
    for r, c in empty:
        board[r][c] = "O"
        if check_winner(board) == "O":
            board[r][c] = " "
            return (r, c)
        board[r][c] = " "

    # 2. Block Visitor (X) from winning
    for r, c in empty:
        board[r][c] = "X"
        if check_winner(board) == "X":
            board[r][c] = " "
            return (r, c)
        board[r][c] = " "

    # 3. Take center if available
    if (1, 1) in empty:
        return (1, 1)

    # 4. Take random corner
    corners = [pos for pos in empty if pos in [(0, 0), (0, 2), (2, 0), (2, 2)]]
    if corners:
        return random.choice(corners)

    # 5. Take any remaining open square
    return random.choice(empty)


def generate_board_markdown(state):
    board = state["board"]
    winner = state["winner"]
    scores = state["scores"]
    last_player = state.get("last_player", "Visitor")

    # Status message
    if winner == "X":
        status_msg = f"<strong>// GAME OVER:</strong> @{last_player} (X) won against the Bot!"
    elif winner == "O":
        status_msg = "<strong>// GAME OVER:</strong> Bot (O) won this round!"
    elif winner == "Draw":
        status_msg = "<strong>// GAME OVER:</strong> Match ended in a draw!"
    else:
        status_msg = "<strong>// YOUR TURN (X):</strong> Click any open coordinate <code>[ · ]</code> below to place your move."

    # Build Markdown table
    def render_cell(r, c):
        val = board[r][c]
        if val == "X":
            return "` X `"
        elif val == "O":
            return "` O `"
        else:
            if winner is not None:
                return "` · `"
            issue_url = (
                f"https://github.com/{REPO_NAME}/issues/new?"
                f"title=ttt:move:{r},{c}&"
                f"body=Click+%22Submit+new+issue%22+to+place+your+move+at+row+{r}+col+{c}.+Please+do+not+modify+the+title."
            )
            return f"[` · `]({issue_url})"

    reset_url = (
        f"https://github.com/{REPO_NAME}/issues/new?"
        f"title=ttt:reset&"
        f"body=Click+%22Submit+new+issue%22+to+restart+the+Tic-Tac-Toe+game."
    )

    lines = [
        "<!-- TTT-START -->",
        "<div align=\"center\">",
        "  <h3>TIC-TAC-TOE // COMMUNITY VS BOT</h3>",
        f"  <p>{status_msg}</p>",
        "  <br/>",
        "  <table>",
        "    <thead>",
        "      <tr>",
        "        <th align=\"center\">Col 0</th>",
        "        <th align=\"center\">Col 1</th>",
        "        <th align=\"center\">Col 2</th>",
        "      </tr>",
        "    </thead>",
        "    <tbody>",
        f"      <tr><td align=\"center\">{render_cell(0,0)}</td><td align=\"center\">{render_cell(0,1)}</td><td align=\"center\">{render_cell(0,2)}</td></tr>",
        f"      <tr><td align=\"center\">{render_cell(1,0)}</td><td align=\"center\">{render_cell(1,1)}</td><td align=\"center\">{render_cell(1,2)}</td></tr>",
        f"      <tr><td align=\"center\">{render_cell(2,0)}</td><td align=\"center\">{render_cell(2,1)}</td><td align=\"center\">{render_cell(2,2)}</td></tr>",
        "    </tbody>",
        "  </table>",
        "  <br/>",
        f"  <sub>Scoreboard — <strong>Community (X):</strong> {scores['visitor']} | <strong>Bot (O):</strong> {scores['bot']} | <strong>Draws:</strong> {scores['draws']}</sub>",
        "  <br/><br/>",
        f"  <a href=\"{reset_url}\"><strong>[ ↻ RESTART NEW GAME ]</strong></a>",
        "</div>",
        "<!-- TTT-END -->"
    ]
    return "\n".join(lines)


def update_readme(board_markdown):
    if not os.path.exists(README_FILE):
        return

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"<!-- TTT-START -->.*?<!-- TTT-END -->", re.DOTALL)
    if pattern.search(content):
        new_content = pattern.sub(board_markdown, content)
    else:
        # Append before connect section or at the end
        new_content = content + "\n\n" + board_markdown

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)


def process_command(issue_title, user_login):
    title = issue_title.strip()
    state = load_state()

    # Match reset command
    if title == "ttt:reset":
        state["board"] = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        state["winner"] = None
        state["last_player"] = user_login
        save_state(state)
        update_readme(generate_board_markdown(state))
        return f"Game has been reset by @{user_login}. Have fun!"

    # Match move command: ttt:move:r,c
    move_match = re.match(r"^ttt:move:([0-2]),([0-2])$", title)
    if not move_match:
        return f"Invalid command format: `{title}`."

    r = int(move_match.group(1))
    c = int(move_match.group(2))

    # If game already ended, require reset
    if state["winner"] is not None:
        return "The game is already over. Please click `[ ↻ RESTART NEW GAME ]` to play again!"

    # Check if square is already occupied
    if state["board"][r][c] != " ":
        return f"Square ({r}, {c}) is already occupied! Please choose an open square."

    # Make visitor's move (X)
    state["board"][r][c] = "X"
    state["last_player"] = user_login

    winner = check_winner(state["board"])
    if winner:
        state["winner"] = winner
        if winner == "X":
            state["scores"]["visitor"] += 1
        elif winner == "Draw":
            state["scores"]["draws"] += 1
        save_state(state)
        update_readme(generate_board_markdown(state))
        return f"Move played at ({r}, {c}). Game finished: {winner}!"

    # Bot's Turn (O)
    bot_move = get_bot_move(state["board"])
    if bot_move:
        br, bc = bot_move
        state["board"][br][bc] = "O"
        winner = check_winner(state["board"])
        if winner:
            state["winner"] = winner
            if winner == "O":
                state["scores"]["bot"] += 1
            elif winner == "Draw":
                state["scores"]["draws"] += 1

    save_state(state)
    update_readme(generate_board_markdown(state))
    return f"Move accepted from @{user_login} at ({r}, {c}). Bot responded at ({br if bot_move else 'N/A'}, {bc if bot_move else 'N/A'})."


if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Local rendering test
        state = load_state()
        print(generate_board_markdown(state))
        sys.exit(0)

    issue_title_arg = sys.argv[1]
    user_login_arg = sys.argv[2]
    result_msg = process_command(issue_title_arg, user_login_arg)
    print(result_msg)
