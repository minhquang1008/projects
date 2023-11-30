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

, [112701.Flex] AS (
	SELECT
		MAX([Ngay]) OVER (PARTITION BY MONTH([Ngay])) [MaxDate]
		, [Ngay]
		, [Ma] [BrokerID]
		, [MaCN] [BranchID]
		, [CoHieuLuc]
	FROM [112701] 
	WHERE [Ngay] = @Date
		AND [CoHieuLuc] = N'Hoạt động'
		AND [MaCN] IN (SELECT [BranchID] FROM [Branch])
		AND (
			ISNUMERIC([Ma]) = 1
			OR [Ma] LIKE 'A%'
		)
)

, [BrokerList] AS (
	SELECT DISTINCT
		[BrokerID]
		, [BranchID]
	FROM [112701.Flex] 
	WHERE [MaxDate] = [Ngay]
)

, [BrokerNumber] AS (
	SELECT
		[BranchID]
		, CASE
			WHEN ISNUMERIC([BrokerID]) = 1 THEN 'STAFF'
			ELSE 'INTERMEDIARY'
		END [brokerType]
	FROM [BrokerList]
)

SELECT
	[BranchID]
	, COUNT(CASE WHEN [brokerType] = 'STAFF' THEN 1 ELSE NULL END) - 1 [Staff] -- không tính GĐCN nên -1 chỗ này
	, COUNT(CASE WHEN [brokerType] = 'INTERMEDIARY' THEN 1 ELSE NULL END) [Intermediary]
FROM [BrokerNumber]
GROUP BY [BranchID]
ORDER BY 1


END