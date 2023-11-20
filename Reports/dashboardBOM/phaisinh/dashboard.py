from abc import ABC, abstractmethod
import sys
sys.path.append('../')
from color import Color
from artist import Artist
from chart import (
    CompletionRings,
    InfoTag,
    FluctuationLine,
    ProgressBar,
    TrailingBars,
    Donut,
    GroupedBar
)


class _Dashboard(ABC):

    def __init__(self, dataContainer):

        # Instantiate data container
        self.dataContainer = dataContainer

        # Instantiate artists
        self.artist = Artist(domain='PhaiSinh')

        # Starting location:
        self.startFirstRowX = 20
        self.startFirstRowY = 700

        # Branch name:
        self.mapBranch = {
            '0101': 'DISTRICT\n03',
            '0102': 'PHU MY\nHUNG',
            '0104': 'DISTRICT \n07',
            '0105': 'TAN\nBINH',
            '0117': 'DISTRICT\n01',
            '0120': 'AMD\n05',
            '0201': 'HA\nNOI',
            '0202': 'THANH\nXUAN',
            '0301': 'HAI\nPHONG',
            '0116': 'AMD\n01',
        }

    def _drawDayProgress(self):
        table = self.dataContainer.get('DayProgress')
        artist = self.artist
        artist.draw(
            table=table,
            chart=ProgressBar(artist.bgColor),
            topLeft=(4000, 300),
        )

    def _drawOverviewCompletionRatio(self):
        table = self.dataContainer.get('OverviewCompletionRatio')
        artist = self.artist
        artist.draw(
            table=table,
            chart=CompletionRings(artist.bgColor),
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY),
        )

    def _drawHeadlineTagMarketShare(self):
        table = self.dataContainer.get('HeadlineTagMarketShare')
        artist = self.artist
        artist.draw(
            table=table,
            chart=InfoTag(artist.bgColor),
            topLeft=(self.startFirstRowX + 2480, self.startFirstRowY + 100),
        )

    def _drawHeadlineTagFeeIncome(self):
        table = self.dataContainer.get('HeadlineTagFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=InfoTag(artist.bgColor),
            topLeft=(self.startFirstRowX + 2480, self.startFirstRowY + 900),
        )

    def _drawFluctuationFeeIncome(self):
        table = self.dataContainer.get('FluctuationFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=FluctuationLine(artist.bgColor),
            topLeft=(self.startFirstRowX + 4000, self.startFirstRowY + 250),
        )

    # row 2 --------------------------------------------------------------------------
    def _drawMarketShareByBranch(self):
        table = self.dataContainer.get('ActualVsTargetMarketShare')
        artist = self.artist
        artist.draw(
            table=table,
            chart=GroupedBar(artist.bgColor),
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY + 2000)
        )

    def _drawTotalBranchesByMarketShare(self):
        table = self.dataContainer.get('TotalBranchesMarketShare')
        artist = self.artist
        artist.draw(
            table=table,
            chart=Donut(artist.bgColor),
            topLeft=(self.startFirstRowX + 3500, self.startFirstRowY + 2200)
        )

    # row 3 --------------------------------------------------------------------------
    def _drawTradingFeeByBranch(self):
        table = self.dataContainer.get('ActualVsTargetFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=GroupedBar(artist.bgColor),
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY + 4200)
        )

    def _drawTotalBranchesByTradingFee(self):
        table = self.dataContainer.get('TotalBranchesFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=Donut(artist.bgColor),
            topLeft=(self.startFirstRowX + 3500, self.startFirstRowY + 4400)
        )

    # row 4 --------------------------------------------------------------------------
    def _drawCompareMarketShareOf12Months(self):
        table = self.dataContainer.get('TrailingMarketShare')
        artist = self.artist
        artist.draw(
            table=table,
            chart=TrailingBars(artist.bgColor),
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY + 6200)
        )

    def _drawCompareTradingFeeOf12Months(self):
        table = self.dataContainer.get('TrailingFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=TrailingBars(artist.bgColor),
            topLeft=(self.startFirstRowX + 3500, self.startFirstRowY + 6200)
        )

    def _writeHeader(self):
        dateString = self.dataContainer.dataDate.strftime('%d.%m.%Y')
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'Daily':
            text = f'DERIVATIVES COMPANY PERFORMANCE\nDaily {dateString}'
        elif className == 'MTD':
            text = f'DERIVATIVES COMPANY PERFORMANCE\nMTD {dateString}'
        elif className == 'YTD':
            text = f'DERIVATIVES COMPANY PERFORMANCE\nYTD {dateString}'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=120,
            color=Color.WHITE,
            topLeft=(artist.productSize[0] // 2 - 1000, self.startFirstRowY - 580),
            align='center',
            spaceBetweenLines=50,
        )

    def _writeOverviewCompletionRatio(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'Daily':
            text = 'Daily completion rate'
        elif className == 'MTD':
            text = 'Mothly completion rate'
        elif className == 'YTD':
            text = 'Yearly completion rate'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY - 170),
            align='left',
        )

    def _writeFluctuationFeeIncome(self):
        artist = self.artist
        artist.write(
            text=f'Trading fee fluctuation',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 4000, self.startFirstRowY + 100),
            align='left',
        )

    def _writeContributionMarketShare(self):
        artist = self.artist
        artist.write(
            text=f'Market share by Branch',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY + 1750),
            align='left'
        )

    def _writeContributionMarketShareBelow(self):
        artist = self.artist
        artist.write(
            text=f'Completion rate',
            size=80,
            color=Color.WHITE,
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY + 1850),
            align='left'
        )

    def _writeContributionFeeIncome(self):
        artist = self.artist
        artist.write(
            text=f'Total  branches by market share',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 3500, self.startFirstRowY + 1750),
            align='left'
        )

    def _writeTop3FeeIncome(self):
        artist = self.artist
        artist.write(
            text=f'Total branches by trading fee',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 3500, self.startFirstRowY + 3750),
            align='left',
        )

    def _writeTrailingFeeIncome(self):
        className = self.__class__.__qualname__
        if className == 'Daily':
            text = f'Trading fee by Branch'
        if className == 'MTD':
            text = f'Trading fee by Branch'
        elif className == 'YTD':
            text = f'Trading fee by Branch'
        artist = self.artist
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY + 3750),
            align='left',
        )

    def _writeTrailingFeeIncomeBelow(self):
        artist = self.artist
        artist.write(
            text='Completion rate',
            size=80,
            color=Color.WHITE,
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY + 3850),
            align='left',
        )

    def _writeCompareMarketShareOf12Months(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'MTD':
            text = f'Compare market share of 12 months (*)'
        elif className == 'YTD':
            text = f'Compare market share of years (*)'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 200, self.startFirstRowY + 6000),
            align='left',
        )

    def _writeCompareTradingFeeOf12Months(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'MTD':
            text = f'Compare trading fee of 12 months (*)'
        elif className == 'YTD':
            text = f'Compare trading fee of years (*)'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 3500, self.startFirstRowY + 6000),
            align='left',
        )

    @abstractmethod
    def draw(self):
        pass


class Daily(_Dashboard):

    def __init__(self, dataContainer):
        super().__init__(dataContainer)

    def draw(self):
        # Draw chart
        self._drawOverviewCompletionRatio()
        self._drawHeadlineTagMarketShare()
        self._drawHeadlineTagFeeIncome()
        self._drawFluctuationFeeIncome()
        self._drawMarketShareByBranch()
        self._drawTotalBranchesByMarketShare()
        self._drawTradingFeeByBranch()
        self._drawTotalBranchesByTradingFee()

        # Write text
        self._writeHeader()
        self._writeOverviewCompletionRatio()
        self._writeFluctuationFeeIncome()
        self._writeContributionMarketShare()
        self._writeContributionMarketShareBelow()
        self._writeContributionFeeIncome()
        self._writeTop3FeeIncome()
        self._writeTrailingFeeIncome()
        self._writeTrailingFeeIncomeBelow()


class MTD(_Dashboard):

    def __init__(self, dataContainer):
        super().__init__(dataContainer)

    def draw(self):
        # Draw chart
        self._drawDayProgress()
        self._drawOverviewCompletionRatio()
        self._drawHeadlineTagMarketShare()
        self._drawHeadlineTagFeeIncome()
        self._drawFluctuationFeeIncome()
        self._drawMarketShareByBranch()
        self._drawTotalBranchesByMarketShare()
        self._drawTradingFeeByBranch()
        self._drawTotalBranchesByTradingFee()
        self._drawCompareMarketShareOf12Months()
        self._drawCompareTradingFeeOf12Months()

        # Write text
        self._writeHeader()
        self._writeOverviewCompletionRatio()
        self._writeFluctuationFeeIncome()
        self._writeContributionMarketShare()
        self._writeContributionMarketShareBelow()
        self._writeContributionFeeIncome()
        self._writeTop3FeeIncome()
        self._writeTrailingFeeIncome()
        self._writeTrailingFeeIncomeBelow()
        self._writeCompareMarketShareOf12Months()
        self._writeCompareTradingFeeOf12Months()


class YTD(_Dashboard):

    def __init__(self, dataContainer):
        super().__init__(dataContainer)

    def draw(self):
        # Draw chart
        self._drawDayProgress()
        self._drawOverviewCompletionRatio()
        self._drawHeadlineTagMarketShare()
        self._drawHeadlineTagFeeIncome()
        self._drawFluctuationFeeIncome()
        self._drawMarketShareByBranch()
        self._drawTotalBranchesByMarketShare()
        self._drawTradingFeeByBranch()
        self._drawTotalBranchesByTradingFee()
        self._drawCompareMarketShareOf12Months()
        self._drawCompareTradingFeeOf12Months()

        # Write text
        self._writeHeader()
        self._writeOverviewCompletionRatio()
        self._writeFluctuationFeeIncome()
        self._writeContributionMarketShare()
        self._writeContributionMarketShareBelow()
        self._writeContributionFeeIncome()
        self._writeTop3FeeIncome()
        self._writeTrailingFeeIncome()
        self._writeTrailingFeeIncomeBelow()
        self._writeCompareMarketShareOf12Months()
        self._writeCompareTradingFeeOf12Months()