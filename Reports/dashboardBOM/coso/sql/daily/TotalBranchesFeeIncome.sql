﻿/*Daily - BOM - CoSo*/

/*Total branches - Fee Income*/

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

, [ValueTotalBranches] AS (
	SELECT 
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [trading_record].[date] = [relationship].[date]
		AND [trading_record].[sub_account] = [relationship].[sub_account]
	WHERE [trading_record].[date] = @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
	GROUP BY [relationship].[branch_id]
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