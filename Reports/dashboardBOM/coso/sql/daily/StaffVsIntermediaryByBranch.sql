/*Daily - BOM - CoSo*/

/*Stacked column - Staff vs Intermediary*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;


WITH

[Branch] AS (
    SELECT DISTINCT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
)

, [BrokerList] AS (
	SELECT DISTINCT
		[MaCN] [BranchID]
		, [Ma]
	FROM [112701]
	WHERE [Ngay] = @Date
		AND [CoHieuLuc] = N'Hoạt động'
		AND (
			ISNUMERIC([Ma]) = 1
			OR [Ma] LIKE 'A%'
		)
)

, [BrokerType] AS (
	SELECT
		[BranchID]
		, CASE
			WHEN ISNUMERIC([Ma]) = 1 THEN 'STAFF'
			ELSE 'INTERMEDIARY'
		END [brokerType]
	FROM [BrokerList]
)

, [result] AS (
	SELECT
		[BranchID]
		, COUNT(CASE WHEN [brokerType] = 'STAFF' THEN 1 ELSE NULL END) - 1 [Staff]
		, COUNT(CASE WHEN [brokerType] = 'INTERMEDIARY' THEN 1 ELSE NULL END) [Intermediary]
	FROM [BrokerType]
	GROUP BY [BranchID]
)

SELECT
	[Branch].[BranchID],
	[Staff],
	[Intermediary]
FROM [Branch]
LEFT JOIN [result]
	ON [result].[BranchID] = [Branch].[BranchID]
ORDER BY 1


END