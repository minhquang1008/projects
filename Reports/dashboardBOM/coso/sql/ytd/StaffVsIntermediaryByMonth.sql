/*YTD - BOM - CoSo*/

/*Stacked column - Staff vs Intermediary - trục X thể hiện theo tháng*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATETIMEFROMPARTS(YEAR(@Date)-4,1,1,0,0,0,0);

WITH 

[Index] AS (
	SELECT DISTINCT
		DATETIMEFROMPARTS(YEAR([Date]),12,31,0,0,0,0) [Date]
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
		MAX([Ngay]) OVER (PARTITION BY YEAR([Ngay])) [MaxDate]
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
		CASE
			WHEN [MaxDate] = DATETIMEFROMPARTS(YEAR([MaxDate]),12,31,0,0,0,0) THEN [MaxDate]
			ELSE DATETIMEFROMPARTS(YEAR([MaxDate]),12,31,0,0,0,0)
		END [Date]
		, [BrokerID]
		, [BranchID]
	FROM [112701.Flex] 
	WHERE [MaxDate] = [Ngay]
)

, [BrokerNumber] AS (
	SELECT
		DATETIMEFROMPARTS(YEAR([Date]),12,31,0,0,0,0) [Date]
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