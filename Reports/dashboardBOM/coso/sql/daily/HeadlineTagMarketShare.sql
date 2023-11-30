/*Daily - BOM - CoSo*/

/*Headline Tag - Market Share (Phần trăm hoàn thành chỉ tiêu ngày - Thị phần) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Prev DATETIME;
SET @Prev = (
	SELECT MIN([Date])
	FROM (
		SELECT TOP 2
			[Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
		ORDER BY [Date] DESC
	) [z]
);

DECLARE @PrevMarketTradingValue DECIMAL(30,8);
SET @PrevMarketTradingValue = (
	SELECT
		CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] = @Prev
);

DECLARE @TodayMarketTradingValue DECIMAL(30,8);
SET @TodayMarketTradingValue = (
	SELECT
		CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] = @Date
);

WITH

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Market Share'
)

, [PrevMarketShare] AS (
	SELECT
		CAST(CAST(SUM([trading_record].[value]) AS DECIMAL(30,8)) / @PrevMarketTradingValue / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Prev
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

, [TodayMarketShare] AS (
	SELECT
		CAST(CAST(SUM([trading_record].[value]) AS DECIMAL(30,8)) / @TodayMarketTradingValue / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

SELECT
	[TodayMarketShare].[MarketShare] [MarketShare]
	, [TodayMarketShare].[MarketShare] - [PrevMarketShare].[MarketShare] [AbsoluteChange]
	, CASE 
		WHEN [PrevMarketShare].[MarketShare] = 0 THEN 0
		ELSE [TodayMarketShare].[MarketShare] / [PrevMarketShare].[MarketShare] - 1
	END [RelativeChange]
FROM [PrevMarketShare]
CROSS JOIN [TodayMarketShare]


END

