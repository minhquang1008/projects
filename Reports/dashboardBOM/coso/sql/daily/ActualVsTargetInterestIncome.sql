/*Daily*/

/*Actual vs Target - Interest Income (Lãi vay ký quỹ - Thực tế và chỉ tiêu)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @WorkDaysOfYear INT;
SET @WorkDaysOfYear = (
	SELECT COUNT(*) 
	FROM [Date] 
	WHERE [Work] = 1 
		AND YEAR([Date]) = YEAR(@Date)
);

WITH

[BranchTarget] AS (
    SELECT 
        [BranchID] 
        , CAST([Target] / @WorkDaysOfYear AS DECIMAL(15,2)) [InterestIncome]
    FROM [BranchTargetByYear] 
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Interest Income'
)

, [BranchActual] AS (
    SELECT 
        [relationship].[branch_id] [BranchID]
        , SUM([rln0019].[interest]) [InterestIncome]
    FROM [rln0019]
    LEFT JOIN [relationship]
        ON [rln0019].[date] = [relationship].[date]
        AND [rln0019].[sub_account] = [relationship].[sub_account]
    WHERE [rln0019].[date] = @Date
    GROUP BY [relationship].[branch_id]
)

SELECT
	[BranchTarget].[BranchID]
	, ISNULL([BranchActual].[InterestIncome],0) [Actual]
    , [BranchTarget].[InterestIncome] [Target]
FROM [BranchTarget]
LEFT JOIN [BranchActual]
    ON [BranchTarget].[BranchID] = [BranchActual].[BranchID]

END
