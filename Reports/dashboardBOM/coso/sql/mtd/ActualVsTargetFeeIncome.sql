/*MTD*/

/*Actual vs Target - Fee Income (Phí giao dịch - Thực tế và chỉ tiêu) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

WITH

[BranchTarget] AS (
    SELECT 
        [BranchID] 
        , CAST([Target] / 12 AS DECIMAL(15,2)) [FeeIncome]
    FROM [BranchTargetByYear] 
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Fee Income'
)

, [BranchActual] AS (
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

SELECT
	[BranchTarget].[BranchID]
	, SUM(ISNULL([BranchActual].[FeeIncome],0)) [Actual]
    , SUM([BranchTarget].[FeeIncome]) [Target]
FROM [BranchTarget]
LEFT JOIN [BranchActual]
    ON [BranchTarget].[BranchID] = [BranchActual].[BranchID]
GROUP BY [BranchTarget].[BranchID]


END
