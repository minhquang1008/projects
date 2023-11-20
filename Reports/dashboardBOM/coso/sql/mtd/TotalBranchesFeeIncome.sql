/*MTD*/

/*Total branches - Fee Income*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

WITH

[Branch] AS (
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
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonth AND @Date
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
	[Branch].[BranchID]
	, ISNULL([FeeIncome], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]


END