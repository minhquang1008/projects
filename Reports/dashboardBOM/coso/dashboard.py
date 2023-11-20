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
    GroupedBar,
    TrailingBars,
    Donut,
    StalkedBar,
    StalkedBarWithBranches
)


class _Dashboard(ABC):

    def __init__(self, dataContainer):

        # Instantiate data container
        self.dataContainer = dataContainer

        # Instantiate artists
        self.artist = Artist(domain='CoSo')

        # Starting location:

        self.startFirstRowX = 20
        self.startFirstRowY = 500

        if self.__class__.__name__ == 'Daily':
            self.startFromSecondRowX = 1300
        else:
            self.startFromSecondRowX = self.startFirstRowX

    def _drawDayProgress(self):
        table = self.dataContainer.get('DayProgress')
        artist = self.artist
        artist.draw(
            table=table,
            chart=ProgressBar(artist.bgColor),
            topLeft=(5800, 200)
        )

    def _drawOverviewCompletionRatio(self):
        table = self.dataContainer.get('OverviewCompletionRatio')
        artist = self.artist
        artist.draw(
            table=table,
            chart=CompletionRings(artist.bgColor),
            topLeft=(self.startFirstRowX, self.startFirstRowY)
        )

    def _drawHeadlineTagMarketShare(self):
        table = self.dataContainer.get('HeadlineTagMarketShare')
        artist = self.artist
        artist.draw(
            table=table,
            chart=InfoTag(artist.bgColor),
            topLeft=(self.startFirstRowX + 1930, self.startFirstRowY + 100)
        )

    def _drawHeadlineTagFeeIncome(self):
        table = self.dataContainer.get('HeadlineTagFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=InfoTag(artist.bgColor),
            topLeft=(self.startFirstRowX + 1930, self.startFirstRowY + 900),
        )

    def _drawHeadlineTagInterestIncome(self):
        table = self.dataContainer.get('HeadlineTagInterestIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=InfoTag(artist.bgColor),
            topLeft=(self.startFirstRowX + 2930, self.startFirstRowY + 100),
        )

    def _drawHeadlineTagNewAccounts(self):
        table = self.dataContainer.get('HeadlineTagNewAccounts')
        artist = self.artist
        artist.draw(
            table=table,
            chart=InfoTag(artist.bgColor),
            topLeft=(self.startFirstRowX + 2930, self.startFirstRowY + 900),
        )

    def _drawFluctuationFeeIncome(self):
        table = self.dataContainer.get('FluctuationFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=FluctuationLine(artist.bgColor),
            topLeft=(self.startFirstRowX + 4130, self.startFirstRowY + 200),
        )

    def _drawFluctuationInterestIncome(self):
        table = self.dataContainer.get('FluctuationInterestIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=FluctuationLine(artist.bgColor),
            topLeft=(self.startFirstRowX + 6150, self.startFirstRowY + 200),
        )

    # row 2 ----------------------------------------------------------------------------------------------------
    def _drawMarketShareByBranch(self):
        table = self.dataContainer.get('ActualVsTargetMarketShare')
        artist = self.artist
        artist.draw(
            table=table,
            chart=GroupedBar(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 50, self.startFirstRowY + 2100),
        )

    def _drawTotalBranchesByMarketShare(self):
        table = self.dataContainer.get('TotalBranchesMarketShare')
        artist = self.artist
        artist.draw(
            table=table,
            chart=Donut(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 2100),
        )

    def _drawCompareMarketShareOf12Months(self):
        table = self.dataContainer.get('TrailingMarketShare')
        artist = self.artist
        artist.draw(
            table=table,
            chart=TrailingBars(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 5800, self.startFirstRowY + 2100),
        )

    # row 3 ----------------------------------------------------------------------------------------------------
    def _drawTradingFeeByBranch(self):
        table = self.dataContainer.get('ActualVsTargetFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=GroupedBar(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 50, self.startFirstRowY + 4100),
        )

    def _drawTotalBranchesByTradingFee(self):
        table = self.dataContainer.get('TotalBranchesFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=Donut(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 4100),
        )

    def _drawCompareTradingFeeOf12Months(self):
        table = self.dataContainer.get('TrailingFeeIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=TrailingBars(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 5800, self.startFirstRowY + 4100),
        )

    # row 4 ----------------------------------------------------------------------------------------------------
    def _drawMarginInterestByBranch(self):
        table = self.dataContainer.get('ActualVsTargetInterestIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=GroupedBar(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 50, self.startFirstRowY + 6100),
        )

    def _drawTotalBranchesByMarginInterest(self):
        table = self.dataContainer.get('TotalBranchesInterestIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=Donut(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 6100),
        )

    def _drawCompareMarketInterestOf12Months(self):
        table = self.dataContainer.get('TrailingInterestIncome')
        artist = self.artist
        artist.draw(
            table=table,
            chart=TrailingBars(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 5800, self.startFirstRowY + 6100),
        )

    # row 5 ----------------------------------------------------------------------------------------------------
    def _drawNewAccountByBranch(self):
        table = self.dataContainer.get('ActualVsTargetNewAccounts')
        artist = self.artist
        artist.draw(
            table=table,
            chart=GroupedBar(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 50, self.startFirstRowY + 7900),
        )

    def _drawTotalBranchesByNewAccount(self):
        table = self.dataContainer.get('TotalBranchesNewAccounts')
        artist = self.artist
        artist.draw(
            table=table,
            chart=Donut(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 8100),
        )

    def _drawCompareNewAccountOf12Months(self):
        table = self.dataContainer.get('TrailingNewAccounts')
        artist = self.artist
        artist.draw(
            table=table,
            chart=TrailingBars(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 5800, self.startFirstRowY + 7900),
        )

    # row 6 ----------------------------------------------------------------------------------------------------
    def _drawStaffAndIntermediaryByBranch(self):
        table = self.dataContainer.get('StaffVsIntermediaryByBranch')
        artist = self.artist
        artist.draw(
            table=table,
            chart=StalkedBarWithBranches(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 9700),
        )

    def _drawTotalBranchesByStaffAndIntermediary(self):
        table = self.dataContainer.get('TotalBranchesStaffVsIntermediary')
        artist = self.artist
        artist.draw(
            table=table,
            chart=Donut(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 9900),
        )

    def _drawCompareStaffAndIntermediaryOf12Months(self):
        table = self.dataContainer.get('StaffVsIntermediaryByMonth')
        artist = self.artist
        artist.draw(
            table=table,
            chart=StalkedBar(artist.bgColor),
            topLeft=(self.startFromSecondRowX + 5800, self.startFirstRowY + 9700),
        )

    def _writeHeader(self):
        dateString = self.dataContainer.dataDate.strftime('%d.%m.%Y')
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'Daily':
            text = f'STOCK COMPANY PERFORMANCE\nDaily {dateString}'
        elif className == 'MTD':
            text = f'STOCK COMPANY PERFORMANCE\nMTD {dateString}'
        elif className == 'YTD':
            text = f'STOCK COMPANY PERFORMANCE\nYTD {dateString}'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=120,
            color=Color.WHITE,
            topLeft=(artist.productSize[0] // 2 - 1000, self.startFirstRowY - 380),
            align='center',
            spaceBetweenLines=50,
        )

    def _writeOverviewCompletionRatio(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'Daily':
            text = 'Daily completion rate'
        elif className == 'MTD':
            text = 'Monthly completion rate'
        elif className == 'YTD':
            text = 'Yearly completion rate'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 250, self.startFirstRowY - 170),
            align='left',
        )

    def _writeFluctuationFeeIncome(self):
        artist = self.artist
        artist.write(
            text=f'Trading fee fluctuation',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 4145, self.startFirstRowY + 85),
            align='left',
        )

    def _writeFluctuationInterestIncome(self):
        artist = self.artist
        artist.write(
            text=f'Margin income fluctuation',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 6150, self.startFirstRowY + 85),
            align='left',
        )

    def _writeMarketShareByBranch(self):
        artist = self.artist
        artist.write(
            text=f'Market share by Branch',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 1800),
            align='left',
        )

    def _writeMarketShareByBranchBelow(self):
        artist = self.artist
        artist.write(
            text=f'Completion rate',
            size=80,
            color=Color.WHITE,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 1900),
            align='left',
        )

    def _writeTotalBranchesByMarketShare(self):
        artist = self.artist
        artist.write(
            text=f'Total branches by market share',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 1800),
            align='left',
        )

    def _writeCompareMarketShareOf12Months(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'MTD':
            text = f'Compare market share of 12 months'
        elif className == 'YTD':
            text = f'Compare market share of years'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 5800, self.startFirstRowY + 1800),
            align='center',
            spaceBetweenLines=30
        )

    def _writeTradingFeeByBranch(self):
        artist = self.artist
        artist.write(
            text=f'Trading fee by branch',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 3705),
            align='left',
        )

    def _writeTradingFeeByBranchBelow(self):
        artist = self.artist
        artist.write(
            text=f'Completion rate',
            size=80,
            color=Color.WHITE,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 3805),
            align='left',
        )

    def _writeTotalBranchesByTradingFee(self):
        artist = self.artist
        artist.write(
            text=f'Total branches by trading fee',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 3705),
            align='left',
        )

    def _writeCompareTradingFeeOf12Months(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'MTD':
            text = f'Compare trading fee of 12 months'
        elif className == 'YTD':
            text = f'Compare trading fee of years'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 5800, self.startFirstRowY + 3705),
            align='left',
        )

    def _writeMarginInterestByBranch(self):
        artist = self.artist
        artist.write(
            text=f'Margin interest by branch',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 5760),
            align='left',
        )

    def _writeMarginInterestByBranchBelow(self):
        artist = self.artist
        artist.write(
            text=f'Completion rate',
            size=80,
            color=Color.WHITE,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 5860),
            align='left',
        )

    def _writeTotalBranchesByMarginInterest(self):
        artist = self.artist
        artist.write(
            text=f'Total branches by margin interest',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 5760),
            align='left',
        )

    def _writeCompareMarketInterestOf12Months(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'MTD':
            text = f'Compare market interest of 12 months'
        elif className == 'YTD':
            text = f'Compare market interest of years'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 5800, self.startFirstRowY + 5760),
            align='left',
        )

    def _writeNewAccountByBranch(self):
        artist = self.artist
        artist.write(
            text=f'New account by branch',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 7660),
            align='left',
        )

    def _writeNewAccountByBranchBelow(self):
        artist = self.artist
        artist.write(
            text=f'Completion rate',
            size=80,
            color=Color.WHITE,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 7760),
            align='left',
        )

    def _writeTotalBranchesByNewAccount(self):
        artist = self.artist
        artist.write(
            text=f'Total branches by new account',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 7660),
            align='left',
        )

    def _writeCompareNewAccountOf12Months(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'MTD':
            text = f'Compare new account of 12 months'
        elif className == 'YTD':
            text = f'Compare new account of years'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 5800, self.startFirstRowY + 7660),
            align='left',
        )

    def _writeStaffAndIntermediaryByBranch(self):
        artist = self.artist
        artist.write(
            text=f'Staff & Intermediary by branch',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 250, self.startFirstRowY + 9500),
            align='left',
        )

    def _writeTotalBranchesByStaffAndIntermediary(self):
        artist = self.artist
        artist.write(
            text=f'Total branches by staff headcount',
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFromSecondRowX + 3200, self.startFirstRowY + 9500),
            align='left',
        )

    def _writeCompareStaffAndIntermediaryOf12Months(self):
        artist = self.artist
        className = self.__class__.__qualname__
        if className == 'MTD':
            text = f'Compare staff & intermediary of 12 months'
        elif className == 'YTD':
            text = f'Compare staff & intermediary of years'
        else:
            raise ValueError(f'Invalid Dashboard object {className}')
        artist.write(
            text=text,
            size=80,
            color=Color.GREEN,
            topLeft=(self.startFirstRowX + 5800, self.startFirstRowY + 9500),
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
        self._drawHeadlineTagInterestIncome()
        self._drawHeadlineTagNewAccounts()
        self._drawFluctuationFeeIncome()
        self._drawFluctuationInterestIncome()
        self._drawMarketShareByBranch()
        self._drawTotalBranchesByMarketShare()
        self._drawTradingFeeByBranch()
        self._drawTotalBranchesByTradingFee()
        self._drawMarginInterestByBranch()
        self._drawTotalBranchesByMarginInterest()
        self._drawNewAccountByBranch()
        self._drawTotalBranchesByNewAccount()
        self._drawStaffAndIntermediaryByBranch()
        self._drawTotalBranchesByStaffAndIntermediary()

        # Write text
        self._writeHeader()
        self._writeOverviewCompletionRatio()
        self._writeFluctuationFeeIncome()
        self._writeFluctuationInterestIncome()
        self._writeMarketShareByBranch()
        self._writeMarketShareByBranchBelow()
        self._writeTotalBranchesByMarketShare()
        self._writeTradingFeeByBranch()
        self._writeTradingFeeByBranchBelow()
        self._writeTotalBranchesByTradingFee()
        self._writeMarginInterestByBranch()
        self._writeMarginInterestByBranchBelow()
        self._writeTotalBranchesByMarginInterest()
        self._writeNewAccountByBranch()
        self._writeNewAccountByBranchBelow()
        self._writeTotalBranchesByNewAccount()
        self._writeStaffAndIntermediaryByBranch()
        self._writeTotalBranchesByStaffAndIntermediary()


class MTD(_Dashboard):

    def __init__(self, dataContainer):
        super().__init__(dataContainer)

    def draw(self):
        # Draw chart
        self._drawDayProgress()
        self._drawOverviewCompletionRatio()
        self._drawHeadlineTagMarketShare()
        self._drawHeadlineTagFeeIncome()
        self._drawHeadlineTagInterestIncome()
        self._drawHeadlineTagNewAccounts()
        self._drawFluctuationFeeIncome()
        self._drawFluctuationInterestIncome()
        self._drawMarketShareByBranch()
        self._drawTotalBranchesByMarketShare()
        self._drawCompareMarketShareOf12Months()
        self._drawTradingFeeByBranch()
        self._drawTotalBranchesByTradingFee()
        self._drawCompareTradingFeeOf12Months()
        self._drawMarginInterestByBranch()
        self._drawTotalBranchesByMarginInterest()
        self._drawCompareMarketInterestOf12Months()
        self._drawNewAccountByBranch()
        self._drawTotalBranchesByNewAccount()
        self._drawCompareNewAccountOf12Months()
        self._drawStaffAndIntermediaryByBranch()
        self._drawTotalBranchesByStaffAndIntermediary()
        self._drawCompareStaffAndIntermediaryOf12Months()

        # Write text
        self._writeHeader()
        self._writeOverviewCompletionRatio()
        self._writeFluctuationFeeIncome()
        self._writeFluctuationInterestIncome()
        self._writeMarketShareByBranch()
        self._writeMarketShareByBranchBelow()
        self._writeTotalBranchesByMarketShare()
        self._writeCompareMarketShareOf12Months()
        self._writeTradingFeeByBranch()
        self._writeTradingFeeByBranchBelow()
        self._writeTotalBranchesByTradingFee()
        self._writeMarginInterestByBranch()
        self._writeMarginInterestByBranchBelow()
        self._writeCompareTradingFeeOf12Months()
        self._writeTotalBranchesByMarginInterest()
        self._writeCompareMarketInterestOf12Months()
        self._writeNewAccountByBranch()
        self._writeNewAccountByBranchBelow()
        self._writeTotalBranchesByNewAccount()
        self._writeCompareNewAccountOf12Months()
        self._writeStaffAndIntermediaryByBranch()
        self._writeTotalBranchesByStaffAndIntermediary()
        self._writeCompareStaffAndIntermediaryOf12Months()


class YTD(_Dashboard):

    def __init__(self, dataContainer):
        super().__init__(dataContainer)

    def draw(self):
        # Draw chart
        self._drawDayProgress()
        self._drawOverviewCompletionRatio()
        self._drawHeadlineTagMarketShare()
        self._drawHeadlineTagFeeIncome()
        self._drawHeadlineTagInterestIncome()
        self._drawHeadlineTagNewAccounts()
        self._drawFluctuationFeeIncome()
        self._drawFluctuationInterestIncome()
        self._drawMarketShareByBranch()
        self._drawTotalBranchesByMarketShare()
        self._drawCompareMarketShareOf12Months()
        self._drawTradingFeeByBranch()
        self._drawTotalBranchesByTradingFee()
        self._drawCompareTradingFeeOf12Months()
        self._drawMarginInterestByBranch()
        self._drawTotalBranchesByMarginInterest()
        self._drawCompareMarketInterestOf12Months()
        self._drawNewAccountByBranch()
        self._drawTotalBranchesByNewAccount()
        self._drawCompareNewAccountOf12Months()
        self._drawStaffAndIntermediaryByBranch()
        self._drawTotalBranchesByStaffAndIntermediary()
        self._drawCompareStaffAndIntermediaryOf12Months()

        # Write text
        self._writeHeader()
        self._writeOverviewCompletionRatio()
        self._writeFluctuationFeeIncome()
        self._writeFluctuationInterestIncome()
        self._writeMarketShareByBranch()
        self._writeMarketShareByBranchBelow()
        self._writeTotalBranchesByMarketShare()
        self._writeCompareMarketShareOf12Months()
        self._writeTradingFeeByBranch()
        self._writeTradingFeeByBranchBelow()
        self._writeTotalBranchesByTradingFee()
        self._writeMarginInterestByBranch()
        self._writeMarginInterestByBranchBelow()
        self._writeCompareTradingFeeOf12Months()
        self._writeTotalBranchesByMarginInterest()
        self._writeCompareMarketInterestOf12Months()
        self._writeNewAccountByBranch()
        self._writeNewAccountByBranchBelow()
        self._writeTotalBranchesByNewAccount()
        self._writeCompareNewAccountOf12Months()
        self._writeStaffAndIntermediaryByBranch()
        self._writeTotalBranchesByStaffAndIntermediary()
        self._writeCompareStaffAndIntermediaryOf12Months()