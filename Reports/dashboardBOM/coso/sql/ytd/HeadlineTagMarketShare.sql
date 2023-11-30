/*YTD - BOM - CoSo*/

/*Headline Tag - Market Share (Phần trăm hoàn thành chỉ tiêu tháng - Thị phần)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfCurrentYear DATETIME;
SET @FirstDateOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfPreviousYear DATETIME;
SET @FirstDateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),1,1,0,0,0,0));

DECLARE @MarketTradingValueOfPreviousPeriod DECIMAL(30,2);
SET @MarketTradingValueOfPreviousPeriod = (
	SELECT
		CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear
);

DECLARE @MarketTradingValueOfCurrentPeriod DECIMAL(30,2);
SET @MarketTradingValueOfCurrentPeriod = (
	SELECT
		CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] BETWEEN @FirstDateOfCurrentYear AND @Date
);

WITH

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Market Share'
)

, [ValuePrevPeriod] AS (
	SELECT
		CAST(CAST(SUM([trading_record].[value]) AS DECIMAL(30,8)) / @MarketTradingValueOfPreviousPeriod / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

, [ValueCurrentPeriod] AS (
	SELECT
		CAST(CAST(SUM([trading_record].[value]) AS DECIMAL(30,8)) / @MarketTradingValueOfCurrentPeriod / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfCurrentYear AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

SELECT
	[ValueCurrentPeriod].[MarketShare] [MarketShare]
	, [ValueCurrentPeriod].[MarketShare] - [ValuePrevPeriod].[MarketShare] [AbsoluteChange]
	, CASE 
		WHEN [ValuePrevPeriod].[MarketShare] = 0 THEN 0
		ELSE [ValueCurrentPeriod].[MarketShare] / [ValuePrevPeriod].[MarketShare] - 1
	END [RelativeChange]
FROM [ValuePrevPeriod]
CROSS JOIN [ValueCurrentPeriod]


END
