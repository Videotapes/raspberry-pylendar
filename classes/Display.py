from PIL import Image, ImageDraw, ImageFont
from unicornhatmini import UnicornHATMini


class Display(UnicornHATMini):
    """A Display object instance; extends UnicornHATMini
    
    Attributes
    ----------
    display_text : str
        Text to be displayed on the hat
    display_font: str
        Location of font to be used for display
    """

    def __init__(self, display_text="default", display_font=None, time_to_live=20):
        """Initializes the Display object instance.
        
        Parameters
        ----------
        display_text : str, optional
            Text to be displayed on the hat.
        display_font: str
            Location of font to be used for display.
        """ 

        self.display_text = display_text
        self.display_font = display_font
        super().__init__()

    def set_column(self, column, r, g, b):
        for i in range(self.get_shape()[0]):
            self.set_pixel(i, column, r, g, b)

    def set_row(self, row, r, g, b):
        for i in range(self.get_shape()[1]):
            self.set_pixel(row, i, r, g, b)
    
    def display_text(self, display_method="static"):
        """Displays text on the hat.

        Parameters
        ----------
        display_method: str, optional
            Determines the manner in which to display the text; defaults to static.
            Options: static, scroll, flash
        """
        if display_method == "scroll":
            pass
        elif display_method == "flash":
            pass
        else:
            pass