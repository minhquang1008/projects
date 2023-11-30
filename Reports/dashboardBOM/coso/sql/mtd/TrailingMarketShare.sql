/*MTD - BOM - CoSo*/

/*Trailing - Market Share*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

WITH 

[MarketTradingValue] AS (
	SELECT
		EOMONTH([TXDATE]) [Date]
		, CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] BETWEEN @Since AND @Date
	GROUP BY EOMONTH([TXDATE])
)

, [BranchList] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear] 
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Market Share'
)

, [MonthlyTarget] AS (
    SELECT
		[Year]
		, CAST(SUM(CAST([Target] AS FLOAT)) AS DECIMAL(30,8)) [Target]
	FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
	WHERE [Year] IN (YEAR(@Since), YEAR(@Date))
		AND [Measure] = 'Market Share'
	GROUP BY [Year]
)

, [ValueAllBranchesByDate] AS (
	SELECT
		EOMONTH([trading_record].[date]) [Date]
		, SUM([trading_record].[value]) [Value]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[date] = [trading_record].[date]
		AND [relationship].[sub_account] = [trading_record].[sub_account]
	WHERE [trading_record].[date] BETWEEN @Since AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [BranchList])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
	GROUP BY EOMONTH([trading_record].[date])
)

SELECT
	[ValueAllBranchesByDate].[Date]
	, [ValueAllBranchesByDate].[Value] / [MarketTradingValue].[TradingValue] / 2 [Actual]
	, [MonthlyTarget].[Target]
FROM [MonthlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [MonthlyTarget].[Year]
LEFT JOIN [MarketTradingValue]
	ON [ValueAllBranchesByDate].[Date] = [MarketTradingValue].[Date]
ORDER BY 1


END