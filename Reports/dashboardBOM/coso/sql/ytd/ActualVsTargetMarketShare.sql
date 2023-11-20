/*YTD*/

/*Actual vs Target - Market Share (Thị phần - Thực tế và chỉ tiêu) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @MarketTradingValueCurrentPeriod DECIMAL(30,2);
SET @MarketTradingValueCurrentPeriod = (
	SELECT
		SUM([TongGiaTriGiaoDich]) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] BETWEEN @FirstDateOfYear AND @Date
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
		, SUM([trading_record].[value]) / @MarketTradingValueCurrentPeriod / 2 [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfYear AND @Date
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