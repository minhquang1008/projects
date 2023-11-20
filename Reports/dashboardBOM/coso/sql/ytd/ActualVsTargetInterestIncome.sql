﻿/*YTD*/

/*Actual vs Target - Interest Income (Lãi vay ký quỹ - Thực tế và chỉ tiêu)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

WITH

[BranchTarget] AS (
    SELECT 
        [BranchID] 
        , CAST([Target] AS DECIMAL(20,2)) [InterestIncome]
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
    WHERE [rln0019].[date] BETWEEN @FirstDateOfYear AND @Date
    GROUP BY [relationship].[branch_id]
)

SELECT 
	[BranchTarget].[BranchID]
	, SUM(ISNULL([BranchActual].[InterestIncome],0)) [Actual]
    , SUM([BranchTarget].[InterestIncome]) [Target]
FROM [BranchTarget]
LEFT JOIN [BranchActual]
    ON [BranchTarget].[BranchID] = [BranchActual].[BranchID]
GROUP BY [BranchTarget].[BranchID]


END
