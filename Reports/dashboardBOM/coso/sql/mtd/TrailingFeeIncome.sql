/*MTD*/

/*Trailing - Fee Income*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

WITH 

[MonthlyTargetByBranch] AS (
    SELECT 
        [BranchID] 
		, [Year]
        , CAST([Target] / 12 AS DECIMAL(30,2)) [Target]
    FROM [BranchTargetByYear] 
	WHERE [Year] IN (YEAR(@Since), YEAR(@Date))
        AND [Measure] = 'Fee Income'
)

, [Index] AS (
	SELECT DISTINCT
		EOMONTH([Date]) [Date]
		, [z].[BranchID]
	FROM [Date]
	CROSS JOIN (SELECT DISTINCT [BranchID] FROM [MonthlyTargetByBranch]) [z]
	WHERE [Date] BETWEEN  @Since AND @Date
)

, [ValueAllBrancheshByDate] AS (
	SELECT
		[trading_record].[date] [Date]
		, [relationship].[branch_id] [BranchID]
		, SUM([trading_record].[fee]) [Actual]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[date] = [trading_record].[date]
		AND [relationship].[sub_account] = [trading_record].[sub_account]
	WHERE [trading_record].[date] BETWEEN @Since AND @Date
	GROUP BY [relationship].[branch_id], [trading_record].[date]
)

, [RawResult] AS (
	SELECT
		EOMONTH([ValueAllBrancheshByDate].[Date]) [Date]
		, [MonthlyTargetByBranch].[BranchID]
		, ISNULL(SUM([ValueAllBrancheshByDate].[Actual]),0) [Actual]
		, MAX([MonthlyTargetByBranch].[Target]) [Target]
	FROM [MonthlyTargetByBranch]
	LEFT JOIN [ValueAllBrancheshByDate]
		ON [MonthlyTargetByBranch].[Year] = YEAR([ValueAllBrancheshByDate].[Date])
		AND [MonthlyTargetByBranch].[BranchID] = [ValueAllBrancheshByDate].[BranchID]
	GROUP BY [MonthlyTargetByBranch].[BranchID], EOMONTH([ValueAllBrancheshByDate].[Date])
)

SELECT 
	[Index].[Date]
	, SUM(ISNULL([RawResult].[Actual],0)) [Actual]
	, SUM(ISNULL([RawResult].[Target],0)) [Target]
FROM [Index]
LEFT JOIN [RawResult]
	ON [Index].[Date] = [RawResult].[Date]
	AND [Index].[BranchID] = [RawResult].[BranchID]
GROUP BY [Index].[Date]
ORDER BY 1


END