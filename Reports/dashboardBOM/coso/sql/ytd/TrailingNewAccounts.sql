/*YTD*/

/*Trailing - New Accounts*/

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
        AND [Measure] = 'New Accounts'
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