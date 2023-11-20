/*MTD*/

/* Fluctuation - Interest Income (Biến động lãi vay ký quỹ) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

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
		, CASE 
			WHEN ISDATE(CONCAT(YEAR([Date]),'-',MONTH([Date]),'-',DAY(@Date))) = 1 
				THEN DATETIMEFROMPARTS(YEAR([Date]),MONTH([Date]),DAY(@Date),0,0,0,0)
			ELSE EOMONTH(DATETIMEFROMPARTS(YEAR([Date]),MONTH([Date]),1,0,0,0,0)) 
		END [EndOfPeriod]
	FROM [Date]
	WHERE [Work] = 1
		AND [Date] BETWEEN @Since AND @Date
		AND DAY([Date]) <= DAY(@Date)
)

, [Index] AS (
	SELECT 
		[WorkDays].[Date]
		, [WorkDays].[EndOfPeriod]
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
		AND DAY([rln0019].[date]) <= DAY(@Date)
	GROUP BY [relationship].[branch_id], [rln0019].[date]
)

SELECT
	[Index].[EndOfPeriod] [Date]
	, ISNULL(SUM([ValueByBranchByDate].[InterestIncome]),0) [Value]
FROM [Index]
LEFT JOIN [ValueByBranchByDate]
	ON [Index].[Date] = [ValueByBranchByDate].[Date]
	AND [Index].[BranchID] = [ValueByBranchByDate].[BranchID]

GROUP BY [Index].[EndOfPeriod]
ORDER BY [Index].[EndOfPeriod]


END
