/*MTD - BOM - CoSo*/

/*Stacked column - Staff vs Intermediary - trục X thể hiện theo tháng*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

WITH

[Index] AS (
	SELECT DISTINCT
		EOMONTH([Date]) [Date]
	FROM [Date]
	WHERE [Date] BETWEEN  @Since AND @Date
)

, [Branch] AS (
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
	WHERE [Ngay] BETWEEN @Since AND @Date
		AND [CoHieuLuc] = N'Hoạt động'
		AND [MaCN] IN (SELECT [BranchID] FROM [Branch])
		AND (
			ISNUMERIC([Ma]) = 1
			OR [Ma] LIKE 'A%'
		)
)

, [BrokerList] AS (
	SELECT DISTINCT
		[MaxDate] [Date]
		, [BrokerID]
		, [BranchID]
	FROM [112701.Flex] 
	WHERE [MaxDate] = [Ngay]
)

, [BrokerNumber] AS (
	SELECT
		EOMONTH([Date]) [Date]
		, [BrokerID]
		, [BranchID]
		, CASE
			WHEN ISNUMERIC([BrokerID]) = 1 THEN 'STAFF'
			ELSE 'INTERMEDIARY'
		END [brokerType]
	FROM [BrokerList]
)

SELECT
	[Index].[Date]
	, CASE COUNT(CASE WHEN [brokerType] = 'STAFF' THEN 1 ELSE NULL END)
		WHEN 0 THEN 0
		ELSE COUNT(CASE WHEN [brokerType] = 'STAFF' THEN 1 ELSE NULL END) - 10 -- chỗ này trừ 10 vì ko tính 10 giám đốc chi nhánh
	END [Staff] 
	, COUNT(CASE WHEN [brokerType] = 'INTERMEDIARY' THEN 1 ELSE NULL END) [Intermediary]
FROM [Index]
LEFT JOIN [BrokerNumber]
	ON [BrokerNumber].[Date] = [Index].[Date]
GROUP BY [Index].[Date]
ORDER BY 1


END