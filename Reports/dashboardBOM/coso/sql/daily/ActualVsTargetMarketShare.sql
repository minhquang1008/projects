/*Daily - BOM - CoSo*/

/*Actual vs Target - Market Share (Thị phần - Thực tế và chỉ tiêu)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @TodayMarketTradingValue DECIMAL(30,2);
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
        , CAST(CAST([Target] AS FLOAT) AS DECIMAL(30,8)) [MarketShare]
    FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Market Share'
)

, [BranchActual] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, CAST(CAST(SUM([trading_record].[value]) AS DECIMAL(30,8)) / @TodayMarketTradingValue / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Date
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
	GROUP BY [relationship].[branch_id]
)

SELECT
	[TargetByBranch].[BranchID]
	, ISNULL([BranchActual].[MarketShare],0) [Actual]
    , [TargetByBranch].[MarketShare] [Target]
FROM [TargetByBranch]
LEFT JOIN [BranchActual]
    ON [TargetByBranch].[BranchID] = [BranchActual].[BranchID]
ORDER BY 1


END