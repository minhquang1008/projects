/*YTD*/

/*Trailing - Market Share*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATETIMEFROMPARTS(YEAR(@Date)-4,1,1,0,0,0,0);

WITH 

[MarketTradingValue] AS (
	SELECT
		DATETIMEFROMPARTS(YEAR([Ngay]),12,31,0,0,0,0) [Date]
		, CAST(SUM([TongGiaTriGiaoDich]) AS DECIMAL(30,2)) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] BETWEEN @Since AND @Date
	GROUP BY DATETIMEFROMPARTS(YEAR([Ngay]),12,31,0,0,0,0)
)

, [YearlyTargetByBranch] AS (
    SELECT 
		[Year]
		, [BranchID]
        , CAST([Target] AS DECIMAL(30,10)) [Target]
    FROM [BranchTargetByYear] 
	WHERE [Year] BETWEEN YEAR(@Since) AND YEAR(@Date)
        AND [Measure] = 'Market Share'
)

, [ValueAllBranchesByDate] AS (
	SELECT
		DATETIMEFROMPARTS(YEAR([trading_record].[date]),12,31,0,0,0,0) [Date]
		, [relationship].[branch_id] [BranchID]
		, SUM([trading_record].[value]) [Value]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @Since AND @Date
	GROUP BY [trading_record].[date], [relationship].[branch_id]	

)

, [RawResult] AS (
	SELECT
		[ValueAllBranchesByDate].[Date] [Date]
		, SUM([ValueAllBranchesByDate].[Value]) [Value]
		, MAX([YearlyTargetByBranch].[Target]) [Target]
	FROM [ValueAllBranchesByDate]
	INNER JOIN [YearlyTargetByBranch]
		ON [YearlyTargetByBranch].[BranchID] = [ValueAllBranchesByDate].[BranchID]
		AND [YearlyTargetByBranch].[Year] = YEAR([ValueAllBranchesByDate].[date])
	GROUP BY [ValueAllBranchesByDate].[Date]
)

SELECT
	[RawResult].[Date]
	, [RawResult].[Value] / [MarketTradingValue].[TradingValue] / 2 [Actual]
	, [RawResult].[Target]
FROM [RawResult]
LEFT JOIN [MarketTradingValue]
	ON [MarketTradingValue].[Date] = [RawResult].[Date]
ORDER BY 1


END