/*Daily - BOM- CoSo*/

/*Total branches - Staff vs Intermediary*/

/*sửa lại theo yêu cầu bên BMD là không lấy CTV*/

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
		AND ISNUMERIC([Ma]) = 1
)

, [ValueBrokerEachBranch] AS (
	SELECT
		[BranchID]
		, COUNT([Ma]) - 1 [BrokerNum]  -- nhân viên là ko tính giám đốc chi nhánh nên -1 này là bỏ giám đốc chi nhánh đó (rule của BMD)
	FROM [BrokerList]
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
	RANK() OVER(ORDER BY ISNULL([BrokerNum], 0) DESC) [Rank]
	, [Branch].[BranchID]
	, ISNULL([BrokerNum], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]
ORDER BY 1


END