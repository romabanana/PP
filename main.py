from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Footer, Header, Button, Input, Tree
from textual.screen import Screen

from pathlib import Path

import json

GIGACHAD = Path("ascii/gigachad.txt").read_text(encoding="utf-8")
COMMUNIST = Path("ascii/communist.txt").read_text(encoding="utf-8")

DESCRIPTION = """\
COUNTRY  : PEOPLE'S REPUBLIC of ARGENTINA
GOVERMENT: TOTALITARIAN DICTATORSHIP
IDEOLOGY : COMMUNISM 
PRESIDENT: JAVIER G. MILEI

    

NEXT ELECTION: 
    

"""
quotes = json.loads(Path("json/quotes.json").read_text())["quotes"]

# events = json.loads(Path("json/events.json").read_text())["events"]
# print(events[0]["effects"]["economy"])


class TopBar(Container):
    # CSS_PATH = "css/TopBar.css"

    def compose(self):
        with Container(id="top-bar"):
            yield Static(f"  {self.app.game_state.hp}", id="hp")
            yield Static(f"  {self.app.game_state.mana}", id="mana")
            yield Static("")  # filler
            yield Static("23/03/24")

    def update(self):
        self.query_one("#hp", Static).update(f"  {self.app.game_state.hp}")
        self.query_one("#mana", Static).update(f" 󱁇 {self.app.game_state.mana}")



class GameState:
    def __init__(self):
        self.turn = 1
        self.hp = 100
        self.mana = 10
        self.seats = 100
        self.depth = 0
        self.player_name = None
        self.country = "Argentina"



class MainMenu(Screen):
    # CSS_PATH = "css/MainMenu.css"
    TITLE = "Politics Game"
    def compose(self) -> ComposeResult:
        # yield Header()
        # yield Footer()

        # yield Static(TRUMP, id="background")
        yield Button("SINGLE PLAYER", id="to_game")
        yield Button("MULTIPLAYER")
        yield Button("OPTIONS", id="to_options")
        yield Button("Quit", id="quit")


        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "to_game":
            self.app.push_screen(GameScene())
        elif event.button.id == "quit":
            self.exit()
        

class CreateCharacter(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Enter your name:")
        yield Input(placeholder="Name", id="name_input")
        yield Input(placeholder="Age", id="age_input")
        yield Button("Confirm", id="confirm")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            name = self.query_one("#name_input", Input).value
            self.app.player_name = name
            age = self.query_one("#age_input", Input).value
            self.app.player_age = age
            
            
            self.app.push_screen(GameScene())

class GameScene(Screen):
    # CSS_PATH = "css/GameScene.css"

    def compose(self) -> ComposeResult:
        self.topbar = TopBar()
        yield self.topbar

        # All other items go inside the new grid container
        with Container(id="grid-container-main"):
            with Container(id="main-box"):
                yield Static(COMMUNIST, id="thumbnail")
                yield Static(quotes[0], id="footnote")
            yield Button("POLICY", classes="box", id="policy")
            yield Button("OFFICE", classes="box", id="office")
            yield Static(DESCRIPTION, id="info-box")
            yield Button("NEXT TURN", classes="box",id="next")
        
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "office":
            self.app.push_screen(OfficeScene())
        elif event.button.id == "policy":
            self.app.push_screen(PolicyScene())
        elif event.button.id == "next":
            self.app.game_state.mana += 1
            self.topbar.update()
            
        
def get_depth(node) -> int:
    depth = 0
    while node.parent is not None:
        depth += 1
        node = node.parent
    return depth

def build_tree_from_json(tree, data, parent=None):
    parent = parent or tree.root
    for key, value in data.items():
        node = parent.add(key, data=value if value else None)
        if isinstance(value, dict) and value:
            build_tree_from_json(tree, value, node)

class PolicyScene(Screen):
    # CSS_PATH = "css/PolicyScene.css"


        
    # print(events[0]["effects"]["economy"])  
    def compose(self) -> ComposeResult:
        focuses = json.loads(Path("focus/focus_data.json").read_text())["focuses"]
    
        with Container(id="top-bar"):
           yield Static(f"  {self.app.game_state.hp}", id="hp")
           yield Static(f"  {self.app.game_state.mana}", id="mana")
           yield Static("")
           yield Static("23/02/24")
        
        with Container(id="grid-container-policy"):
            data = json.loads(Path("focus/focus.json").read_text())
            tree = Tree("Focus Tree", id="focus")  # root node
            # tree.show_root = True
            
            tree.ICON_NODE = ''
            tree.ICON_NODE_EXPANDED = ''

            # tree.auto_expand = False

            tree.guide_depth = 2

            # tree.add_json(data)
            build_tree_from_json(tree, data)

            tree.root.expand()
            test = tree.root.children[0]
            test.expand()
            # test.remove()
            
            yield tree
            yield Static(focuses[self.app.game_state.depth]["desc"], id="policy-desc")
            yield Static(f"{self.app.game_state.depth}", classes="box", id="debug1")
            yield Button("COMPLETE", classes="box", id="exit")


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit":
            self.app.push_screen(GameScene())
    


    def on_tree_node_selected(self, event: Tree.NodeExpanded) -> None:
        focuses = json.loads(Path("focus/focus_data.json").read_text())["focuses"]

        node = event.node

        self.app.game_state.depth = node.id
        self.query_one("#debug1", Static).update(f"{self.app.game_state.depth}")
        self.query_one("#policy-desc", Static).update(focuses[self.app.game_state.depth]["desc"])
        if self.app.game_state.depth == 7:
            node.collapse()
        if self.app.game_state.depth == 3:
            node.collapse()

        # parent_data = node.parent
        # if self.app.game_state.depth % 2 == 0:
        #     if self.app.game_state.mana <= parent_data.get("cost"):
        #         node.collapse()
                
        # else:
          
            

class OfficeScene(Screen):
    def compose(self) -> ComposeResult:
        yield Static("OFFICE")
        yield Button("BACK", id="exit")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit":
            self.app.push_screen(GameScene())

        

            
           
class PoliticsGame(App):
    CSS_PATH = "css/app.css"

    def on_mount(self) -> None:

        self.game_state = GameState()
        self.push_screen(MainMenu())

if __name__ == "__main__":
    app = PoliticsGame()
    app.run()
