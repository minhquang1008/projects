/*MTD - BOM*/

/*Trailing - New Accounts*/

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
        AND [Measure] = 'New Accounts'
)

, [Index] AS (
	SELECT DISTINCT
		EOMONTH([Date]) [Date]
		, [z].[BranchID]
	FROM [Date]
	CROSS JOIN (SELECT DISTINCT [BranchID] FROM [MonthlyTargetByBranch]) [z]
	WHERE [Date] BETWEEN  @Since AND @Date
)

, [Rel] AS (
	SELECT DISTINCT
		[date] [Date]
		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
	WHERE [date] BETWEEN @Since AND @Date
)

, [ValueAllBrancheshByDate] AS (
	SELECT
		[Rel].[Date] 
		, [Rel].[BranchID]
		, ISNULL(COUNT(*),0) [Actual]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [customer_change].[account_code]
		AND [Rel].[Date] = [customer_change].[open_date]
	WHERE [customer_change].[open_date] BETWEEN @Since AND @Date
		AND [customer_change].[open_or_close] = 'Mo'
		AND [Rel].[BrokerID] IS NOT NULL -- không tính các tài khoản chưa duyệt nên chưa có môi giới
	GROUP BY [Rel].[BranchID], [Rel].[Date] 
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