/*MTD*/

/* Fluctuation - Fee Income (Biến động phí giao dịch) */

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
		AND [Measure] = 'Fee Income'
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
		[trading_record].[date] [Date]
		, [relationship].[branch_id] [BranchID]
		, SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [trading_record].[date] = [relationship].[date]
		AND [trading_record].[sub_account] = [relationship].[sub_account]
	WHERE [trading_record].[date] BETWEEN @Since AND @Date
		AND DAY([trading_record].[date]) <= DAY(@Date)
	GROUP BY [relationship].[branch_id], [trading_record].[date]
)

SELECT
	[Index].[EndOfPeriod] [Date]
	, ISNULL(SUM([ValueByBranchByDate].[FeeIncome]),0) [Value]
FROM [Index]
LEFT JOIN [ValueByBranchByDate]
	ON [Index].[Date] = [ValueByBranchByDate].[Date]
	AND [Index].[BranchID] = [ValueByBranchByDate].[BranchID]

GROUP BY [Index].[EndOfPeriod]
ORDER BY [Index].[EndOfPeriod]


END
