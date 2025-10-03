import warnings

import geopandas as gpd  # type: ignore
import matplotlib.pyplot as plt
from PIL import Image
from rich_pixels import Pixels
from textual.app import App, ComposeResult
from textual.widgets import Static

MAP_FILENAME = "world_population.png"

# Ignore that the geopandas.dataset module is deprecated!
warnings.filterwarnings("ignore", category=FutureWarning)


def generate_map_image() -> None:
    world = gpd.read_file(
        gpd.datasets.get_path("naturalearth"),  # type: ignore
    )
    # Remove Antarctica
    world = world[world["continent"] != "Antarctica"]
    # Remove axis labels
    ax = world.plot(column="pop_est")
    ax.set_axis_off()
    # Save as image
    plt.savefig(MAP_FILENAME, bbox_inches="tight", transparent="True")


class WorldPopulationApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        with Image.open(MAP_FILENAME) as image:
            size_ratio = image.width / self.size.width
            new_width = int(image.width / size_ratio)
            new_height = int(image.height / size_ratio)
            resized_image = image.resize(
                (new_width, new_height),
                Image.Resampling.NEAREST,
            )
            pixels = Pixels.from_image(resized_image)
        yield Static(pixels)


if __name__ == "__main__":
    generate_map_image()
    app = WorldPopulationApp()
    app.run()