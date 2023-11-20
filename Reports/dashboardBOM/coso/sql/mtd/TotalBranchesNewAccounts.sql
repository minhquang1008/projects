/*MTD*/

/*Total branches - New Accounts*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

WITH

[Branch] AS (
    SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'New Accounts'
        AND [Year] = YEAR(@Date)
)

, [Rel] AS (
	SELECT DISTINCT
		[relationship].[date] [Date]
		, [relationship].[branch_id] [BranchID]
		, [relationship].[broker_id] [BrokerID]
		, [relationship].[account_code] [AccountCode]
	FROM [relationship]
	WHERE [relationship].[date] BETWEEN @FirstDateOfMonth AND @Date
)

, [ValueTotalBranches] AS (
	SELECT
		[Rel].[BranchID]
		, COUNT(*) [NewAccountsByBroker]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [customer_change].[account_code] = [Rel].[AccountCode]
		AND [customer_change].[open_date] = [Rel].[Date]
	WHERE [customer_change].[open_date] BETWEEN @FirstDateOfMonth AND @Date
		AND [customer_change].[open_or_close] = 'Mo'
		AND [Rel].[BrokerID] IS NOT NULL -- không tính các tài khoản chưa duyệt nên chưa có môi giới
	GROUP BY [Rel].[BranchID]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [NewAccountsByBroker]
		, CAST([NewAccountsByBroker] AS DECIMAL(10,5)) / CAST((SELECT SUM([NewAccountsByBroker]) FROM [ValueTotalBranches]) AS DECIMAL(10,5)) [Contribution]
	FROM [ValueTotalBranches]
)

SELECT	
	[Branch].[BranchID]
	, ISNULL([NewAccountsByBroker], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]

END
