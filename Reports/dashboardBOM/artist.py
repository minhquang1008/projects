import pandas as pd

from typing import Tuple, Literal
from PIL import Image, ImageDraw, ImageFont

from color import Color
from chart import _Chart


class Artist:

    def __init__(self, domain: Literal['CoSo', 'PhaiSinh']) -> None:

        if domain == 'CoSo':
            self.bgColor = Color.DARKBLUE
            self.productSize = (8400, 11800)
        else:
            self.bgColor = Color.DARKGREEN
            self.productSize = (6200, 8800)  # final

        self.backgroundImage = Image.new(
            mode='RGB',
            size=self.productSize,
            color=self.bgColor
        )
        self.__product = self.backgroundImage

    def draw(
            self,
            table: pd.DataFrame,
            chart: _Chart,
            topLeft: Tuple[int, int]
    ):
        chart.data = table
        chartImage = chart.produce()
        self.__product.paste(chartImage, topLeft)

    def write(
            self,
            text: str,
            size: int,
            color: str,
            topLeft: Tuple[int, int],
            align: str = 'center',
            anchor=None,
            spaceBetweenLines: int = 50,
    ):
        writer = ImageDraw.Draw(self.__product)
        writer.text(
            xy=topLeft,
            text=text,
            fill=color,
            font=ImageFont.truetype(font="arialbd.ttf", size=size),
            align=align,
            anchor=anchor,
            spacing=spaceBetweenLines,
        )

    @property
    def product(self):
        return self.__product