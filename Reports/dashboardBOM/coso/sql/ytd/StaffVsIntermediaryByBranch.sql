/*YTD*/

/*Stacked column - Staff vs Intermediary - trục X thể hiện theo chi nhánh */

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
		, CASE
			WHEN ISNUMERIC([brokerid]) = 1 THEN 'STAFF'
			ELSE 'INTERMEDIARY'
		END [brokerType]
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
		, COUNT(CASE WHEN [brokerType] = 'STAFF' THEN 1 ELSE NULL END) [Staff]
		, COUNT(CASE WHEN [brokerType] = 'INTERMEDIARY' THEN 1 ELSE NULL END) [Intermediary]
	FROM [BrokerActual]
	GROUP BY [BranchID]
)

SELECT
	[Branch].[BranchID],
	[Staff],
	[Intermediary]
FROM [Branch]
LEFT JOIN [ValueBrokerEachBranch]
	ON [ValueBrokerEachBranch].[BranchID] = [Branch].[BranchID]


END