/*Daily - BOM - PhaiSinh*/

/*Total branches - Fee Income (Phí giao dịch - by branch, pie chart) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

WITH

[Branch] AS (
    SELECT DISTINCT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
)

, [TargetByBranch] AS (
    SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'Fee Income'
        AND [Year] = YEAR(@Date)
)

, [Rel] AS (
    SELECT DISTINCT
        [account_code] [AccountCode]
        , [broker_id] [BrokerID]
        , [branch_id] [BranchID]
    FROM [relationship]
    WHERE [date] = @Date
)

, [ValueTotalBranches] AS (
	SELECT 
		[Rel].[BranchID] [BranchID]
        , SUM([RRE0018].[PhiGiaoDichPHSThu]) [FeeIncome]
	FROM [RRE0018]
    LEFT JOIN [Rel]
        ON [RRE0018].[SoTaiKhoan] = [Rel].[AccountCode]
    WHERE [RRE0018].[Ngay] = @Date
    GROUP BY [Rel].[BranchID]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [FeeIncome]
		, CASE [FeeIncome] 
			WHEN 0 THEN 0
			ELSE CAST([FeeIncome] / SUM([FeeIncome]) OVER() AS DECIMAL(7,6))
		END [Contribution]
	FROM [ValueTotalBranches]
)

SELECT
	RANK() OVER(ORDER BY ISNULL([FeeIncome], 0) DESC) [Rank]
	, [Branch].[BranchID]
	, ISNULL([FeeIncome], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]
ORDER BY 1


END