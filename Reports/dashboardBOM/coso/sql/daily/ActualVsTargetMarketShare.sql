/*Daily*/

/*Actual vs Target - Market Share (Thị phần - Thực tế và chỉ tiêu)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @TodayMarketTradingValue DECIMAL(30,2);
SET @TodayMarketTradingValue = (
	SELECT
		SUM([TongGiaTriGiaoDich]) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] = @Date
);

WITH

[BranchTarget] AS (
    SELECT 
        [BranchID] 
        , CAST([Target] AS DECIMAL(7,6)) [MarketShare]
    FROM [BranchTargetByYear] 
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Market Share'
)

, [BranchActual] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[value]) / @TodayMarketTradingValue / 2 [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Date
	GROUP BY [relationship].[branch_id]
)

SELECT
	[BranchTarget].[BranchID]
	, SUM(ISNULL([BranchActual].[MarketShare],0)) [Actual]
    , SUM([BranchTarget].[MarketShare]) [Target]
FROM [BranchTarget]
LEFT JOIN [BranchActual]
    ON [BranchTarget].[BranchID] = [BranchActual].[BranchID]
GROUP BY [BranchTarget].[BranchID]


END