/*MTD*/

/* Headline Tag - Market Share (Phần trăm hoàn thành chỉ tiêu tháng - Thị phần) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonthOfCurrentYear DATETIME;
SET @FirstDateOfMonthOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfMonthOfPreviousYear DATETIME;
SET @FirstDateOfMonthOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),MONTH(@DateOfPreviousYear),1,0,0,0,0));

DECLARE @MarketTradingValueOfPreviousPeriod DECIMAL(30,2);
SET @MarketTradingValueOfPreviousPeriod = (
	SELECT
		SUM([TongGiaTriGiaoDich]) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] BETWEEN @FirstDateOfMonthOfPreviousYear AND @DateOfPreviousYear
);

DECLARE @MarketTradingValueOfCurrentPeriod DECIMAL(30,2);
SET @MarketTradingValueOfCurrentPeriod = (
	SELECT
		SUM([TongGiaTriGiaoDich]) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] BETWEEN @FirstDateOfMonthOfCurrentYear AND @Date
);

WITH

[BranchTarget] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Market Share'
)

, [ValueByBranchOfPreviousPeriod] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[value]) / @MarketTradingValueOfPreviousPeriod / 2 [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonthOfPreviousYear AND @DateOfPreviousYear
	GROUP BY [relationship].[branch_id]
)

, [ValueByBranchOfCurrentPeriod] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[value]) / @MarketTradingValueOfCurrentPeriod / 2 [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonthOfCurrentYear AND @Date
	GROUP BY [relationship].[branch_id]
)

, [result] AS (
	SELECT
		[BranchTarget].[BranchID]
		, ISNULL([ValueByBranchOfCurrentPeriod].[MarketShare],0) [MarketShare]
		, ISNULL([ValueByBranchOfCurrentPeriod].[MarketShare],0) - ISNULL([ValueByBranchOfPreviousPeriod].[MarketShare],0) [AbsoluteChange]
		, CASE 
			WHEN ISNULL([ValueByBranchOfPreviousPeriod].[MarketShare],0) = 0 THEN 0
			ELSE ISNULL([ValueByBranchOfCurrentPeriod].[MarketShare],0) / [ValueByBranchOfPreviousPeriod].[MarketShare] - 1
		END [RelativeChange]
	FROM [BranchTarget]
	LEFT JOIN [ValueByBranchOfCurrentPeriod]
		ON [BranchTarget].[BranchID] = [ValueByBranchOfCurrentPeriod].[BranchID]
	LEFT JOIN [ValueByBranchOfPreviousPeriod]
		ON [BranchTarget].[BranchID] = [ValueByBranchOfPreviousPeriod].[BranchID]
)

SELECT
	SUM([MarketShare]) [MarketShare]
	, SUM([AbsoluteChange]) [AbsoluteChange]
	, SUM([RelativeChange]) [RelativeChange]
FROM [result]


END