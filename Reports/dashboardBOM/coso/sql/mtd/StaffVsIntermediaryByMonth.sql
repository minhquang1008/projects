/*MTD*/

/*Stacked column - Staff vs Intermediary - trục X thể hiện theo tháng */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

WITH 

[MonthlyTargetByBranch] AS (
    SELECT DISTINCT [BranchID]
    FROM [BranchTargetByYear] 
	WHERE [Year] = YEAR(@Date)
)

, [BrokerList] AS (
	SELECT 
		[date] [Date]
		, [brokerid] [BrokerID]
	FROM [brokerlevel] WHERE [date] BETWEEN @FirstDateOfYear AND @Date
	UNION ALL
	SELECT [date], [leadbrokerid]
	FROM [brokerlevel] WHERE [date] BETWEEN @FirstDateOfYear AND @Date
)

, [ValueOfBrokerList] AS (
	SELECT DISTINCT
		EOMONTH([BrokerList].[Date]) [Date]
		, [BrokerID]
	FROM [BrokerList]
	WHERE ISNUMERIC(brokerid) = 1
		OR [brokerid] LIKE 'A%'
)

, [ValueBrokerEachBranch] AS (
	SELECT
		[Date]
		, [MonthlyTargetByBranch].[BranchID]
		, CASE
			WHEN ISNUMERIC([brokerid]) = 1 THEN 'STAFF'
			ELSE 'INTERMEDIARY'
		END [brokerType]
	FROM [ValueOfBrokerList]
	LEFT JOIN [broker]
		ON [broker].[broker_id] = [ValueOfBrokerList].[BrokerID]
	RIGHT JOIN [MonthlyTargetByBranch]
		ON [broker].[branch_id] = [MonthlyTargetByBranch].[BranchID]
)

, [ValueBrokerByType] AS (
	SELECT
		[p].[Date],
		[p].[STAFF],
		[p].[INTERMEDIARY]
	FROM [ValueBrokerEachBranch]
	PIVOT (
		COUNT([BranchID]) FOR [brokerType] IN ([STAFF], [INTERMEDIARY])
	) [p]
)

SELECT
	[Date]
	, [STAFF]
	, [INTERMEDIARY]
FROM [ValueBrokerByType]
ORDER BY 1


END