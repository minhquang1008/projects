/*MTD*/

/*Total branches - Staff vs Intermediary*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;


WITH

[Branch] AS (
    SELECT DISTINCT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
)

, [AllBroker] AS (
	SELECT [brokerid]
	FROM [brokerlevel] WHERE [date] = @Date
	UNION ALL
	SELECT [leadbrokerid]
	FROM [brokerlevel] WHERE [date] = @Date
)

, [BrokerList] AS (
	SELECT DISTINCT 
		[brokerid] [BrokerID]
	FROM [AllBroker]
)

, [BrokerActual] AS (
	SELECT 
		[BrokerList].[BrokerID]
		, [broker].[branch_id] [BranchID]
	FROM [BrokerList]
	LEFT JOIN [broker]
		ON [broker].[broker_id] = [BrokerList].[BrokerID]
	WHERE
		[branch_id] IS NOT NULL
		AND (
			ISNUMERIC(brokerid) = 1
			OR [brokerid] LIKE 'A%'
		)
)

, [ValueBrokerEachBranch] AS (
	SELECT
		[BranchID]
		, COUNT([BrokerID]) [BrokerNum]
	FROM [BrokerActual]
	GROUP BY [BranchID]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [BrokerNum]
		, CAST([BrokerNum] AS DECIMAL(10,5)) / CAST((SELECT SUM([BrokerNum]) FROM [ValueBrokerEachBranch]) AS DECIMAL(10,5)) [Contribution]
	FROM [ValueBrokerEachBranch]
)

SELECT	
	[Branch].[BranchID],
	ISNULL([BrokerNum], 0) [Value],
	ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]


END