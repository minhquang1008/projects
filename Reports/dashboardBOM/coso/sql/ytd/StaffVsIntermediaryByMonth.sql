/*YTD*/

/*Stacked column - Staff vs Intermediary - trục X thể hiện theo tháng */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATETIMEFROMPARTS(YEAR(@Date)-4,1,1,0,0,0,0);

WITH 

[YearlyTargetByBranch] AS (
    SELECT DISTINCT [Year], [BranchID]
    FROM [BranchTargetByYear]
	WHERE [Year] BETWEEN YEAR(@Since) AND YEAR(@Date)
)

, [BrokerList] AS (
	SELECT
		[date]
		, [brokerid]
	FROM [brokerlevel] WHERE [date] BETWEEN @Since AND @Date
	UNION ALL (
		SELECT 
			[date], 
			[leadbrokerid]
		FROM [brokerlevel] WHERE [date] BETWEEN @Since AND @Date
	)
)

, [ValueOfBrokerList] AS (
	SELECT DISTINCT
		DATETIMEFROMPARTS(YEAR([Date]),12,31,0,0,0,0) [Date]
		, [brokerid] [BrokerID]
	FROM [BrokerList]
	WHERE
		[Date] IN (DATETIMEFROMPARTS(YEAR([Date]),12,31,0,0,0,0), @Date)
		AND (
			ISNUMERIC(brokerid) = 1
			OR [brokerid] LIKE 'A%'
		)
)

, [ValueBrokerEachBranch] AS (
	SELECT
		DATETIMEFROMPARTS([YearlyTargetByBranch].[Year],12,31,0,0,0,0) [Date]
		, [YearlyTargetByBranch].[BranchID]
		, CASE
			WHEN ISNUMERIC([brokerid]) = 1 THEN 'STAFF'
			WHEN [brokerid] LIKE 'A%' THEN 'INTERMEDIARY'
		END [brokerType]
	FROM [ValueOfBrokerList]
	LEFT JOIN [broker]
		ON [broker].[broker_id] = [ValueOfBrokerList].[BrokerID]
	RIGHT JOIN [YearlyTargetByBranch]
		ON [YearlyTargetByBranch].[Year] = YEAR([ValueOfBrokerList].[Date])
		AND [broker].[branch_id] = [YearlyTargetByBranch].[BranchID]
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