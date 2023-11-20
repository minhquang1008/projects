/*YTD*/

/*Trailing - Interest Income*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATETIMEFROMPARTS(YEAR(@Date)-4,1,1,0,0,0,0);

WITH 

[YearlyTargetByBranch] AS (
    SELECT 
        [BranchID] 
		, [Year]
        , CAST([Target] AS DECIMAL(30,2)) [Target]
    FROM [BranchTargetByYear] 
	WHERE [Year] BETWEEN YEAR(@Since) AND YEAR(@Date)
        AND [Measure] = 'Interest Income'
)

, [ValueAllBranchesByDate] AS (
	SELECT
		[rln0019].[date] [Date]
		, [relationship].[branch_id] [BranchID]
		, SUM([rln0019].[interest]) [Actual]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[date] = [rln0019].[date]
		AND [relationship].[sub_account] = [rln0019].[sub_account]
	WHERE [rln0019].[date] BETWEEN @Since AND @Date
	GROUP BY [relationship].[branch_id], [rln0019].[date]
)

, [RawResult] AS (
	SELECT
		DATETIMEFROMPARTS([YearlyTargetByBranch].[Year],12,31,0,0,0,0) [Date]
		, [YearlyTargetByBranch].[BranchID]
		, ISNULL(SUM([ValueAllBranchesByDate].[Actual]),0) [Actual]
		, MAX([YearlyTargetByBranch].[Target]) [Target]
	FROM [YearlyTargetByBranch]
	LEFT JOIN [ValueAllBranchesByDate]
		ON [YearlyTargetByBranch].[Year] = YEAR([ValueAllBranchesByDate].[Date])
		AND [YearlyTargetByBranch].[BranchID] = [ValueAllBranchesByDate].[BranchID]
	GROUP BY [YearlyTargetByBranch].[BranchID], DATETIMEFROMPARTS([YearlyTargetByBranch].[Year],12,31,0,0,0,0)
)

SELECT 
	[Date]
	, SUM(ISNULL([RawResult].[Actual],0)) [Actual]
	, SUM(ISNULL([RawResult].[Target],0)) [Target]
FROM [RawResult]
GROUP BY [Date]
ORDER BY 1


END