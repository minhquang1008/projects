/*MTD - BOM - CoSo*/

/*Actual vs Target - Market Share (Thị phần - Thực tế và chỉ tiêu) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @MarketTradingValue DECIMAL(30,2);
SET @MarketTradingValue = (
	SELECT
		CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] BETWEEN @FirstDateOfMonth AND @Date
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
		, CAST(CAST(SUM([trading_record].[value]) AS DECIMAL(30,8)) / @MarketTradingValue / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonth AND @Date
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