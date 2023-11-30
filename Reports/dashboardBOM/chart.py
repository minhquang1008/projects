import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
import matplotlib.image as image
import mplcyberpunk
import warnings

from abc import ABC, abstractmethod
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from color import Color

plt.ioff()
warnings.filterwarnings('ignore')


class _Chart(ABC):

    def __init__(self, bgColor: str) -> None:
        self.__data = None
        self.__height = None
        self.__width = None
        self.__title = None
        self.bgColor = bgColor

        # Branch name:
        self.mapBranch = {
            '0101': 'DISTRICT 03',
            '0102': 'PHU MY HUNG',
            '0104': 'DISTRICT 07',
            '0105': 'TAN BINH',
            '0117': 'DISTRICT 01',
            '0120': 'AMD-05',
            '0201': 'HA NOI',
            '0202': 'THANH XUAN',
            '0301': 'HAI PHONG',
            '0116': 'AMD-01',
        }

    @property
    def data(self) -> pd.DataFrame:
        return self.__data

    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        self.__data = data

    @property
    def height(self) -> int:
        """
        Height in pixel
        """
        return self.__height

    @height.setter
    def height(self, value: int) -> None:
        self.__height = value

    @property
    def width(self) -> int:
        """
        Width in pixel
        """
        return self.__width

    @width.setter
    def width(self, value: int) -> None:
        self.__width = value

    @property
    def title(self) -> str:
        """
        Title of the chart
        """
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        self.__title = value

    @abstractmethod
    def produce(self) -> Image:
        """
        Draw chart to PIL.Image object
        """
        pass


class CompletionRings(_Chart):

    def produce(self) -> Image:

        # Default setting
        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE,
        })

        # Tạo figure & axes
        fig = plt.figure(
            figsize=(6.5, 6.5),
            facecolor=self.bgColor
        )
        ax = fig.add_subplot()
        ax.set_frame_on(False)

        # Measures (vẽ từ ngoài vào trong)
        measures = ['MarketShare', 'FeeIncome', 'InterestIncome', 'NewAccounts']
        displayNames = {
            'MarketShare': 'Market share',
            'FeeIncome': 'Trading fee',
            'InterestIncome': 'Margin income',
            'NewAccounts': 'New account',
        }
        # Radius
        maxRadius = 1.5
        minRadius = 0.4
        # Ring width
        ringWidth = (maxRadius - minRadius) / len(measures)
        # Data
        columns = [col for col in self.data.columns if col in measures]
        data = self.data[columns].squeeze().map(lambda x: min(x, 1))
        for i, measure in enumerate(columns):
            completionRatio = data[measure]
            if completionRatio <= 0.2:
                ringColor = Color.RED
            elif completionRatio <= 0.5:
                ringColor = Color.ORANGE
            elif completionRatio <= 0.8:
                ringColor = Color.BLUE
            elif completionRatio < 1:
                ringColor = Color.MEDIUMGREEN
            else:
                ringColor = Color.SEANCE

            ringRadius = maxRadius - i * ringWidth

            ax.pie(
                x=[completionRatio, 1 - completionRatio],
                radius=ringRadius,
                startangle=90,
                counterclock=False,
                colors=[ringColor, self.bgColor],
                wedgeprops={'width': ringWidth, 'edgecolor': self.bgColor, 'linewidth': 8},
                textprops={'color': Color.WHITE, 'weight': 'bold', 'fontsize': 22, 'ha': 'center', 'va': 'center'},
                labels=[f"{round(self.data[measure].iloc[0] * 100)}%", ''],
                labeldistance=1 - ringWidth / 2 / ringRadius
            )
            ax.text(
                x=0,
                y=ringRadius - ringWidth / 2,
                s=displayNames.get(measure),
                ha='right',
                va='center',
                fontsize=20,
                weight='bold',
                color=Color.WHITE
            )

        # Convert to Image
        plt.tight_layout()
        while True:
            try:
                plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=self.bgColor, bbox_inches='tight')
                break
            except (OSError,):
                pass
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')


class TrailingBars(_Chart):

    def produce(self) -> Image:

        # Default setting
        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE,
        })

        # Tạo figure & axes
        fig = plt.figure(
            figsize=(9, 6),
            facecolor=self.bgColor
        )
        ax = fig.add_subplot()
        ax.set_facecolor(self.bgColor)

        # 4 spines of chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(Color.WHITE)

        # Legend
        legendHandles = [
            patches.Rectangle(xy=(0, 0), width=1, height=1, color=Color.MEDIUMGREEN),
            patches.Rectangle(xy=(0, 0), width=1, height=1, color=Color.BLUE),
            patches.Rectangle(xy=(0, 0), width=1, height=1, color=Color.WHITE),
        ]
        legendLabels = [r'Đạt chỉ tiêu', r'Không đạt chỉ tiêu', r'Chỉ tiêu']
        plt.legend(
            handles=legendHandles,
            labels=legendLabels,
            frameon=False,
            ncol=3,
            loc='upper center',
            bbox_to_anchor=(0.5, -0.05),
            fontsize=13
        )

        # Horizontal ticks & tick labels
        plt.tick_params(
            axis='both', left=False, top=False, right=False, bottom=False,
            labelleft=True, labeltop=False, labelright=False, labelbottom=True
        )
        ax.tick_params(axis='x', colors=Color.WHITE)
        xLoc = np.arange(self.data.shape[0])

        if self.data.shape[0] == 12:  # MTD
            plt.xticks(xLoc, self.data['Date'].dt.strftime("T%m'%y"), fontsize=13)
        else:  # YTD
            plt.xticks(xLoc, self.data['Date'].dt.strftime("%Y"), fontsize=13)

        # Inner bars
        innerBars = plt.bar(
            x=np.arange(self.data.shape[0]),
            height=self.data['Actual'],
            width=0.6,
            align='center',
            color=[
                Color.BLUE
                if self.data.loc[index, ['Actual']].squeeze() < self.data.loc[index, ['Target']].squeeze()
                else Color.MEDIUMGREEN for index in self.data.index
            ],
        )

        # Vertical ticks & tick labels
        ax.tick_params(axis='y', colors=Color.WHITE)
        verticalValues = ax.get_yticks()
        if max(verticalValues) > 1e9:
            verticalLabels = ['{:,.1f}B'.format(y / 1e9) for y in verticalValues]
        elif max(verticalValues) > 1e5:
            verticalLabels = ['{:,.1f}M'.format(y / 1e6) for y in verticalValues]
        elif 0 < max(verticalValues) < 1:
            verticalLabels = ['{:.3f}%'.format(y * 100) for y in verticalValues]
        else:
            verticalLabels = ['{:,.3f}'.format(y) for y in verticalValues]
        plt.yticks(verticalValues, verticalLabels, fontsize=13)

        # Horizontal gridlines
        ax.grid(visible=False)
        ax.grid(which='major', axis='y', alpha=0.04, color=Color.WHITE)

        # Benchmark lines
        x_start = np.array([plt.getp(bar, 'x') for bar in innerBars])
        x_end = x_start + [plt.getp(bar, 'width') for bar in innerBars]
        plt.hlines(
            self.data['Target'],
            x_start,
            x_end,
            colors=Color.WHITE,
            linewidth=3
        )
        # Value in bars
        # minTarget = self.data['Target'].min()
        # minActual = self.data['Actual'].min()
        maxTarget = self.data['Target'].max()
        maxActual = self.data['Actual'].max()
        actualData = self.data['Actual'].reset_index(drop=True)

        if self.data['Target'].max() > 1e9:
            stringFormat = '{:,.1f}B'
            dividor = 1e9
        elif self.data['Target'].max() > 1e5:
            stringFormat = '{:,.1f}M'
            dividor = 1e6
        elif self.data['Target'].max() < 1:
            stringFormat = '{:.3f}%'
            dividor = 1 / 100
        else:
            stringFormat = '{:,.0f}'
            dividor = 1

        for index in xLoc:
            actual = actualData.loc[index]
            plt.text(
                x=index,
                y=max(maxTarget, maxActual) / 10,
                s=stringFormat.format(actual / dividor),
                ha='center',
                rotation=90,
                fontsize=14
            )

        # Convert to Image
        plt.tight_layout()
        while True:
            try:
                plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=self.bgColor, bbox_inches='tight')
                break
            except (OSError,):
                pass
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')


class FluctuationLine(_Chart):

    def produce(self) -> Image:

        # Default setting
        plt.style.use("cyberpunk")
        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE,
        })

        # Tạo figure & axes
        fig = plt.figure(
            figsize=(7.3, 5.7),
            facecolor=self.bgColor
        )
        ax = fig.add_subplot()
        ax.set_facecolor(self.bgColor)

        # y label
        plt.ylabel("VND million", fontsize=16)

        # 4 spines of chart
        plt.xticks(rotation=45)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['bottom'].set_color(Color.WHITE)
        ax.tick_params(axis='x', colors=Color.WHITE, labelsize=15)
        ax.tick_params(axis='y', colors=Color.WHITE, labelsize=15)

        # Reformat date axis
        reformat = mdates.DateFormatter('%b-%y')
        ax.xaxis.set_major_formatter(reformat)

        # Line chart
        plt.plot(
            self.data['Date'],
            self.data['Value'] / 1e6,
            color=Color.GREEN
        )

        # Grid lines
        plt.grid(visible=False)  # xóa toàn bộ grid line sẵn có
        plt.grid(which='major', axis='y', color=Color.WHITE, alpha=0.3)

        # Reformat value axis
        verticalValues = ax.get_yticks()
        verticalLabels = ['{:,.0f}'.format(y) for y in verticalValues]
        plt.yticks(verticalValues, verticalLabels, fontsize=15)

        # Tắt hết các ticks & tick labels
        plt.tick_params(
            axis='both',
            left=False, top=False, right=False, bottom=False,
            labelleft=True, labeltop=False, labelright=False, labelbottom=True,
        )

        # Add glow effect to line chart
        mplcyberpunk.make_lines_glow()
        mplcyberpunk.add_underglow()

        # Convert to Image
        plt.tight_layout()
        while True:
            try:
                plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=self.bgColor, bbox_inches='tight')
                break
            except (OSError,):
                pass
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')


class InfoTag(_Chart):

    def produce(self) -> Image:

        # Default setting
        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE,
        })
        # Tạo figure & axes
        if self.bgColor == Color.DARKGREEN:  # PhaiSinh
            faceColor = Color.MEDIUMGREEN
        else:  # CoSo
            faceColor = Color.MEDIUMBLUE
        fig = plt.figure(
            figsize=(5.5, 14.5 / 4),
            facecolor=faceColor
        )
        ax = fig.add_subplot()
        ax.set_facecolor(faceColor)
        ax.set_frame_on(False)
        ax.axes.set_xticks([])
        ax.axes.set_yticks([])
        ax.set_xlim(left=0, right=1)

        # Data
        if self.data.empty:
            raise ValueError("Invalid Branch")
        data = self.data.squeeze()
        if 'MarketShare' in data.index:
            tagTitle = 'Market Share'
            absoluteValueString = r'{:,.3f}%'.format(data['MarketShare'] * 100)
            absoluteChangeString = r'{:+,.3f}%'.format(data['AbsoluteChange'] * 100)
            relativeChangeString = r'{:+,.3f}%'.format(data['RelativeChange'] * 100)
        elif 'FeeIncome' in data.index:
            tagTitle = 'Trading Fee'
            absoluteValueString = r'{:,.1f} M'.format(data['FeeIncome'] / 1e6)
            absoluteChangeString = r'{:+,.1f} M'.format(data['AbsoluteChange'] / 1e6)
            relativeChangeString = r'{:+,.3f}%'.format(data['RelativeChange'] * 100)
        elif 'InterestIncome' in data.index:
            tagTitle = 'Margin Income'
            absoluteValueString = r'{:,.1f} M'.format(data['InterestIncome'] / 1e6)
            absoluteChangeString = r'{:+,.1f} M'.format(data['AbsoluteChange'] / 1e6)
            relativeChangeString = r'{:+,.3f}%'.format(data['RelativeChange'] * 100)
        elif 'NewAccounts' in data.index:
            tagTitle = 'New accounts'
            absoluteValueString = r'{:,.0f}'.format(data['NewAccounts'])
            absoluteChangeString = r'{:+,.0f}'.format(data['AbsoluteChange'])
            relativeChangeString = r'{:+,.3f}%'.format(data['RelativeChange'] * 100)
        else:
            raise ValueError("Invalid Measure")

        # Icon: Change
        absoluteChange = data['AbsoluteChange']
        if absoluteChange >= 0:
            trianglePath = r"img\green_triangle.png"
        else:
            trianglePath = r"img\red_triangle.png"

        # Title
        plt.text(
            x=0.3,
            y=0.8,
            s=tagTitle,
            fontsize=24,
            fontweight='bold',
            color=Color.WHITE,
            ha='center',
            va='bottom',
        )

        # Value
        plt.text(
            x=0.25,
            y=0.45,
            s=absoluteValueString,
            fontsize=22,
            fontweight='bold',
            color=Color.WHITE,
            ha='center',
            va='bottom',
        )

        # Change
        triangleImage = image.imread(trianglePath)
        triangleOffsetBox = OffsetImage(arr=triangleImage, zoom=0.4)
        triangleAnnotationBbox = AnnotationBbox(
            offsetbox=triangleOffsetBox,
            xy=(0.05, 0.15),
            frameon=False,
        )
        ax.add_artist(triangleAnnotationBbox)
        plt.text(
            x=0.15,
            y=0.1,
            s=f"{absoluteChangeString} ({relativeChangeString})",
            fontsize=20,
            fontweight='bold',
            color=Color.WHITE,
            ha='left',
            va='bottom',
        )

        # Convert to Image
        plt.tight_layout()
        plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=faceColor)
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')


class ProgressBar(_Chart):

    def produce(self) -> Image:
        # Default setting
        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE,
        })

        # Tạo figure & axes
        fig = plt.figure(
            figsize=(7.2, 1.2),  # width = 12, height = 1.5
            facecolor=self.bgColor
        )
        ax = fig.add_subplot()
        ax.set_facecolor(self.bgColor)
        ax.set_frame_on(False)
        ax.axes.set_xticks([])
        ax.axes.set_yticks([])

        # Data
        data = self.data.squeeze()

        totalBar = plt.barh(
            y=0,
            width=data['Total'],
            height=0.1,
            color=Color.WHITE,
        )[0]
        progressBar = plt.barh(
            y=0,
            width=data['At'],
            height=0.1,
            color=Color.BLUE,
        )[0]
        endCircleTotal = patches.Ellipse(
            xy=(data['Total'], 0),
            width=data['Total'] * 0.03,
            height=totalBar.get_height() * 0.92,
            color=Color.WHITE
        )
        startCircleAt = patches.Ellipse(
            xy=(0, 0),
            width=data['Total'] * 0.03,
            height=progressBar.get_height() * 0.92,
            color=Color.BLUE
        )
        endCircleAt = patches.Ellipse(
            xy=(data['At'], 0),
            width=data['Total'] * 0.03,
            height=progressBar.get_height() * 0.92,
            color=Color.BLUE,
        )
        ax.add_patch(endCircleTotal)
        ax.add_patch(startCircleAt)
        ax.add_patch(endCircleAt)

        plt.text(
            x=data['At'],
            y=progressBar.get_height() * 0.8,
            s=f"{data['At']} /{data['Total']} Days",
            va='bottom',
            ha='center',
            color=Color.WHITE,
            fontsize=30,
            weight='bold'
        )

        # Convert to Image
        plt.tight_layout()
        plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=self.bgColor)
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')


class Donut(_Chart):

    def produce(self) -> Image:
        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE,
        })
        # chỉnh cột số thành numeric
        self.data[['Value']] = self.data[['Value']].apply(lambda x: pd.to_numeric(x, downcast='float'))
        fig, ax = plt.subplots(
            figsize=(8, 8),
            facecolor=self.bgColor
        )

        colors = [
            Color.RED,
            Color.YELLOW,
            Color.BLUE,
            Color.PURPLE,
            Color.ORANGE,
            Color.GREEN,
            Color.PINK,
            Color.GRAY,
            Color.JUNGLEGREEN,
            Color.MINT
        ]

        ax.set_prop_cycle(
            color=colors
        )
        ax.set_facecolor(self.bgColor)

        def percentage(i):
            return round((i / sum(self.data['Value']) * 100), 2)

        def getStringValue(x):
            if x == 0:
                return ''
            elif x < 1:  # phần trăm
                return '{:.3f}%'.format(x * 100)
            elif x > 1e9:
                return '{:,.1f} B'.format(x / 1e9)
            elif x > 1e5:
                return '{:,.1f} M'.format(x / 1e6)
            else:
                return '{:,.3f}'.format(x)

        labels = ['{} ({}%)'.format(getStringValue(round(i, 5)), percentage(i)) for i in self.data['Value']]
        wedges, texts = ax.pie(
            self.data['Value'],
            wedgeprops={'linewidth': 0, 'width': 0.5},
            startangle=80
        )
        kw = dict(arrowprops=dict(arrowstyle="-", color='white'), zorder=0, va="center", size=12, color='white')
        yValues = []
        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2 + p.theta1
            y = np.sin(np.deg2rad(ang))
            yValues.append(y)
            x = np.cos(np.deg2rad(ang))
            horizontalAlignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionStyle = f"angle,angleA=0,angleB={ang}"
            kw["arrowprops"].update({"connectionstyle": connectionStyle})
            if len(yValues) > 1 and x > 0 and y > 0 and abs(yValues[i] - yValues[i - 1]) < 0.1:
                coordinateLabelY = y + i * 0.1
            else:
                coordinateLabelY = 1.1 * y
            ax.annotate(
                labels[i],
                xy=(x, y),
                xytext=(1.3 * np.sign(x), coordinateLabelY),
                horizontalalignment=horizontalAlignment,
                **kw
            )
        plt.legend(
            [self.mapBranch.get(self.data.loc[idx, 'BranchID']) + f" - Rank {self.data.loc[idx, 'Rank']}" for idx in self.data.index],
            loc="upper left",
            bbox_to_anchor=(0.88, 0.75),
            prop={'size': 12},
            bbox_transform=fig.transFigure
        )

        # Convert to Image
        plt.tight_layout()
        while True:
            try:
                plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=self.bgColor, bbox_inches='tight')
                break
            except (OSError,):
                pass
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')


class StalkedBar(_Chart):

    def produce(self) -> Image:
        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE,
        })
        self.data[['Staff', 'Intermediary']] = self.data[['Staff', 'Intermediary']].apply(pd.to_numeric)
        df = self.data.set_index('Date')
        df.index.name = None
        # vẽ
        ax = df.plot(kind='bar', stacked=True, figsize=(12, 7), rot=0, color=[Color.CHAMBRAY, Color.ORANGE])

        xLoc = np.arange(self.data.shape[0])
        if self.data.shape[0] == 12:  # MTD
            plt.xticks(xLoc, self.data['Date'].dt.strftime("T%m'%y"), fontsize=13)
        else:  # YTD
            plt.xticks(xLoc, self.data['Date'].dt.strftime("%Y"), fontsize=13)

        ax.set_facecolor(self.bgColor)
        ax.set_axisbelow(True)
        ax.grid(axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        plt.tick_params(
            axis='both',
            left=False,
            top=False,
            right=False,
            bottom=False,
            labelleft=True,
            labeltop=False,
            labelright=False,
            labelbottom=True
        )
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
        for c in ax.containers:
            # Optional: if the segment is small or 0, customize the labels
            labels = [int(v.get_height()) if v.get_height() > 0 else '' for v in c]
            # remove the labels parameter if it's not needed for customized labels
            ax.bar_label(c, labels=labels, label_type='center')

        while True:
            try:
                plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=self.bgColor, bbox_inches='tight')
                break
            except (OSError,):
                pass
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')


class StalkedBarWithBranches(_Chart):

    def produce(self) -> Image:
        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE,
        })
        convertToInt = lambda x: pd.to_numeric(x, downcast='integer')
        self.data[['Staff', 'Intermediary']] = self.data[['Staff', 'Intermediary']].apply(convertToInt)
        # xử lý fake data
        for i in range(0, len(self.data['BranchID'])):
            self.data['BranchID'].iloc[i] = self.mapBranch.get(self.data['BranchID'].iloc[i])
        df = self.data.set_index('BranchID')
        df.index.name = None
        # vẽ
        ax = df.plot(kind='bar', stacked=True, figsize=(13, 7), rot=0, color=[Color.PURPLE, Color.LAVENDER])
        ax.set_facecolor(self.bgColor)
        ax.set_axisbelow(True)
        ax.grid(axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.tick_params(
            axis='both',
            left=False,
            top=False,
            right=False,
            bottom=False,
            labelleft=True,
            labeltop=False,
            labelright=False,
            labelbottom=True
        )
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
        for c in ax.containers:
            # Optional: if the segment is small or 0, customize the labels
            labels = [int(v.get_height()) if v.get_height() > 0 else '' for v in c]
            # remove the labels parameter if it's not needed for customized labels
            ax.bar_label(c, labels=labels, label_type='center')
        while True:
            try:
                plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=self.bgColor, bbox_inches='tight')
                break
            except (OSError,):
                pass
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')


class GroupedBar(_Chart):

    def produce(self) -> Image:

        plt.rcParams.update({
            'font.family': 'Arial',
            'text.color': Color.WHITE,
            'axes.labelcolor': Color.WHITE
        })
        convertToInt = lambda x: pd.to_numeric(x, downcast='integer')
        self.data[['Actual', 'Target']] = self.data[['Actual', 'Target']].apply(convertToInt)
        self.data['ratio'] = self.data['Actual'] / self.data['Target']
        for i in range(0, len(self.data['ratio'])):
            if self.data['ratio'].iloc[i] == float('inf'):
                self.data['ratio'].iloc[i] = 0
        branch = [self.mapBranch.get(i) for i in self.data['BranchID']]
        data = {
            'Actual': tuple(self.data['Actual']),
            'Target': tuple(self.data['Target'])
        }
        x = np.arange(len(branch))
        width = 0.25
        multiplier = 0
        fig, ax = plt.subplots(figsize=(12.5, 6), facecolor=self.bgColor)
        ax.set_prop_cycle(color=[Color.PURPLE, Color.ORANGE])
        for attribute, measurement in data.items():
            offset = width * multiplier
            labelAdjustment = [
                '{:.3f}%'.format(a * 100) if 0 < a < 1 else
                '{:,.1f}B'.format(a / 1e9) if a > 1e9 else
                '{:,.1f}M'.format(a / 1e6) if a > 1e4 else
                a for a in measurement
            ]
            rects = ax.bar(x + offset, measurement, width, label=attribute)
            ax.bar_label(rects, padding=0, label_type='edge', labels=labelAdjustment)
            multiplier += 1
        plt.tick_params(
            axis='both',
            length=0,
            left=False,
            top=False,
            right=False,
            bottom=False,
            labelleft=False,
            labeltop=False,
            labelright=False,
            labelbottom=True
        )
        plt.grid(False)
        ax.set_facecolor(self.bgColor)
        ax.set_xticks(x + width, branch)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)

        for i, v in enumerate(self.data['ratio'].values):
            ax.annotate(str(round(v * 100, 2)) + "%", xy=(i, 0), xytext=(0, 360), textcoords='offset points')

        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        plt.grid(False)
        # Convert to Image
        plt.tight_layout()
        while True:
            try:
                plt.savefig(r'temp\tempImage.png', dpi=256, facecolor=self.bgColor, bbox_inches='tight')
                break
            except (OSError,):
                pass
        time.sleep(0.2)
        return Image.open(r'temp\tempImage.png')
