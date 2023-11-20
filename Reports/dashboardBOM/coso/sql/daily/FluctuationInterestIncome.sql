/*Daily*/

/*Fluctuation - Interest Income (Biến động lãi vay ký quỹ) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = (
	SELECT [Date] FROM (
		SELECT ROW_NUMBER() OVER (ORDER BY [Date] DESC) [No], [Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
	) [z] WHERE [No] = 180
);


WITH

[BranchTarget] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Interest Income'
)

, [WorkDays] AS (
	SELECT 
		[Date]
	FROM [Date]
	WHERE [Work] = 1
		AND [Date] BETWEEN @Since AND @Date
)

, [Index] AS (
	SELECT 
		[WorkDays].[Date]
		, [BranchTarget].[BranchID]
	FROM [BranchTarget] CROSS JOIN [WorkDays]
)

, [ValueByBranchByDate] AS (
	SELECT
		[rln0019].[date] [Date]
		, [relationship].[branch_id] [BranchID]
		, SUM([rln0019].[interest]) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [rln0019].[date] = [relationship].[date]
		AND [rln0019].[sub_account] = [relationship].[sub_account]
	WHERE [rln0019].[date] BETWEEN @Since AND @Date
	GROUP BY [relationship].[branch_id], [rln0019].[date]
)

SELECT
	[Index].[Date]
	, ISNULL(SUM([ValueByBranchByDate].[InterestIncome]),0) [Value]
FROM [Index]
LEFT JOIN [ValueByBranchByDate]
	ON [Index].[Date] = [ValueByBranchByDate].[Date]
	AND [Index].[BranchID] = [ValueByBranchByDate].[BranchID]

GROUP BY [Index].[Date]
ORDER BY [Index].[Date]


END
