/*Daily*/

/*Headline Tag - Fee Income (Phần trăm hoàn thành chỉ tiêu ngày - Phí giao dịch) */

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
		AND [Measure] = 'Fee Income'
)

, [PrevValueByBranch] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Prev
	GROUP BY [relationship].[branch_id]
)

, [TodayValueByBranch] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Date
	GROUP BY [relationship].[branch_id]
)

, [result] AS (
	SELECT
		[BranchTarget].[BranchID]
		, ISNULL([TodayValueByBranch].[FeeInCome],0) [FeeIncome]
		, ISNULL([TodayValueByBranch].[FeeInCome],0) - ISNULL([PrevValueByBranch].[FeeInCome],0) [AbsoluteChange]
		, CASE 
			WHEN ISNULL([PrevValueByBranch].[FeeInCome],0) = 0 THEN 0
			ELSE ISNULL([TodayValueByBranch].[FeeInCome],0) / [PrevValueByBranch].[FeeInCome] - 1
		END [RelativeChange]
	FROM [BranchTarget]
	LEFT JOIN [PrevValueByBranch]
		ON [BranchTarget].[BranchID] = [PrevValueByBranch].[BranchID]
	LEFT JOIN [TodayValueByBranch]
		ON [BranchTarget].[BranchID] = [TodayValueByBranch].[BranchID]
)

SELECT
	SUM([FeeIncome]) [FeeIncome]
	, SUM([AbsoluteChange]) [AbsoluteChange]
	, SUM([RelativeChange]) [RelativeChange]
FROM [result]


END
