/*YTD*/

/*Trailing - Fee Income (So sánh 5 năm gần nhất) */

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
        AND [Measure] = 'Fee Income'
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
		DATETIMEFROMPARTS([YearlyTargetByBranch].[Year],12,31,0,0,0,0) [Date]
		, [YearlyTargetByBranch].[BranchID]
		, ISNULL(SUM([ValueAllBrancheshByDate].[Actual]),0) [Actual]
		, MAX([YearlyTargetByBranch].[Target]) [Target]
	FROM [YearlyTargetByBranch]
	LEFT JOIN [ValueAllBrancheshByDate]
		ON [YearlyTargetByBranch].[Year] = YEAR([ValueAllBrancheshByDate].[Date])
		AND [YearlyTargetByBranch].[BranchID] = [ValueAllBrancheshByDate].[BranchID]
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
