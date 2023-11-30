/*Daily - BOM - CoSo*/

/*Total branches - Market share*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @TodayMarketTradingValue DECIMAL(30,8);
SET @TodayMarketTradingValue = (
	SELECT
		CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] = @Date
);

WITH

[Branch] AS (
    SELECT DISTINCT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
)

, [TargetByBranch] AS (
    SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'Market Share'
        AND [Year] = YEAR(@Date)
)

, [ValueTotalBranches] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, CAST(CAST(SUM([trading_record].[value]) AS DECIMAL(30,8)) / @TodayMarketTradingValue / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
	GROUP BY [relationship].[branch_id]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [MarketShare]
		, CASE [MarketShare] 
			WHEN 0 THEN 0
			ELSE [MarketShare] / (SELECT SUM([MarketShare]) FROM [ValueTotalBranches])
		END [Contribution]
	FROM [ValueTotalBranches]
)

SELECT
	RANK() OVER(ORDER BY ISNULL([MarketShare], 0) DESC) [Rank]
	, [Branch].[BranchID]
	, ISNULL([MarketShare], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]
ORDER BY 1


END