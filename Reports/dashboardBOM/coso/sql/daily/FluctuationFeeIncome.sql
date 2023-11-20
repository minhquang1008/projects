/*Daily*/

/*Fluctuation - Fee Income (Biến động phí giao dịch) */

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
		AND [Measure] = 'Fee Income'
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
		[trading_record].[date] [Date]
		, [relationship].[branch_id] [BranchID]
		, SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [trading_record].[date] = [relationship].[date]
		AND [trading_record].[sub_account] = [relationship].[sub_account]
	WHERE [trading_record].[date] BETWEEN @Since AND @Date
	GROUP BY [relationship].[branch_id], [trading_record].[date]
)

SELECT
	[Index].[Date]
	, ISNULL(SUM([ValueByBranchByDate].[FeeIncome]),0) [Value]
FROM [Index]
LEFT JOIN [ValueByBranchByDate]
	ON [Index].[Date] = [ValueByBranchByDate].[Date]
	AND [Index].[BranchID] = [ValueByBranchByDate].[BranchID]

GROUP BY [Index].[Date]
ORDER BY [Index].[Date]


END
