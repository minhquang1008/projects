/*YTD*/

/*Total branches - Interest Income*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

WITH

[Branch] AS (
    SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'Interest Income'
        AND [Year] = YEAR(@Date)
)

, [ValueTotalBranches] AS (
	SELECT 
		[relationship].[branch_id] [BranchID]
		, SUM([rln0019].[interest]) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [rln0019].[date] = [relationship].[date]
		AND [rln0019].[sub_account] = [relationship].[sub_account]
	WHERE [rln0019].[date] BETWEEN @FirstDateOfYear AND @Date
	GROUP BY [relationship].[branch_id]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [InterestIncome]
		, CASE [InterestIncome] 
			WHEN 0 THEN 0
			ELSE [InterestIncome] / (SELECT SUM([InterestIncome]) FROM [ValueTotalBranches])
		END [Contribution]
	FROM [ValueTotalBranches]
)

SELECT	
	[Branch].[BranchID],
	ISNULL([InterestIncome], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]


END