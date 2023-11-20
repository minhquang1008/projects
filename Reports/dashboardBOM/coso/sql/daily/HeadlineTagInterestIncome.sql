/*Daily*/

/*Headline Tag - Interest Income (Phần trăm hoàn thành chỉ tiêu ngày - Lãi vay ký quỹ) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Prev DATETIME;
SET @Prev = (
	SELECT MIN([Date]) 
	FROM (
		SELECT TOP 2
			[Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
		ORDER BY [Date] DESC
	) [z]
);

WITH

[BranchTarget] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Interest Income'
)

, [PrevValueByBranch] AS (
	SELECT
		[relationship].[branch_id] [BranchID],
		SUM([rln0019].[interest]) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	WHERE [rln0019].[date] = @Prev
	GROUP BY [relationship].[branch_id]
)

, [TodayValueByBranch] AS (
	SELECT
		[relationship].[branch_id] [BranchID],
		SUM([rln0019].[interest]) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	WHERE [rln0019].[date] = @Date
	GROUP BY [relationship].[branch_id]
)

, [result] AS (
	SELECT
		[BranchTarget].[BranchID]
		, ISNULL([TodayValueByBranch].[InterestIncome],0) [InterestIncome]
		, ISNULL([TodayValueByBranch].[InterestIncome],0) - ISNULL([PrevValueByBranch].[InterestIncome],0) [AbsoluteChange]
		, CASE 
			WHEN ISNULL([PrevValueByBranch].[InterestIncome],0) = 0 THEN 0
			ELSE ISNULL([TodayValueByBranch].[InterestIncome],0) / [PrevValueByBranch].[InterestIncome] - 1
		END [RelativeChange]
	FROM [BranchTarget]
	LEFT JOIN [PrevValueByBranch]
		ON [BranchTarget].[BranchID] = [PrevValueByBranch].[BranchID]
	LEFT JOIN [TodayValueByBranch]
		ON [BranchTarget].[BranchID] = [TodayValueByBranch].[BranchID]
)

SELECT
	SUM([InterestIncome]) [InterestIncome],
	SUM([AbsoluteChange]) [AbsoluteChange],
	SUM([RelativeChange]) [RelativeChange]
FROM [result]


END