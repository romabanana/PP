from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Footer, Header, Button, Input, Tree
from textual.screen import Screen

from pathlib import Path

import json

from rich_pixels import Pixels

from PIL import Image

import pygame

GIGACHAD = Path("ascii/arg.txt").read_text(encoding="utf-8")
COMMUNIST = Path("ascii/tank.txt").read_text(encoding="utf-8")
DESCRIPTION = """\
COUNTRY  : PEOPLE'S REPUBLIC of ARGENTINA
GOVERMENT: TOTALITARIAN DICTATORSHIP
IDEOLOGY : COMMUNISM 
PRESIDENT: JAVIER G. MILEI

    

NEXT ELECTION: 
    

"""
quotes = json.loads(Path("json/quotes.json").read_text())["quotes"]
k = 0.05
w = int(90)
h = int(70)
pixels = Pixels.from_image_path("img/commie.webp", [w, h])

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
        self.depth = 0
        self.player_name = None
        self.focus = None
        self.country = "Argentina"
        self.focus_array = [0]*100
        self.focus_cost_array = []



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
                yield Static(pixels, id="thumbnail")
                # yield ImageView("img/031")
                yield Static(quotes[0], id="footnote")
            yield Button("POLICY", classes="box", id="policy")
            yield Button("OFFICE", classes="box", id="office")
            yield Static("t", classes="box")
            yield Static("t", classes="box")
           
            yield Static(DESCRIPTION, id="info-box")
            yield Button("NEXT TURN", classes="box",id="next")
        
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "office":
            self.app.push_screen(OfficeScene())
            self.app.click_sound.play()  # Just play sound, no modifications to UI
           
        elif event.button.id == "policy":
            self.app.push_screen(PolicyScene())
            self.app.click_sound.play()  # Just play sound, no modifications to UI
           
        elif event.button.id == "next":
            self.app.game_state.mana += 1
            self.app.click_sound.play()  # Just play sound, no modifications to UI
            self.topbar.update()
            
        
def get_depth(node) -> int:
    depth = 0
    while node.parent is not None:
        depth += 1
        node = node.parent
    return depth

def build_tree_from_json(self, tree, data,parent=None):
    parent = parent or tree.root
    
    for key, value in data.items():
        node = parent.add(key, data=value if value else None)
        id = node.id
        # self.log(count)
        if self.app.game_state.focus_array[id] == 1:
            node.set_label(f"[green]{key}[/green]")
            node.expand()
        elif self.app.game_state.focus_array[id] == 2:
            node.set_label(f"[red]{key} (locked)[/red]")


        if isinstance(value, dict) and value:
            build_tree_from_json(self, tree, value, node)


class PolicyScene(Screen):
    def compose(self) -> ComposeResult:
        focuses = json.loads(Path("focus/focus_data.json").read_text())["focuses"]
        
        self.topbar = TopBar()
        yield self.topbar

        with Container(id="grid-container-policy"):
            data = json.loads(Path("focus/focus.json").read_text())
            tree = Tree("Focus Tree", id="focus")  # root node
            tree.show_root = False
            
            tree.ICON_NODE = ''
            tree.ICON_NODE_EXPANDED = ''

            # tree.auto_expand = False

            tree.guide_depth = 2
            self.app.game_state.focus_array[0] = 1
            self.app.game_state.focus = tree.root
            # tree.add_json(data)
            build_tree_from_json(self, tree, data)
            self.log(self.app.game_state.focus_array)
            # tree_set_state(self, tree, data)
            
            tree.root.expand()
            test = tree.root.children[0]
            test.expand()
            # test.remove()
            
            yield tree
            
            yield Static(focuses[self.app.game_state.focus.id]["desc"], id="policy-desc")
            yield Static(str(focuses[self.app.game_state.focus.id]["cost"]), classes="box", id="focus-cost")
            yield Static(f"{self.app.game_state.depth}", classes="box", id="debug1")
            
            yield Button("TAKE", classes="box", id="focus-button")
            yield Button("COMPLETE", classes="box", id="exit")


    def on_button_pressed(self, event: Button.Pressed) -> None:
        focuses = json.loads(Path("focus/focus_data.json").read_text())["focuses"]
    
        if event.button.id == "exit":
            self.log(self.app.game_state.depth)
            self.log(self.app.game_state.focus_array)
            self.app.push_screen(GameScene())
            self.app.click_sound.play()  # Just play sound, no modifications to UI
           
        elif event.button.id == "focus-button": 
            if self.app.game_state.focus_array[self.app.game_state.focus.id] == 0:
                if self.app.game_state.mana >= focuses[self.app.game_state.focus.id]["cost"]: 
                    self.app.game_state.focus_array[self.app.game_state.focus.id] = 1
                    self.app.game_state.focus.expand()
                    self.app.game_state.mana -= focuses[self.app.game_state.focus.id]["cost"]
                    self.app.game_state.focus.set_label(f"[green]{self.app.game_state.focus.label}[/green]")
                    for id in focuses[self.app.game_state.focus.id]["excludes"]:
                        for sib in self.app.game_state.focus.siblings:
                            if sib.id == id:
                                sib.set_label(f"[red]{sib.label}[/red]")
                                self.app.game_state.focus_array[sib.id] = 2
                    self.topbar.update()
                    self.app.click_sound.play()  # Just play sound, no modifications to UI
           

    def update_focus_tree(self) -> None:
        focuses = json.loads(Path("focus/focus_data.json").read_text())["focuses"]
        self.app.game_state.depth = self.app.game_state.focus.id
        self.query_one("#debug1", Static).update(f"{self.app.game_state.depth}")
        self.query_one("#policy-desc", Static).update(focuses[self.app.game_state.focus.id]["desc"])
        self.query_one("#focus-cost", Static).update(str(focuses[self.app.game_state.focus.id]["cost"]))

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        self.app.game_state.focus = event.node
        self.update_focus_tree()
       

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        self.app.game_state.focus = event.node
        self.update_focus_tree()
        self.app.click_sound.play()  # Just play sound, no modifications to UI
           
       

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        if self.app.game_state.focus_array[self.app.game_state.focus.id] == 1:
            event.node.expand()
       

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        self.app.game_state.focus = event.node
        id = self.app.game_state.focus.id
        self.update_focus_tree()
       
        if self.app.game_state.focus_array[id] == 0:
            event.node.collapse()
        
        
          
            

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

        pygame.mixer.init()
        self.click_sound = pygame.mixer.Sound("click.mp3")
        # music = pygame.mixer.Sound("background.mp3")
        # music.set_volume(0.1)  # 20% volume
        # music.play(loops=-1)   # loop forever
        self.game_state = GameState()
        self.push_screen(MainMenu())

if __name__ == "__main__":
    app = PoliticsGame()
    app.run()
